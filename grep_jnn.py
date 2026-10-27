import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('2.56.179.170', username='root', password='4Tq4kgsLoPH7', timeout=10)

stdin, stdout, stderr = ssh.exec_command("grep -B 2 -A 5 'jnn-pa.googleapis.com' /etc/cascadedns/domains.json")
print("grep jnn:\n", stdout.read().decode('utf-8'))

ssh.close()
