# -*- coding: utf-8 -*-
from i18n_data import i18n

# Verify key parity across languages
ru_keys = set(i18n["ru"].keys())
for lang in ["en", "zh", "tr"]:
    lang_keys = set(i18n[lang].keys())
    missing = ru_keys - lang_keys
    extra = lang_keys - ru_keys
    assert not missing, f"Missing keys in {lang}: {missing}"
    assert not extra, f"Extra keys in {lang}: {extra}"

print("All keys match perfectly across RU, EN, ZH, TR! Total keys per language:", len(ru_keys))
