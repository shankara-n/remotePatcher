MAX_WAIT_SECS = 6
import paramiko
import csv
import time

precommands = []
precommand = '; '
filepointer = open('Patch Automation - SSH commands pre transfer.csv', 'r')
contents = csv.reader(filepointer)
for row in contents:
    precommands.append(row[0])
filepointer.close()
precommand = precommand.join(precommands)

postcommands = []
postcommand = '; '
filepointer = open('Patch Automation - SSH commands post transfer.csv', 'r')
contents = csv.reader(filepointer)
for row in contents:
    postcommands.append(row[0])
filepointer.close()
postcommand = postcommand.join(postcommands)

ssh_client = paramiko.SSHClient()

try:
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname='10.53.78.48', username='reaper', password='password')
    print(precommand)
    stdin, stdout, stderr = ssh_client.exec_command(precommand)
    time.sleep(MAX_WAIT_SECS)
    if stdout.channel.recv_ready():
        print("Command executed without errors, printing output log")
        print(stdout.readlines())
    elif stderr.channel.recv_ready() is True:
        print("An error has occured\nExiting...")
        print(stderr.readlines())
    else:
        print("The process could not be completed in time.")
        
except Exception as e:
    print(e)
    print("Exiting...")
