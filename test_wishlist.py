# -*- coding: utf-8 -*-
"""
Verification suite for Community Wishlist & Service Proposal feature.
"""
import os
import sys
import json
import re

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_HTML = os.path.join(BASE_DIR, 'index.html')
PUBLIC_INDEX_HTML = os.path.join(BASE_DIR, 'public', 'index.html')
WISHLIST_JSON = os.path.join(BASE_DIR, 'wishlist.json')

def test_wishlist():
    assert os.path.exists(INDEX_HTML), "index.html missing"
    assert os.path.exists(PUBLIC_INDEX_HTML), "public/index.html missing"
    assert os.path.exists(WISHLIST_JSON), "wishlist.json missing"

    # 1. Verify wishlist.json content
    with open(WISHLIST_JSON, 'r', encoding='utf-8') as f:
        w_data = json.load(f)
    assert isinstance(w_data, list), "wishlist.json must be a list"
    assert len(w_data) == 1, f"wishlist.json must contain ONLY Konami, found {len(w_data)} items"
    konami = w_data[0]
    assert konami["id"] == "konami", "First item must be konami"
    assert "Konami" in konami["title"], "Title must contain Konami"
    assert "eFootball" in konami["title"], "Title must contain eFootball"
    assert "Yu-Gi-Oh" in konami["title"], "Title must contain Yu-Gi-Oh"
    assert "В обработке у команды 🟡" in konami["status_text"], "Status text must be 'В обработке у команды 🟡'"

    # 2. Verify index.html content
    with open(INDEX_HTML, 'r', encoding='utf-8') as f:
        html = f.read()

    # Section exists
    assert 'id="wishlist"' in html, "Wishlist section id missing"
    assert 'class="wishlist-section"' in html, "Wishlist section class missing"

    # Only Konami card
    assert 'id="card-konami"' in html, "Konami card missing"
    assert 'Konami (eFootball / PES / Yu-Gi-Oh)' in html, "Konami title missing in card"
    assert 'В обработке у команды 🟡' in html, "Konami status missing"
    assert 'id="vote-btn-konami"' in html, "Konami vote button missing"
    assert 'id="vote-count-konami"' in html, "Konami vote count missing"

    # Action card & button
    assert 'id="wishlist-action-card"' in html, "Wishlist action card missing"
    assert 'id="action-card-suggest-btn"' in html, "Action card suggest button missing"
    assert 'id="open-suggest-btn"' in html, "Header suggest button missing"

    # 4-step process pipeline
    assert 'class="wishlist-pipeline"' in html, "Process pipeline container missing"
    assert 'Ваше предложение' in html, "Step 1 missing"
    assert 'Проверка на РКН' in html, "Step 2 missing"
    assert 'Модерация и тесты' in html, "Step 3 missing"
    assert 'Публикация в вишлист' in html, "Step 4 missing"

    # Suggestion modal & form
    assert 'id="suggest-modal"' in html, "Suggest modal missing"
    assert 'id="suggest-form"' in html, "Suggest form missing"
    assert 'id="suggest-name"' in html, "Suggest name input missing"
    assert 'id="suggest-domain"' in html, "Suggest domain input missing"
    assert 'id="suggest-reason"' in html, "Suggest reason textarea missing"
    assert 'id="suggest-contact"' in html, "Suggest contact input missing"
    assert 'id="suggest-submit-btn"' in html, "Suggest submit button missing"
    assert 'data-suggest-type="game"' in html, "Game type chip missing"
    assert 'data-suggest-type="ai"' in html, "AI type chip missing"
    assert 'data-suggest-type="app"' in html, "App type chip missing"

    # Regulatory compliance: NO forbidden terms anywhere in html
    lower_html = html.lower()
    for forbidden in ['обход', 'разблок', 'взлом', 'аноним', 'запрещен', 'запрещён', 'заблокир']:
        assert forbidden not in lower_html, f"Forbidden term found: {forbidden}"

    # JS handlers present
    assert 'toggleSuggestModal' in html, "toggleSuggestModal function missing in JS"
    assert 'magicdns_voted_wishlist' in html, "localStorage voted wishlist key missing in JS"
    assert 'voteKonamiBtn' in html, "voteKonamiBtn binding missing in JS"

    print("ALL WISHLIST VERIFICATION CHECKS PASSED!")

if __name__ == '__main__':
    test_wishlist()
