import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8')

if __name__ == '__main__':
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect('2.56.175.196', username='root', password='4Tq4kgsLoPH7', timeout=10)
        stdin, stdout, stderr = ssh.exec_command('dig @127.0.0.1 jnn-pa.googleapis.com')
        print(stdout.read().decode('utf-8'))
        ssh.close()
    except Exception as e:
        print('Dig test skipped or connection error:', e)
