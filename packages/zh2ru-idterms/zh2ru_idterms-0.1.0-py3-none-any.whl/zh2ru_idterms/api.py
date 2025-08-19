# src/zh2ru_idterms/api.py
# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import sqlite3
import threading
from pathlib import Path
from typing import Optional, Dict, Any, List
import importlib.resources as resources

import zh2ru_idterms  # 包自身，用于定位随包数据

# =========================
# 内部连接与路径解析
# =========================
_DB_LOCK = threading.RLock()
_CONN: Optional[sqlite3.Connection] = None
_DB_PATH_OVERRIDE: Optional[str] = None  # 用户可外部指定


def set_db_path(path: str) -> None:
    """
    可选：显式指定外部 terms.db 的路径（会重置连接）。
    """
    global _DB_PATH_OVERRIDE, _CONN
    with _DB_LOCK:
        _DB_PATH_OVERRIDE = path
        if _CONN is not None:
            try:
                _CONN.close()
            finally:
                _CONN = None


def _candidate_paths() -> List[Path]:
    cands: List[Path] = []

    # 1) 外部设置
    if _DB_PATH_OVERRIDE:
        cands.append(Path(_DB_PATH_OVERRIDE))

    # 2) 环境变量
    env_p = os.getenv("ZH2RU_TERMS_DB")
    if env_p:
        cands.append(Path(env_p))

    # 3) 包内资源（安装后）
    try:
        p = resources.files(zh2ru_idterms) / "data" / "terms.db"
        cands.append(Path(str(p)))
    except Exception:
        pass

    # 4) 源码相对路径（开发/编辑安装）
    cands.append(Path(__file__).parent / "data" / "terms.db")

    # 去重，保序
    seen = set()
    uniq: List[Path] = []
    for p in cands:
        sp = str(p)
        if sp not in seen:
            seen.add(sp)
            uniq.append(p)
    return uniq


def _resolve_db_path() -> str:
    for p in _candidate_paths():
        if p.exists() and p.is_file():
            return str(p)
    raise FileNotFoundError(
        "terms.db 未找到。\n"
        "请检查：\n"
        "  1) 是否已将数据库放在 src/zh2ru_idterms/data/terms.db；\n"
        "  2) 若使用可编辑安装(pip install -e .)，确保该文件真实存在于源码目录；\n"
        "  3) pyproject.toml 中包含数据文件：\n"
        "     [tool.setuptools.package-data]\n"
        "     zh2ru_idterms = [\"data/terms.db\"]\n"
        "  4) 或通过 set_db_path('/path/to/terms.db') / 环境变量 ZH2RU_TERMS_DB 指定。\n"
    )


def _get_conn() -> sqlite3.Connection:
    global _CONN
    if _CONN is not None:
        return _CONN
    with _DB_LOCK:
        if _CONN is None:
            db_path = _resolve_db_path()
            conn = sqlite3.connect(db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            _CONN = conn
    return _CONN


def close() -> None:
    """关闭内部连接（通常不需要）"""
    global _CONN
    with _DB_LOCK:
        if _CONN is not None:
            try:
                _CONN.close()
            finally:
                _CONN = None


# =========================
# 工具
# =========================
def _norm(s: Optional[str]) -> Optional[str]:
    if s is None:
        return None
    s = str(s).strip()
    return s or None


# =========================
# 地理查询
# =========================
def get_place_path(
        province_zh: Optional[str] = None,
        city_zh: Optional[str] = None,
        district_zh: Optional[str] = None
) -> Dict[str, Optional[str]]:
    """
    返回 {province, city, district} 的俄文名称（缺项返回 None）
    """
    conn = _get_conn()
    res = {"province": None, "city": None, "district": None}

    if province_zh:
        row = conn.execute(
            "SELECT name_ru FROM geo_province WHERE name_zh=?", (province_zh,)
        ).fetchone()
        res["province"] = row["name_ru"] if row else None

    if province_zh and city_zh:
        row = conn.execute(
            """
            SELECT c.name_ru AS ru
            FROM geo_city c
            JOIN geo_province p ON p.id=c.province_id
            WHERE p.name_zh=? AND c.name_zh=?
            """,
            (province_zh, city_zh),
        ).fetchone()
        res["city"] = row["ru"] if row else None

    if province_zh and city_zh and district_zh:
        row = conn.execute(
            """
            SELECT d.name_ru AS ru
            FROM geo_district d
            JOIN geo_city c ON c.id=d.city_id
            JOIN geo_province p ON p.id=c.province_id
            WHERE p.name_zh=? AND c.name_zh=? AND d.name_zh=?
            """,
            (province_zh, city_zh, district_zh),
        ).fetchone()
        res["district"] = row["ru"] if row else None

    return res


# =========================
# 姓氏
# =========================
def find_surname_pinyin(pinyin: str) -> Optional[str]:
    py = _norm(pinyin.lower())
    if not py:
        return None
    conn = _get_conn()
    row = conn.execute(
        "SELECT ru_map FROM surname_pinyin_rule WHERE pinyin=?", (py,)
    ).fetchone()
    return row["ru_map"] if row else None


# =========================
# 给名（音节规则）
# =========================
def _load_given_rules() -> Dict[str, str]:
    conn = _get_conn()
    rows = conn.execute(
        "SELECT pattern, ru_map FROM givenname_rule ORDER BY LENGTH(pattern) DESC, priority ASC"
    ).fetchall()
    return {r["pattern"].lower(): r["ru_map"] for r in rows}


_GIVEN_RULES_CACHE: Optional[Dict[str, str]] = None


def to_palladius_given(pinyin: str) -> str:
    """
    将给名拼音（不带空格的连写，例如 xiaoming）按音节映射为俄文并拼接（最长优先）。
    """
    global _GIVEN_RULES_CACHE
    text = (_norm(pinyin) or "").lower()
    if not text:
        return ""
    if _GIVEN_RULES_CACHE is None:
        with _DB_LOCK:
            if _GIVEN_RULES_CACHE is None:
                _GIVEN_RULES_CACHE = _load_given_rules()
    rules = _GIVEN_RULES_CACHE

    i = 0
    out: List[str] = []
    max_len = max((len(k) for k in rules.keys()), default=0)

    while i < len(text):
        for L in range(min(max_len, len(text) - i), 0, -1):
            seg = text[i:i + L]
            ru = rules.get(seg)
            if ru is not None:
                out.append(ru)
                i += L
                break
        else:
            out.append(text[i])
            i += 1
    return "".join(out)


# =========================
# 机构（护照/驾照）
# =========================
def find_org(
        name_zh: str,
        doc_type: str = "passport",
        region_zh: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    机构名翻译；精确匹配 name_zh，region_zh 可选；doc_type: passport | driving_licence
    """
    dt = doc_type if doc_type in ("passport", "driving_licence") else "passport"
    n = _norm(name_zh)
    r = _norm(region_zh)
    if not n:
        return None
    conn = _get_conn()

    if r is None:
        row = conn.execute(
            """
            SELECT name_zh, name_ru, doc_type, region_zh
            FROM authority_org
            WHERE doc_type=? AND name_zh=? AND region_zh IS NULL
            """,
            (dt, n),
        ).fetchone()
        if not row:
            row = conn.execute(
                """
                SELECT name_zh, name_ru, doc_type, region_zh
                FROM authority_org
                WHERE doc_type=? AND name_zh=?
                ORDER BY region_zh IS NOT NULL
                LIMIT 1
                """,
                (dt, n),
            ).fetchone()
    else:
        row = conn.execute(
            """
            SELECT name_zh, name_ru, doc_type, region_zh
            FROM authority_org
            WHERE doc_type=? AND name_zh=? AND region_zh=?
            """,
            (dt, n, r),
        ).fetchone()

    return dict(row) if row else None


# =========================
# 人名组合
# =========================
def translate_person_name(surname_pinyin: str, given_pinyin: str) -> str:
    sur_ru = find_surname_pinyin(surname_pinyin) or surname_pinyin
    giv_ru = to_palladius_given(given_pinyin) or given_pinyin
    return f"{sur_ru.capitalize()} {giv_ru}"
