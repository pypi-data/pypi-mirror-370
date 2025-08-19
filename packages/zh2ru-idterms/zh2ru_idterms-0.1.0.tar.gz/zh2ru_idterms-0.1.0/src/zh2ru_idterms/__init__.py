# src/zh2ru_idterms/__init__.py
# -*- coding: utf-8 -*-

from .api import (
    get_place_path,
    find_surname_pinyin,
    to_palladius_given,
    translate_person_name,
    find_org,
    close,
)

__all__ = [
    "get_place_path",
    "find_surname_pinyin",
    "to_palladius_given",
    "translate_person_name",
    "find_org",
    "close",
]