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
import socket 

# GLOBAL VARIABLES
HOSTNAME = 'raspberrypi.local'
USERNAME = 'pi'
PASSWORD = 'sunshine'

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
    """Takes a filepath to return the list of source and destination paths."""
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

# READ USERNAME, PASSWORD, HOSTNAME AND PORT from IP.csv
def logincred(path):
    """There are sometimes usernames and passes, but without ports, for which we need an extra parameter. Here, we return only the lists without a port number."""

    phost = []
    puser = []
    ppass = []
    port  = []

    try:
        csv_file=open(path, mode='r')
    except IOError:
        print("IP.csv file does not exist")

    contents = csv.reader(csv_file)

    for row in contents:
        phost.append(row[0])
        puser.append(row[1])
        ppass.append(row[2])
        port.append(row[3])
        
    # filepointer.close()

    return phost, puser, ppass, port



# PINGING
# def ping(host):
#     """
#     Returns True if host (str) responds to a ping request.
#     Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
#     """
#     # Option for the number of packets as a function of
#     param = '-n' if platform.system().lower()=='windows' else '-c'
#     # Building the command. Ex: "ping -c 1 google.com"
#     command = ['ping', param, '1', '-W 100',  '-Q', host]
#     return subprocess.call(command) == 0

# # CHECK IP ADDRESS
# def checkIPAddress(ipaddr):
#     goodIPlist=[]
#     badIPlist=[]
#     portlist=[]
#     try:
#         csv_file=open(ipaddr, mode='r')
#     except IOError:
#         print('File does not exist')

#     csv_reader = csv.reader(csv_file, delimiter=',')
#     line_count = 0

#     for row in csv_reader:
#         if line_count==0:
#             line_count+=1
#             continue
#         else:
#             if not row:
#                 continue
#             connectionStatus = ping(row[0])
#             if(connectionStatus==False):
#                 badIPlist.append(row[0])
#             else:
#                 goodIPlist.append(row[0])
#                 portlist.append(row[1])
    
#     #checking if the file is empty
#     if(line_count==0 or 1):
#         print("File is empty.")

#     return goodIPlist, badIPlist, portlist

# Function to test every host and port from the file
def checkHosts(hostlist, userlist, passlist, portlist):
    goodhostlist=[]
    gooduserlist=[]
    goodpasslist=[]
    goodportlist=[]
    
    # badhostlist=[]
    # baduserlist=[]
    # badpasslist=[]
    # badportlist=[]
    ssh_client =paramiko.SSHClient()
    for (host, user, passw, port) in zip(hostlist, userlist, passlist, portlist):
        print("\n\nHostname {}, port #{}, User {}".format(host, port, user))
        try:
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(hostname=host,username=user,password=passw,port=port)
        except socket.gaierror as e:
            # badhostlist.append(host)
            # badportlist.append(port)
            
            if(e.errno == -3):
                print("Hostname could not be resolved. Please check again.")
            elif(e.errno == -2):
                print("Hostname could not be identified. Please check hostname, and remove 'https://' if present.")
            else:
                print(e)
        except Exception as e:
            # badhostlist.append(host)
            # badportlist.append(port)
            print("Unknown exception encountered.")
            print(e)
            print("Exiting...")
        else:
            print("Authentication passed")
            goodhostlist.append(host)
            goodportlist.append(port)
            gooduserlist.append(user)
            goodpasslist.append(passw)
    
    return goodhostlist, gooduserlist, goodpasslist, goodportlist


# Global event for executing command
commandfinish = multiprocessing.Event()  

# HELPER TO EXECUTE ONE COMMAND, WITH TIMING.
def execute(ssh_client, command):
    global HOSTNAME
    global USERNAME
    global PASSWORD
    global PORT

    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname=HOSTNAME,username=USERNAME,password=PASSWORD,port=PORT)
    stdin, stdout, stderr = ssh_client.exec_command(command)
    
    commandfinish.set()
    # time.sleep(2)
    print("Output:")
    # print(stdout.readlines())
    for line in stdout.readlines():
        print(line, end="")
    print("Error:")
    for line in stderr.readlines():
        print(line, end="")

    
    return (stdin, stdout, stderr)

# EXECUTE COMMANDS IN LIST
def remoteCommandExecutor(file):
    commands = []
    waittime = []

    global HOSTNAME
    global USERNAME
    global PASSWORD
    global PORT

    # print("Hostname {}, port #{}, User {}, pass {}".format(HOSTNAME, PORT, USERNAME, PASSWORD))

    filepointer = open(file, 'r')
    contents = csv.reader(filepointer)

    for row in contents:
        commands.append(row[0])
        waittime.append(int(row[1]))
    
    filepointer.close()
    
    ssh_client = paramiko.SSHClient()

    try:
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=HOSTNAME,username=USERNAME,password=PASSWORD,port=PORT)
        
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
    global PORT

    print("="*64)
    print("\n*****STARTING REMOTEPATCHER SCRIPT*****\n")
    print("="*64)
    print("Reading source and destination paths")
    source, dest = readpaths("../input/Patch Automation - FTP.csv")
    # if checkfromexists(source):
    #     print("All source files present")
    # else:
    #     print("Some source files missing")
    print("Done")

    print("Reading login credentials")
    hostlist, userlist, passlist, portlist = logincred("../input/Patch Automation - IPs CSV.csv")
    print("Done")

    print("\nVerifying login credentials")
    hostlist, userlist, passlist, portlist = checkHosts(hostlist, userlist, passlist, portlist)

    print("\nNumber of valid connections : {}".format(len(userlist)))
    

    for (host, user, passw, port) in zip(hostlist, userlist, passlist, portlist):
        HOSTNAME = host
        PORT = port
        USERNAME = user
        PASSWORD = passw
        # print(type(host))
        # print(type(user))
        # print(type(passw))
        # print(type(port))
        print("\n\nHostname {}, port #{}, User {}".format(host, port, user))

        # Execute all the commands in pre transfer
        print("Running precommands")
        remoteCommandExecutor("../input/Patch Automation - SSH commands pre transfer.csv")
        print("Done")


        print("+"*32)
        print("Transferring files")
        ssh_client =paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=HOSTNAME,username=USERNAME,password=PASSWORD,port=PORT)
        
        ftp_client = ssh_client.open_sftp()

        
        print("Starting transfer")

        src, dest = filesToSend("../input/Patch Automation - FTP.csv")

        for (file1, file2) in zip(src, dest):
            try:
                ftp_client.put(file1, file2)
            except Exception:
                print("Some error occured, check the file '{}' path and try again".format(file1))
            
        
        print("Done")

        ftp_client.close()

        print("Running post commands")
        remoteCommandExecutor("../input/Patch Automation - SSH commands post transfer.csv")
        print("Done")


        print("+-"*16 + "+")
        print("\n\nSCRIPT COMPLETE.\n\n")
        print("+-"*16 + "+")



if __name__ == "__main__":
    # remoteCommandExecutor("../input/Patch Automation - SSH commands pre transfer.csv")
    main()
