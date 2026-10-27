import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('2.56.179.170', username='root', password='4Tq4kgsLoPH7', timeout=10)

stdin, stdout, stderr = ssh.exec_command("curl -s -X POST http://127.0.0.1:5380/domains/reload || curl -s http://127.0.0.1:5380/domains/reload")
print("Reload response:\n", stdout.read().decode('utf-8'))

# Check dig again
stdin, stdout, stderr = ssh.exec_command("dig @127.0.0.1 jnn-pa.googleapis.com +short")
print("dig jnn-pa.googleapis.com:\n", stdout.read().decode('utf-8'))

ssh.close()
