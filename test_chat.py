import re
import os
import subprocess

html = open('index.html', encoding='utf-8').read()

tests = []
def test(name, condition, details=""):
    tests.append((name, condition, details))

# 1. HTML Element presence
test("Chat FAB button exists", 'id="chat-fab"' in html)
test("Chat FAB has aria-label", 'aria-label="Открыть чат поддержки MagicDNS"' in html)
test("Chat Window dialog exists", 'id="chat-window"' in html)
test("Chat Window has role dialog", 'role="dialog"' in html)
test("Chat close button exists", 'id="chat-close-btn"' in html)
test("Chat messages container exists", 'id="chat-messages"' in html)
test("Chat input exists", 'id="chat-input"' in html)
test("Chat send button exists", 'id="chat-send-btn"' in html)

# 2. FAQ Chips
faq_keys = ['router', 'security', 'ios', 'disable', 'diff']
for key in faq_keys:
    test(f"FAQ chip data-faq='{key}' present", f'data-faq="{key}"' in html)

# 3. Cloudflare Worker files
worker_path = os.path.join('cloudflare-worker', 'worker.js')
wrangler_path = os.path.join('cloudflare-worker', 'wrangler.toml')
readme_path = os.path.join('cloudflare-worker', 'README.md')

test("cloudflare-worker/worker.js exists", os.path.exists(worker_path))
test("cloudflare-worker/wrangler.toml exists", os.path.exists(wrangler_path))
test("cloudflare-worker/README.md exists", os.path.exists(readme_path))

if os.path.exists(worker_path):
    worker_js = open(worker_path, encoding='utf-8').read()
    test("Worker handles OPTIONS CORS preflight", "request.method === 'OPTIONS'" in worker_js)
    test("Worker checks GEMINI_API_KEY", "env.GEMINI_API_KEY" in worker_js)
    test("Worker queries Gemini Flash endpoint", "generativelanguage.googleapis.com" in worker_js and "gemini-1.5-flash" in worker_js)
    test("Worker contains Swedish IP 109.120.132.43", "109.120.132.43" in worker_js)
    test("Worker contains DoH URL https://dns.magicdns.ru/dns-query", "https://dns.magicdns.ru/dns-query" in worker_js)

    # Check worker syntax with Node.js
    res = subprocess.run(['node', '--check', worker_path], capture_output=True, text=True)
    test("cloudflare-worker/worker.js syntax is 100% valid in Node.js", res.returncode == 0, res.stderr.strip())

# 4. Client Script Logic
test("Client script contains CF_WORKER_URL", "CF_WORKER_URL" in html)
test("Client script contains faqAnswers", "faqAnswers" in html)
test("Client script contains findLocalMatch fallback", "findLocalMatch" in html)

print("\n" + "="*50)
print("CHAT & CLOUDFLARE WORKER VERIFICATION RESULTS")
print("="*50)
all_passed = True
for name, passed, details in tests:
    status = "PASS" if passed else "FAIL"
    detail_str = f" ({details})" if details else ""
    print(f"[{status}] {name}{detail_str}")
    if not passed:
        all_passed = False

print(f"\nFINAL STATUS: {'ALL CHAT TESTS PASSED!' if all_passed else 'SOME CHAT TESTS FAILED!'}")
if not all_passed:
    exit(1)
