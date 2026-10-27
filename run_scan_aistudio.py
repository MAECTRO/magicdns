import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('2.56.179.170', username='root', password='4Tq4kgsLoPH7', timeout=10)

sftp = ssh.open_sftp()
sftp.put(r'C:\Users\GreenFest\.gemini\antigravity\scratch\magicdns\remote_scan_aistudio.py', '/tmp/remote_scan_aistudio.py')
sftp.close()

stdin, stdout, stderr = ssh.exec_command("python3 /tmp/remote_scan_aistudio.py")
print(stdout.read().decode('utf-8'))
print(stderr.read().decode('utf-8'))

ssh.close()
