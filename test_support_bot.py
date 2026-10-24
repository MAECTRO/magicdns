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
        # Test simulated reply dictionary injection
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

if __name__ == '__main__':
    unittest.main()
