import unittest
import os
import json
import time
import xml.etree.ElementTree as ET
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
        statuses_all_ok = {
            'se': {'status': 'ok'},
            'de': {'status': 'ok'}
        }
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
        self.assertIn("admin_dig_info", callbacks)

        srv_kb = support_bot.get_admin_servers_kb()
        srv_callbacks = [btn['callback_data'] for row in srv_kb['inline_keyboard'] for btn in row if 'callback_data' in btn]
        self.assertIn("admin_test_ai", srv_callbacks)

    def test_generate_mobileconfig_variants(self):
        self.assertTrue(hasattr(support_bot, 'generate_mobileconfig'))
        for v in ['dual', 'se', 'de']:
            raw = support_bot.generate_mobileconfig(v)
            self.assertIsInstance(raw, bytes)
            xml_str = raw.decode('utf-8')
            root = ET.fromstring(xml_str)
            self.assertEqual(root.tag, 'plist')
            if v == 'se':
                self.assertIn('109.120.132.43', xml_str)
                self.assertNotIn('94.249.177.102', xml_str)
            elif v == 'de':
                self.assertIn('94.249.177.102', xml_str)
                self.assertNotIn('109.120.132.43', xml_str)
            else:
                self.assertIn('109.120.132.43', xml_str)
                self.assertIn('94.249.177.102', xml_str)

    def test_run_dig_diagnostics(self):
        self.assertTrue(hasattr(support_bot, 'run_dig_diagnostics'))
        # Valid domain
        rep, clean_dom = support_bot.run_dig_diagnostics("https://claude.ai/login")
        self.assertEqual(clean_dom, "claude.ai")
        self.assertIn("DNS-диагностика домена", rep)
        self.assertIn("claude.ai", rep)

        # Invalid domain
        err_rep, err_dom = support_bot.run_dig_diagnostics("invalid..domain!!!")
        self.assertIsNone(err_dom)
        self.assertIn("Некорректный домен", err_rep)

    def test_ios_picker_keyboards(self):
        self.assertTrue(hasattr(support_bot, 'get_ios_picker_kb'))
        kb = support_bot.get_ios_picker_kb()
        callbacks = [btn['callback_data'] for row in kb['inline_keyboard'] for btn in row if 'callback_data' in btn]
        self.assertIn("dl_ios_dual", callbacks)
        self.assertIn("dl_ios_se", callbacks)
        self.assertIn("dl_ios_de", callbacks)

    def test_feedback_api_wishlist_and_vote(self):
        import io
        from unittest.mock import patch, MagicMock

        messages_sent = []
        def mock_send(chat_id, text, reply_markup=None):
            messages_sent.append((chat_id, text, reply_markup))

        with patch.object(support_bot, 'send_message', side_effect=mock_send):
            # 1. Wishlist vote
            vote_body = json.dumps({'type': 'vote', 'service_id': 'konami'}).encode('utf-8')
            h1 = support_bot.FeedbackAPIHandler.__new__(support_bot.FeedbackAPIHandler)
            h1.path = '/api/feedback'
            h1.headers = {'Content-Length': str(len(vote_body))}
            h1.rfile = io.BytesIO(vote_body)
            h1.wfile = io.BytesIO()
            h1.send_response = MagicMock()
            h1.send_header = MagicMock()
            h1.end_headers = MagicMock()
            h1.do_POST()
            h1.send_response.assert_called_with(200)
            resp = json.loads(h1.wfile.getvalue().decode('utf-8'))
            self.assertTrue(resp.get('ok'))
            self.assertEqual(resp.get('message'), 'Голос принят')
            self.assertEqual(len(messages_sent), 0)

            # 2. Wishlist proposal
            wishlist_body = json.dumps({
                'type': 'wishlist',
                'service_title': 'EA FC 25',
                'category': 'Игра',
                'domain': 'ea.com',
                'message': 'Ошибка авторизации EA Play',
                'contact': '@gamer123'
            }).encode('utf-8')
            h2 = support_bot.FeedbackAPIHandler.__new__(support_bot.FeedbackAPIHandler)
            h2.path = '/api/feedback'
            h2.headers = {'Content-Length': str(len(wishlist_body))}
            h2.rfile = io.BytesIO(wishlist_body)
            h2.wfile = io.BytesIO()
            h2.send_response = MagicMock()
            h2.send_header = MagicMock()
            h2.end_headers = MagicMock()
            h2.do_POST()
            h2.send_response.assert_called_with(200)
            self.assertEqual(len(messages_sent), 1)
            _, text2, _ = messages_sent[0]
            self.assertIn('#ВИШЛИСТ', text2)
            self.assertIn('EA FC 25', text2)
            self.assertIn('ea.com', text2)
            self.assertIn('@gamer123', text2)
            self.assertIn('149-ФЗ', text2)

            # 3. Idea (distinct from wishlist)
            idea_body = json.dumps({
                'type': 'idea',
                'name': 'Иван',
                'platform': 'iOS',
                'message': 'Добавьте поддержку DoH3 на роутерах',
                'contact': '@ivan'
            }).encode('utf-8')
            h3 = support_bot.FeedbackAPIHandler.__new__(support_bot.FeedbackAPIHandler)
            h3.path = '/api/feedback'
            h3.headers = {'Content-Length': str(len(idea_body))}
            h3.rfile = io.BytesIO(idea_body)
            h3.wfile = io.BytesIO()
            h3.send_response = MagicMock()
            h3.send_header = MagicMock()
            h3.end_headers = MagicMock()
            h3.do_POST()
            h3.send_response.assert_called_with(200)
            self.assertEqual(len(messages_sent), 2)
            _, text3, _ = messages_sent[1]
            self.assertIn('#ИДЕЯ', text3)
            self.assertNotIn('#ВИШЛИСТ', text3)
            self.assertIn('DoH3', text3)

            # 4. Bug report
            bug_body = json.dumps({
                'type': 'bug',
                'platform': 'Windows',
                'message': 'Кнопка не нажимается в Firefox',
                'contact': '@tester'
            }).encode('utf-8')
            h4 = support_bot.FeedbackAPIHandler.__new__(support_bot.FeedbackAPIHandler)
            h4.path = '/api/feedback'
            h4.headers = {'Content-Length': str(len(bug_body))}
            h4.rfile = io.BytesIO(bug_body)
            h4.wfile = io.BytesIO()
            h4.send_response = MagicMock()
            h4.send_header = MagicMock()
            h4.end_headers = MagicMock()
            h4.do_POST()
            h4.send_response.assert_called_with(200)
            self.assertEqual(len(messages_sent), 3)
            _, text4, _ = messages_sent[2]
            self.assertIn('#БАГ', text4)
            self.assertNotIn('#ВИШЛИСТ', text4)

if __name__ == '__main__':
    unittest.main()
