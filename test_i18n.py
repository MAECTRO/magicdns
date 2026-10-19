# -*- coding: utf-8 -*-
from i18n_data import i18n, faq_answers

# Verify key parity across languages in i18n dictionary
ru_keys = set(i18n["ru"].keys())
for lang in ["en", "zh", "tr"]:
    lang_keys = set(i18n[lang].keys())
    missing = ru_keys - lang_keys
    extra = lang_keys - ru_keys
    assert not missing, f"Missing keys in {lang}: {missing}"
    assert not extra, f"Extra keys in {lang}: {extra}"

# Verify key parity across languages in faq_answers
ru_faq_keys = set(faq_answers["ru"].keys())
for lang in ["en", "zh", "tr"]:
    assert lang in faq_answers, f"Missing language {lang} in faq_answers"
    lang_faq_keys = set(faq_answers[lang].keys())
    missing = ru_faq_keys - lang_faq_keys
    extra = lang_faq_keys - ru_faq_keys
    assert not missing, f"Missing FAQ keys in {lang}: {missing}"
    assert not extra, f"Extra FAQ keys in {lang}: {extra}"

print("All keys match perfectly across RU, EN, ZH, TR! Total keys per language:", len(ru_keys))
print("All FAQ answers match perfectly across RU, EN, ZH, TR! Total FAQ keys per language:", len(ru_faq_keys))

