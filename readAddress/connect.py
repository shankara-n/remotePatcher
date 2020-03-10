import paramiko

HOSTNAME = '192.168.43.130'
USERNAME = 'vigneshsrinivasan'
PASSWORD = 'apple'

ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh_client.connect(hostname='192.168.43.130',username='vigneshsrinivasan',password='apple')

stdin, stdout, stderr = ssh_client.exec_command("ls")
print(stdout.readlines())