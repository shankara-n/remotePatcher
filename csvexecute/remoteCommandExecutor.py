MAX_WAIT_SECS = 6
import paramiko
import csv
import time
import multiprocessing
import threading

commandfinish = multiprocessing.Event()

def remoteCommandExecutor(ssh_client, command):
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname='local', username='reaper', password='password')
    stdin, stdout, stderr = ssh_client.exec_command(command)
    commandfinish.set()
    time.sleep(2)
    print(stdout.readlines())
    print(stderr.readlines())
    return (stdin, stdout, stderr)

precommands = []
precommand = '; '
filepointer = open('Patch Automation - SSH commands pre transfer.csv', 'r')
contents = csv.reader(filepointer)
for row in contents:
    precommands.append(row[0])
filepointer.close()
precommand = precommand.join(precommands)

# postcommands = []
# postcommand = '; '
# filepointer = open('Patch Automation - SSH commands post transfer.csv', 'r')
# contents = csv.reader(filepointer)
# for row in contents:
#     postcommands.append(row[0])
# filepointer.close()
# postcommand = postcommand.join(postcommands)

ssh_client = paramiko.SSHClient()

try:
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname='local', username='reaper', password='password')

    
    for command in precommands:
        print(command)
        exec = multiprocessing.Process(target=remoteCommandExecutor, name="command execution", args=(ssh_client, command))
        exec.start()
        
        for i in range(MAX_WAIT_SECS):
            time.sleep(1)
            print("time is {}".format(i))
            print(exec.is_alive)
            if commandfinish.is_set():
                break
            
        if not commandfinish.is_set():
            print("Process still running after timeout. stopping...")
            exec.terminate()
        else:
            print("Display results of process...")
        commandfinish.clear()
        
except Exception as e:
    print(e)
    print("Exiting...")
