import paramiko
import json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('2.56.179.170', username='root', password='4Tq4kgsLoPH7', timeout=10)

stdin, stdout, stderr = ssh.exec_command("cat /etc/cascadedns/domains.json")
raw = stdout.read().decode('utf-8')
data = json.loads(raw)

google_domains = [d['domain'] for d in data if any(k in d['domain'] for k in ['google', 'gemini', 'deepmind', 'bard', 'antigravity'])]
print(f"Total domains in domains.json: {len(data)}")
print(f"Google/Gemini domains currently in domains.json: {len(google_domains)}")
for d in sorted(google_domains):
    print(d)

ssh.close()
