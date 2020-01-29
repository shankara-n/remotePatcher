import paramiko
import csv
filepointer = open('newFile', 'r')
contents = csv.reader(filepointer)
row = next(contents)
filepointer.close()
# print(type(row))
# print(row[0])
# print(row[1])
# print(row[2])
ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh_client.connect(hostname=row[0], username=row[1], password=row[2])
stdin,stdout,stderr=ssh_client.exec_command("ls | grep 'new'")

lines = []
lines = stdout.readlines()
for line in lines:
    print(line, end='')

ftp_client = ssh_client.open_sftp()
ftp_client.put('newFile', 'newFile')
ftp_client.close()

ftp_client=ssh_client.open_sftp()
ftp_client.get('hello', 'warpath')
ftp_client.close()

stdin,stdout,stderr=ssh_client.exec_command("ls | grep new")