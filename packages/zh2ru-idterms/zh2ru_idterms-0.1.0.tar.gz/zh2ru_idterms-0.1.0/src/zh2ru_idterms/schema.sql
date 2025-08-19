PRAGMA foreign_keys = ON;

-- 地理
CREATE TABLE IF NOT EXISTS geo_province (
  id INTEGER PRIMARY KEY,
  name_zh TEXT NOT NULL UNIQUE,
  name_ru TEXT,
  aliases_zh TEXT DEFAULT '[]',
  aliases_ru TEXT DEFAULT '[]',
  meta TEXT DEFAULT '{}',
  updated_at TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS geo_city (
  id INTEGER PRIMARY KEY,
  province_id INTEGER NOT NULL REFERENCES geo_province(id) ON DELETE CASCADE,
  name_zh TEXT NOT NULL,
  name_ru TEXT,
  aliases_zh TEXT DEFAULT '[]',
  aliases_ru TEXT DEFAULT '[]',
  meta TEXT DEFAULT '{}',
  updated_at TEXT DEFAULT (datetime('now')),
  UNIQUE (province_id, name_zh)
);
CREATE TABLE IF NOT EXISTS geo_district (
  id INTEGER PRIMARY KEY,
  city_id INTEGER NOT NULL REFERENCES geo_city(id) ON DELETE CASCADE,
  name_zh TEXT NOT NULL,
  name_ru TEXT,
  aliases_zh TEXT DEFAULT '[]',
  aliases_ru TEXT DEFAULT '[]',
  meta TEXT DEFAULT '{}',
  updated_at TEXT DEFAULT (datetime('now')),
  UNIQUE (city_id, name_zh)
);
-- 姓氏：拼音→俄文
CREATE TABLE IF NOT EXISTS surname_pinyin_rule (
    id INTEGER PRIMARY KEY,
    pinyin TEXT NOT NULL UNIQUE,
    ru_map TEXT NOT NULL,
    priority INTEGER DEFAULT 10,
    meta TEXT DEFAULT '{}'
);
-- 姓名
CREATE TABLE IF NOT EXISTS surname_rule (
  id INTEGER PRIMARY KEY,
  hanzi TEXT NOT NULL UNIQUE,
  ru_pref TEXT NOT NULL,
  ru_aliases TEXT DEFAULT '[]',
  meta TEXT DEFAULT '{}'
);
CREATE TABLE IF NOT EXISTS givenname_rule (
  id INTEGER PRIMARY KEY,
  pattern TEXT NOT NULL,
  ru_map TEXT NOT NULL,
  priority INTEGER DEFAULT 100,
  meta TEXT DEFAULT '{}'
);
CREATE TABLE IF NOT EXISTS name_exception (
  id INTEGER PRIMARY KEY,
  name_zh TEXT NOT NULL UNIQUE,
  name_ru TEXT NOT NULL,
  meta TEXT DEFAULT '{}'
);

-- 机构
CREATE TABLE IF NOT EXISTS authority_org (
  id INTEGER PRIMARY KEY,
  doc_type TEXT NOT NULL CHECK (doc_type IN ('passport','driving_licence')),
  name_zh TEXT NOT NULL,
  name_ru TEXT,
  region_zh TEXT,
  parent_org_id INTEGER REFERENCES authority_org(id) ON DELETE SET NULL,
  aliases_zh TEXT DEFAULT '[]',
  aliases_ru TEXT DEFAULT '[]',
  meta TEXT DEFAULT '{}',
  updated_at TEXT DEFAULT (datetime('now'))
);
CREATE UNIQUE INDEX IF NOT EXISTS u_authority_org
    ON authority_org (doc_type, name_zh, IFNULL(region_zh,''));


