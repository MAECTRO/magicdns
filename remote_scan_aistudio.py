import urllib.request
import re
import json

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'}
req = urllib.request.Request('https://aistudio.google.com/', headers=headers)
try:
    with urllib.request.urlopen(req, timeout=10) as r:
        html = r.read().decode('utf-8', errors='ignore')
except Exception as e:
    print("Fetch error:", e)
    exit(1)

scripts = re.findall(r'src="([^"]+)"', html)
all_found = set()
all_found.update(re.findall(r'([a-zA-Z0-9.-]+\.(?:googleapis\.com|clients6\.google\.com|clients\.google\.com|google|gstatic\.com|googleusercontent\.com|goog|withgoogle\.com))', html))

for s in scripts:
    if not s.startswith('http'):
        s = 'https://aistudio.google.com' + s
    try:
        req_s = urllib.request.Request(s, headers=headers)
        with urllib.request.urlopen(req_s, timeout=8) as sr:
            js = sr.read().decode('utf-8', errors='ignore')
            found = set(re.findall(r'([a-zA-Z0-9.-]+\.(?:googleapis\.com|clients6\.google\.com|clients\.google\.com|google|gstatic\.com|googleusercontent\.com|goog|withgoogle\.com))', js))
            all_found.update(found)
    except Exception as e:
        pass

with open('/etc/cascadedns/domains.json', 'r') as f:
    current = {x['domain'].lower() for x in json.load(f)}

missing = []
for d in sorted(all_found):
    if '.' in d and not d.startswith('.') and not d.endswith('.'):
        if d.lower() not in current:
            missing.append(d.lower())

print(f"AI STUDIO MISSING DOMAINS IN DOMAINS.JSON ({len(missing)}):")
for m in sorted(set(missing)):
    print(m)
