import sys, paramiko
sys.stdout.reconfigure(encoding='utf-8')

local_file = r'C:\Users\GreenFest\.gemini\antigravity\scratch\magicdns\support_bot.py'
remote_file = '/root/magicdns_bot.py'
host = '2.56.175.196'
user = 'root'
pwd = '4Tq4kgsLoPH7'

print(f"Connecting to {host}...")
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=pwd, timeout=15)

# Backup current file
stdin, stdout, stderr = ssh.exec_command(f"cp {remote_file} {remote_file}.bak")
stdout.channel.recv_exit_status()
print(f"Created remote backup: {remote_file}.bak")

# Upload new file
sftp = ssh.open_sftp()
sftp.put(local_file, remote_file)
sftp.close()
print("Uploaded new support_bot.py to /root/magicdns_bot.py")

# Check syntax on remote server
stdin, stdout, stderr = ssh.exec_command("python3 -m py_compile /root/magicdns_bot.py")
exit_code = stdout.channel.recv_exit_status()
err = stderr.read().decode('utf-8', errors='replace')
if exit_code != 0:
    print(f"SYNTAX ERROR ON REMOTE: {err}")
    print("Reverting backup...")
    ssh.exec_command(f"cp {remote_file}.bak {remote_file}")
    ssh.close()
    sys.exit(1)
print("Remote python3 syntax check PASSED cleanly!")

# Restart service
stdin, stdout, stderr = ssh.exec_command("systemctl restart magicdns-bot.service")
stdout.channel.recv_exit_status()
print("Service magicdns-bot.service restarted.")

# Check service status
stdin, stdout, stderr = ssh.exec_command("systemctl status magicdns-bot.service --no-pager")
status_out = stdout.read().decode('utf-8', errors='replace')
print("Service status:\n" + status_out)

ssh.close()
print("Deployment completed successfully!")
