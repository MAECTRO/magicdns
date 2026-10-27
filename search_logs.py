import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('2.56.179.170', username='root', password='4Tq4kgsLoPH7', timeout=10)

cmd = "grep -i -E 'teletype|bitrix' /var/log/nginx/* 2>/dev/null"
stdin, stdout, stderr = ssh.exec_command(cmd)
out = stdout.read().decode('utf-8', errors='replace')
print("Logs found:")
print(out if out.strip() else "No direct matches in /var/log/nginx/*")

# Also check gz logs if rotated
cmd2 = "zgrep -i -E 'teletype|bitrix' /var/log/nginx/*.gz 2>/dev/null"
stdin, stdout, stderr = ssh.exec_command(cmd2)
out2 = stdout.read().decode('utf-8', errors='replace')
if out2.strip():
    print("Found in gz logs:")
    print(out2)

ssh.close()
