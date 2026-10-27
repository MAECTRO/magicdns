import paramiko
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('2.56.179.170', username='root', password='4Tq4kgsLoPH7', timeout=10)

def check_node(name, ip, is_local=False):
    if is_local:
        cmd = "cat /etc/cascadedns/domains.json"
    else:
        cmd = f"ssh -o StrictHostKeyChecking=no root@{ip} 'cat /etc/cascadedns/domains.json'"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    raw = stdout.read().decode('utf-8')
    try:
        data = json.loads(raw)
        domains = {d['domain'].lower(): d for d in data}
        return domains
    except Exception as e:
        print(f"Error on {name}: {e}")
        return {}

fi_domains = check_node("Finland", "2.56.179.170", is_local=True)
se_domains = check_node("Sweden", "109.120.132.43")
de_domains = check_node("Germany", "94.249.177.102")

print(f"Finland total: {len(fi_domains)}")
print(f"Sweden total: {len(se_domains)}")
print(f"Germany total: {len(de_domains)}")

# Let's check key Google / Gemini domains
keys_to_check = [
    "jnn-pa.googleapis.com",
    "jnn-pa.clients6.google.com",
    "jnn-pa.clients.google.com",
    "jnn-web-pa.googleapis.com",
    "gemini.app.google",
    "gemini.google.com",
    "gemini.google",
    "gemini.gstatic.com",
    "geminiweb-pa.clients6.google",
    "geminiweb-pa.clients6.google.com",
    "geminiweb-pa.googleapis.com",
    "appsgenaiserver-pa.clients6.google.com",
    "appsgenaiserver-pa.googleapis.com",
    "consent.google",
    "consent.google.com",
    "waa-pa.clients6.google",
    "ogads-pa.clients6.google",
    "push.clients6.google",
    "apis.google",
    "accounts.google",
    "policies.google",
    "cloudconsole-pa.clients6.google",
    "alkalimakersuite-pa.clients6.google",
    "content.googleapis.com",
    "www.googleapis.com",
    "auditrecording-pa.googleapis.com",
    "opal.google",
    "opal.google.com",
    "stitch.withgoogle.com",
    "ai.studio"
]

print("\n--- STATUS OF KEY DOMAINS ---")
for k in keys_to_check:
    fi_st = "FI:" + ("OK" if k in fi_domains else "MISSING")
    se_st = "SE:" + ("OK" if k in se_domains else "MISSING")
    de_st = "DE:" + ("OK" if k in de_domains else "MISSING")
    print(f"{k.ljust(40)} {fi_st.ljust(12)} {se_st.ljust(12)} {de_st.ljust(12)}")

ssh.close()
