import paramiko
import re

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('2.56.179.170', username='root', password='4Tq4kgsLoPH7', timeout=10)

# 1. Fetch current domains.json on Finland
stdin, stdout, stderr = ssh.exec_command("cat /etc/cascadedns/domains.json")
raw_json = stdout.read().decode('utf-8')
import json
current_domains = set()
try:
    obj = json.loads(raw_json)
    if isinstance(obj, list):
        for item in obj:
            if isinstance(item, dict) and 'domain' in item:
                current_domains.add(item['domain'].lower())
except Exception as e:
    print("Error parsing domains.json:", e)

print(f"Current domains.json has {len(current_domains)} domains.")

# 2. Extract domains from live gemini.google.com/app HTML
cmd_gemini = """python3 -c "
import urllib.request, re
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'}
req = urllib.request.Request('https://gemini.google.com/app', headers=headers)
with urllib.request.urlopen(req, timeout=10) as r:
    html = r.read().decode('utf-8', errors='ignore')

# Extract all hostnames
domains = set(re.findall(r'https?://([a-zA-Z0-9.-]+\\.(?:google|google\\.com|googleapis\\.com|gstatic\\.com|goog|googleusercontent\\.com))', html))
print('GEMINI_DOMAINS:' + ','.join(domains))

# Also look for content security policy hosts
csp = re.findall(r'https?://([a-zA-Z0-9.-]+)', html)
" """

stdin, stdout, stderr = ssh.exec_command(cmd_gemini)
out = stdout.read().decode('utf-8')
print("Gemini response:")
print(out[:500])

ssh.close()
