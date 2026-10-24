import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("2.56.179.170", username="root", password="4Tq4kgsLoPH7", timeout=15)

def run_cmd(client, cmd, title=""):
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    print(f"=== {title} ===")
    if out: print(out[:1500])
    if err: print("[ERR]", err[:500])

run_cmd(ssh, "ss -tulpn | grep -E ':53|:443'", "FINLAND PORTS 53 / 443")
run_cmd(ssh, "systemctl list-units --type=service --state=running | grep -E 'dns|nginx|cascade|named'", "FINLAND RUNNING SERVICES")

# From Finland, check Sweden (10.10.0.1) and Germany (10.10.0.2)
run_cmd(ssh, "ssh -o StrictHostKeyChecking=no 10.10.0.1 'ss -tulpn | grep -E \":53|:443\"'", "SWEDEN PORTS")
run_cmd(ssh, "ssh -o StrictHostKeyChecking=no 10.10.0.1 'systemctl list-units --type=service --state=running | grep -E \"dns|nginx|cascade|named\"'", "SWEDEN SERVICES")
run_cmd(ssh, "ssh -o StrictHostKeyChecking=no 10.10.0.1 'cat /etc/nginx/nginx.conf | head -n 40'", "SWEDEN NGINX HEAD")

run_cmd(ssh, "ssh -o StrictHostKeyChecking=no 10.10.0.2 'ss -tulpn | grep -E \":53|:443\"'", "GERMANY PORTS")
run_cmd(ssh, "ssh -o StrictHostKeyChecking=no 10.10.0.2 'systemctl list-units --type=service --state=running | grep -E \"dns|nginx|cascade|named\"'", "GERMANY SERVICES")

ssh.close()
