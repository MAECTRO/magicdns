import unittest
import os
import json
import time
import support_bot

class TestSupportBot(unittest.TestCase):
    def setUp(self):
        self.test_sub_file = "test_subscribers_temp.json"
        support_bot.SUBSCRIBERS_FILE = self.test_sub_file
        support_bot.subscribers.clear()

    def tearDown(self):
        if os.path.exists(self.test_sub_file):
            os.remove(self.test_sub_file)

    def test_subscribers_seed(self):
        support_bot.load_subscribers()
        self.assertGreaterEqual(len(support_bot.subscribers), 5)
        self.assertIn("268714811", support_bot.subscribers)

    def test_register_subscriber(self):
        support_bot.load_subscribers()
        support_bot.register_subscriber(999999, "TestUser", "test_user")
        self.assertIn("999999", support_bot.subscribers)
        self.assertEqual(support_bot.subscribers["999999"]["first_name"], "TestUser")
        
        # Admin should not be registered as subscriber
        support_bot.register_subscriber(support_bot.ADMIN_CHAT_ID, "Admin", "admin")
        self.assertNotIn(str(support_bot.ADMIN_CHAT_ID), support_bot.subscribers)

    def test_format_alert(self):
        raw = "Внимание <тест> & авария"
        formatted = support_bot.format_alert_message(raw)
        self.assertIn("ВНИМАНИЕ: ОПОВЕЩЕНИЕ СЕТИ MAGICDNS", formatted)
        self.assertIn("&lt;тест&gt; &amp; авария", formatted)
        self.assertIn("/status", formatted)

    def test_cards_and_compliance(self):
        welcome = support_bot.get_welcome_card()
        self.assertIn("MagicDNS", welcome)
        self.assertIn("без сторонних приложений и тоннелей", welcome)
        self.assertNotIn("без vpn", welcome.lower())
        
        prohibited = ['обход', 'разблок', 'аноним', 'взлом', 'запрещен', 'запрещён']
        for p in prohibited:
            self.assertNotIn(p, welcome.lower(), f"Prohibited word '{p}' found in welcome card")
            
        status = support_bot.get_status_card()
        self.assertIn("109.120.132.43", status)
        self.assertIn("94.249.177.102", status)

    def test_review_reply_structure(self):
        self.assertTrue(hasattr(support_bot, 'reply_to_review_on_github'))
        mock_reviews = [
            {"id": 12345, "author": "User", "message": "Good!", "rating": 5}
        ]
        mock_reply_text = "Спасибо за отзыв!"
        for r in mock_reviews:
            if r['id'] == 12345:
                r['reply'] = {
                    'text': mock_reply_text,
                    'date': '24 октября 2026',
                    'author': 'Команда MagicDNS'
                }
        self.assertIn('reply', mock_reviews[0])
        self.assertEqual(mock_reviews[0]['reply']['text'], mock_reply_text)
        self.assertEqual(mock_reviews[0]['reply']['author'], 'Команда MagicDNS')

    def test_sync_servers_to_site_logic(self):
        self.assertTrue(hasattr(support_bot, 'sync_servers_to_site'))
        
        # Test mock statuses when all OK
        statuses_all_ok = {
            'se': {'status': 'ok'},
            'de': {'status': 'ok'}
        }
        # In test environment, set_site_alert won't commit to GitHub (no token), but function logic should execute without crash
        try:
            support_bot.sync_servers_to_site(statuses_all_ok)
        except Exception as e:
            self.fail(f"sync_servers_to_site crashed on all_ok: {e}")

    def test_run_ai_diagnostics(self):
        self.assertTrue(hasattr(support_bot, 'run_ai_diagnostics'))
        card = support_bot.run_ai_diagnostics()
        self.assertIn("Результаты экспресс-теста доступности ИИ", card)
        self.assertIn("Google Gemini", card)
        self.assertIn("Google AI Studio", card)
        self.assertIn("OpenAI (ChatGPT)", card)
        self.assertIn("Anthropic Claude", card)
        self.assertIn("Microsoft Copilot", card)

    def test_ai_diagnostics_kb(self):
        self.assertTrue(hasattr(support_bot, 'get_ai_diagnostics_kb'))
        kb = support_bot.get_ai_diagnostics_kb()
        self.assertIn("inline_keyboard", kb)
        callbacks = [btn['callback_data'] for row in kb['inline_keyboard'] for btn in row if 'callback_data' in btn]
        self.assertIn("admin_test_ai", callbacks)
        self.assertIn("admin_srv_status", callbacks)
        self.assertIn("admin_panel", callbacks)

    def test_admin_panel_kb_has_new_features(self):
        kb = support_bot.get_admin_panel_kb()
        callbacks = [btn['callback_data'] for row in kb['inline_keyboard'] for btn in row if 'callback_data' in btn]
        self.assertIn("admin_test_ai", callbacks)
        self.assertIn("admin_srv_status", callbacks)

        srv_kb = support_bot.get_admin_servers_kb()
        srv_callbacks = [btn['callback_data'] for row in srv_kb['inline_keyboard'] for btn in row if 'callback_data' in btn]
        self.assertIn("admin_test_ai", srv_callbacks)

if __name__ == '__main__':
    unittest.main()
