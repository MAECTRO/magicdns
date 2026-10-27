import paramiko
import re

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('2.56.179.170', username='root', password='4Tq4kgsLoPH7', timeout=10)

cmd = """python3 -c "
import urllib.request, re

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'}
req = urllib.request.Request('https://gemini.google.com/app', headers=headers)
with urllib.request.urlopen(req, timeout=10) as r:
    html = r.read().decode('utf-8', errors='ignore')

# Find all script src
scripts = re.findall(r'src=\"([^\"]+)\"', html)
print('Total scripts in HTML:', len(scripts))
all_found_domains = set()

for s in scripts[:10]:
    if not s.startswith('http'):
        s = 'https://gemini.google.com' + s
    try:
        req_s = urllib.request.Request(s, headers=headers)
        with urllib.request.urlopen(req_s, timeout=8) as sr:
            js = sr.read().decode('utf-8', errors='ignore')
            # Extract domain patterns like *.googleapis.com, *.google.com, *.google
            domains = set(re.findall(r'[a-zA-Z0-9.-]+\\.(?:googleapis\\.com|clients6\\.google\\.com|clients\\.google\\.com|google|gstatic\\.com|googleusercontent\\.com)', js))
            all_found_domains.update(domains)
    except Exception as e:
        pass

print('Found domains in JS:')
for d in sorted(all_found_domains):
    print(d)
" """

stdin, stdout, stderr = ssh.exec_command(cmd)
print(stdout.read().decode('utf-8'))
print(stderr.read().decode('utf-8'))

ssh.close()
