import os
import sys

html_path = r'C:\Users\GreenFest\.gemini\antigravity\scratch\magicdns\index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

assert 'id="ai-services-grid"' in html, "ai-services-grid missing"
for svc in ['claude', 'gemini', 'chatgpt', 'perplexity', 'aistudio']:
    assert f'id="probe-card-{svc}"' in html, f"probe-card-{svc} missing"
    assert f'id="probe-badge-{svc}"' in html, f"probe-badge-{svc} missing"

assert 'probeEndpoint' in html, "probeEndpoint missing"
assert 'AI_SERVICES_LIST' in html, "AI_SERVICES_LIST missing"
assert 'metric-gateway-status' in html, "metric-gateway-status missing"
assert 'metric-access-status' in html, "metric-access-status missing"
assert 'ai-services-probe-grid' in html, "ai-services-probe-grid class missing"

print("AI PROBE ASSERTIONS: ALL PASSED!")
