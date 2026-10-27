import paramiko
import json
import time
import sys
sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('2.56.179.170', username='root', password='4Tq4kgsLoPH7', timeout=15)

NEW_DOMAINS = [
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
    "geminiweb-pa.clients.google.com",
    "geminiweb-pa.googleapis.com",
    "appsgenaiserver-pa.clients6.google.com",
    "appsgenaiserver-pa.clients.google.com",
    "appsgenaiserver-pa.googleapis.com",
    "consent.google",
    "consent.google.com",
    "waa-pa.clients6.google",
    "waa-pa.clients6.google.com",
    "ogads-pa.clients6.google",
    "ogads-pa.clients6.google.com",
    "push.clients6.google",
    "push.clients6.google.com",
    "push.clients.google.com",
    "apis.google",
    "apis.google.com",
    "accounts.google",
    "accounts.google.com",
    "policies.google",
    "policies.google.com",
    "cloudconsole-pa.clients6.google",
    "cloudconsole-pa.clients6.google.com",
    "alkalimakersuite-pa.clients6.google",
    "alkalimakersuite-pa.clients6.google.com",
    "alkalimakersuiteapplets.pa.clients6.google",
    "alkalimakersuiteapplets.pa.clients6.google.com",
    "webchannel-alkalimakersuite-pa.clients6.google",
    "webchannel-alkalimakersuite-pa.clients6.google.com",
    "people-pa.clients6.google",
    "people-pa.clients6.google.com",
    "content.googleapis.com",
    "www.googleapis.com",
    "auditrecording-pa.googleapis.com",
    "opal.google",
    "opal.google.com",
    "stitch.withgoogle.com",
    "ai.studio",
    "codeassist.google",
    "codeassist.googleapis.com",
    "lh3.google",
    "myaccount.google",
    "ogs.google",
    "one.google",
    "play.google",
    "support.google",
    "workspace.google",
    "console.cloud.google",
    "deepmind.google",
    "deepmind.com",
    "aistudio.google",
    "aistudio.google.com"
]

nodes = [
    ("Finland", "2.56.179.170", True),
    ("Sweden", "109.120.132.43", False),
    ("Germany", "94.249.177.102", False),
]

for name, ip, is_local in nodes:
    print(f"\n================ Updating {name} ({ip}) ================")
    # 1. Read existing domains.json
    if is_local:
        cat_cmd = "cat /etc/cascadedns/domains.json"
    else:
        cat_cmd = f"ssh -o StrictHostKeyChecking=no root@{ip} 'cat /etc/cascadedns/domains.json'"
    
    stdin, stdout, stderr = ssh.exec_command(cat_cmd)
    raw = stdout.read().decode('utf-8')
    data = json.loads(raw)
    
    existing_domains = {d['domain'].lower() for d in data}
    added_count = 0
    for dom in NEW_DOMAINS:
        dom_clean = dom.lower().strip()
        if dom_clean not in existing_domains:
            data.append({
                "domain": dom_clean,
                "tier": "basket1",
                "ip": "2.56.179.170"
            })
            existing_domains.add(dom_clean)
            added_count += 1
            
    print(f"{name}: added {added_count} new domains. Total now: {len(data)}")
    
    # 2. Write back updated domains.json
    new_raw = json.dumps(data, indent=2, ensure_ascii=False)
    timestamp = int(time.time())
    
    if is_local:
        with open(r'C:\Users\GreenFest\.gemini\antigravity\scratch\magicdns\temp_domains.json', 'w', encoding='utf-8') as f:
            f.write(new_raw)
        sftp = ssh.open_sftp()
        sftp.put(r'C:\Users\GreenFest\.gemini\antigravity\scratch\magicdns\temp_domains.json', f'/etc/cascadedns/domains.json.{timestamp}.bak')
        sftp.put(r'C:\Users\GreenFest\.gemini\antigravity\scratch\magicdns\temp_domains.json', '/etc/cascadedns/domains.json')
        sftp.close()
        
        # Restart cascadedns
        stdin, stdout, stderr = ssh.exec_command("systemctl restart cascadedns")
        stdout.channel.recv_exit_status()
        print(f"{name}: cascadedns restarted.")
    else:
        # Write to remote node
        sftp = ssh.open_sftp()
        with open(r'C:\Users\GreenFest\.gemini\antigravity\scratch\magicdns\temp_domains.json', 'w', encoding='utf-8') as f:
            f.write(new_raw)
        sftp.put(r'C:\Users\GreenFest\.gemini\antigravity\scratch\magicdns\temp_domains.json', f'/tmp/domains_{name}.json')
        sftp.close()
        
        cp_cmd = f"ssh -o StrictHostKeyChecking=no root@{ip} 'cp /etc/cascadedns/domains.json /etc/cascadedns/domains.json.{timestamp}.bak && cp /tmp/domains_{name}.json /etc/cascadedns/domains.json && systemctl restart cascadedns'"
        stdin, stdout, stderr = ssh.exec_command(cp_cmd)
        stdout.channel.recv_exit_status()
        print(f"{name}: cascadedns updated and restarted.")

# Verify resolution of key new domains via dig
print("\n--- Verifying resolution via CascadeDNS ---")
for dom in ["gemini.app.google", "jnn-pa.googleapis.com", "accounts.google", "consent.google"]:
    stdin, stdout, stderr = ssh.exec_command(f"dig @127.0.0.1 {dom} +short")
    res = stdout.read().decode('utf-8').strip()
    print(f"dig {dom} -> {res}")

ssh.close()
