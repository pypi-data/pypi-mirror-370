RULES = [
    ("zh", "чж"), ("ch", "ч"), ("sh", "ш"), ("ng", "н"),
    ("a", "а"), ("ai", "ай"), ("an", "ань"), ("ang", "ан"), ("ao", "ао"),
    ("e", "э"), ("ei", "эй"), ("en", "энь"), ("eng", "эн"), ("er", "эр"),
    ("i", "и"), ("ia", "я"), ("ian", "янь"), ("iang", "ян"), ("iao", "яо"),
    ("ie", "е"), ("in", "инь"), ("ing", "ин"), ("iong", "юн"), ("iu", "ю"),
    ("o", "о"), ("ong", "ун"), ("ou", "оу"),
    ("u", "у"), ("ua", "уа"), ("uan", "уань"), ("uang", "уан"), ("ui", "уй"),
    ("un", "унь"), ("uo", "о"),
    ("ü", "ю"), ("üe", "юэ"), ("üan", "юань"), ("ün", "юнь"),
]


def to_palladius_given(pinyin: str) -> str:
    s = pinyin.lower()
    for pat, rep in sorted(RULES, key=lambda x: -len(x[0])):
        s = s.replace(pat, rep)
    return s
