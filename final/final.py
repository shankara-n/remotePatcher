# for path.exists(), os.access() and os.W_OK()
from os import path
from os import access
from os import W_OK

# for handling csv files
import csv

# for verifying ip independent of platform
import platform
import subprocess

# for running commands as mulutiprocessing routine to check timeout
import time
import multiprocessing

# for ssh and sftp
import paramiko

# GLOBAL VARIABLES
# HOSTNAME = 'raspberrypi.local'
# USERNAME = 'pi'
# PASSWORD = 'sunshine'

HOSTNAME = 'proxy72.rt3.io'
USERNAME = 'pi'
PASSWORD = 'sunshine'
CHOICE = 0

# filepointer = open('Patch Automation - FTP.csv', 'r')

# READING FILE FOR CHECKING
def readpaths(file):
    """Reads from path passed as file, and returns two lists"""
    frompath = []
    topath = []

    filepointer = open(file, 'r')
    contents = csv.reader(filepointer)
    for row in contents:
        frompath.append(row[0])
        topath.append(row[1])
    filepointer.close()

    # for pathf in topath:
    #     print(path.exists(pathf))
    # for pathf in frompath:
    #     print(path.exists(pathf))
    # print(frompath)
    # print(topath)
    return frompath, topath


def filesToSend(file):
    src=[]
    dest=[]
    filepointer = open(file, 'r')
    contents = csv.reader(filepointer)
    for row in contents:
        src.append(row[0])
        dest.append(row[1])
    return src, dest


# VERIFYING SOURCE FILES EXISTS
def checkfromexists(frompath):
    """Serially checks each path in frompath, returns True iff all files exist."""
    for file in frompath:
        if not path.isfile(file):
            return False
    return True

# VERIFYING DESTINATION FOLDER EXISTS
def checktoexists(topath):
    """Intended to check if the directory of topath exists and needs discussion"""
    for file in topath:
        directory = file.split('/')
        directory.pop()
        directory='/'.join(directory)
        if not path.exists(directory):
            if not access(directory, W_OK):
                print('No write access to', directory)
                return False
    return True

# PINGING
def ping(host):
    """
    Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
    """
    # Option for the number of packets as a function of
    param = '-n' if platform.system().lower()=='windows' else '-c'
    # Building the command. Ex: "ping -c 1 google.com"
    command = ['ping', param, '1', '-W 100',  '-Q', host]
    return subprocess.call(command) == 0

# CHECK IP ADDRESS
def checkIPAddress(ipaddr):
    goodIPlist=[]
    badIPlist=[]

    try:
        csv_file=open(ipaddr, mode='r')
    except IOError:
        print('File does not exist')

    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0

    for row in csv_reader:
        if line_count==0:
            line_count+=1
            continue
        else:
            if not row:
                continue
            connectionStatus = ping(row[0])
            if(connectionStatus==False):
                badIPlist.append(row[0])
            else:
                goodIPlist.append(row[0])
    
    #checking if the file is empty
    if(line_count==0 or 1):
        print("File is empty.")

    return goodIPlist, badIPlist

# Global event for executing command
commandfinish = multiprocessing.Event()  

# HELPER TO EXECUTE ONE COMMAND, WITH TIMING.
def execute(ssh_client, command):
    global HOSTNAME
    global USERNAME
    global PASSWORD
    global CHOICE

    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    if CHOICE == 0:
        ssh_client.connect(hostname=HOSTNAME, username=USERNAME, password=PASSWORD)
    else
        ssh_client.connect(hostname=HOSTNAME,username=USERNAME,password=PASSWORD, port=34136)
    stdin, stdout, stderr = ssh_client.exec_command(command)
    
    # time.sleep(2)
    print("Output:")
    for line in stdout.readlines():
        print(line, end="")
    print("Error:")
    for line in stderr.readlines():
        print(line, end="")

    commandfinish.set()
    return (stdin, stdout, stderr)

# EXECUTE COMMANDS IN LIST
def remoteCommandExecutor(file):
    commands = []
    waittime = []

    global HOSTNAME
    global USERNAME
    global PASSWORD
    global CHOICE

    filepointer = open(file, 'r')
    contents = csv.reader(filepointer)

    for row in contents:
        commands.append(row[0])
        waittime.append(int(row[1]))
    
    filepointer.close()
    
    ssh_client = paramiko.SSHClient()

    try:
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if CHOICE == 0:
            ssh_client.connect(hostname=HOSTNAME, username=USERNAME, password=PASSWORD)
        else
            ssh_client.connect(hostname=HOSTNAME,username=USERNAME,password=PASSWORD, port=34136)
        
        for (command, wtime) in zip(commands, waittime):
            print("+"*32)
            print("EXECUTING COMMAND \"" + command + "\"")

            if(wtime == 0):
                stdin,stdout,stderr=ssh_client.exec_command(command)
                print("Output:")
                if stdout.readlines():
                    for line in stdout.readlines():
                        print(line)
                else:
                    print("No output produced")
                print("Errors:")
                if stdout.readlines():
                    for line in stdout.readlines():
                        print(line)
                else:
                    print("No errors produced")
            else:
                exec = multiprocessing.Process(target=execute, name="command execution", args=(ssh_client, command))
                exec.start()
                
                for i in range(wtime):
                    time.sleep(1)
                    print("Wait time :{}".format(i+1))
                    if commandfinish.is_set():
                        break
                    
                if not commandfinish.is_set():
                    print("Process still running after timeout. Stopping...")
                    exec.terminate()

                commandfinish.clear()
                
            
    except Exception as e:
        print(e)
        print("Exiting...")

# Verify all files are placed where they should be
def checkcsv(listofpaths):
    for path in listofpaths:
        try:
            __ =open(path, mode='r')
        except IOError:
            print('File {} not found'.format(path))


# SETUP
def main():
    
    global HOSTNAME
    global USERNAME
    global PASSWORD

    print("="*64)
    print("*****STARTING REMOTEPATCHER SCRIPT*****\n\n")
    print("="*64)
    CHOICE = int(input("Use local rpi or remote rpi?"))
    if(CHOICE == 0):
        HOSTNAME = 'raspberrypi.local'
        USERNAME = 'pi'
        PASSWORD = 'sunshine'
    elif (CHOICE == 1):
        pass

    source, dest = readpaths("../input/Patch Automation - FTP.csv")
    # if checkfromexists(source):
    #     print("All source files present")
    # else:
    #     print("Some source files missing")

    # goodIPlist, badIPlist = checkIPAddress("../input/Patch Automation - IPs CSV.csv")
    

    # if not goodIPlist:
    #     print("No IP addresses were succesfully verified\nFATAL ERROR")
    #     exit()

    goodIPlist = [HOSTNAME]

    for ip in goodIPlist:
        HOSTNAME = ip

        # Execute all the commands in pre transfer
        remoteCommandExecutor("../input/Patch Automation - SSH commands pre transfer.csv")

        ssh_client =paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if CHOICE == 0:
            ssh_client.connect(hostname=HOSTNAME, username=USERNAME, password=PASSWORD)
        else
            ssh_client.connect(hostname=HOSTNAME,username=USERNAME,password=PASSWORD, port=34136)
        
        ftp_client = ssh_client.open_sftp()

        print("+"*32)
        print("Starting transfer")

        src, dest = filesToSend("../input/Patch Automation - FTP.csv")

        for (file1, file2) in zip(src, dest):
            ftp_client.put(file1, file2)
        
        print("Transfer complete")

        ftp_client.close()
        remoteCommandExecutor("../input/Patch Automation - SSH commands post transfer.csv")

        print("+-"*16 + "+")
        print("\n\nSCRIPT COMPLETE.\n\n")
        print("+-"*16 + "+")



if __name__ == "__main__":
    # remoteCommandExecutor("../input/Patch Automation - SSH commands pre transfer.csv")
    main()