import paramiko
ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh_client.connect(hostname='10.4.1.15', username='s1221', password='testinglol')
stdin,stdout,stderr=ssh_client.exec_command("ls")

lines = []
lines = stdout.readlines()
for line in lines:
    print(line, end='')
