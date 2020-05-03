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

def checkIPAddress(hostlist):
    goodIPlist=[]
    badIPlist=[]

    for host in hostlist:
        connectionStatus = ping(host)
        if(connectionStatus==False):
            badIPlist.append(host)
        else:
            goodIPlist.append(host)

    print(goodIPlist)
    print(badIPlist)


hostlist, userlist, passlist, portlist = logincred("../input/Patch Automation - IPs CSV.csv")

def checkHosts(hostlist, userlist, passlist, portlist):
    goodhostlist=[]
    goodportlist=[]
    badhostlist=[]
    badportlist=[]
    ssh_client =paramiko.SSHClient()
    for (host, user, passw, port) in zip(hostlist, userlist, passlist, portlist):
        print("Hostname {}, port #{}, User {}".format(host, port, user))
        try:
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(hostname=host,username=user,password=passw,port=port)
        except socket.gaierror as e:
            # print(e)
            badhostlist.append(host)
            badportlist.append(port)
            if(e.errno == -3):
                print("Hostname could not be resolved. Please check again.")
            if(e.errno == -2):
                print("Hostname could not be identified. Please check hostname, and remove 'https://' if present.")
        except Exception as e:
            badhostlist.append(host)
            badportlist.append(port)
            print("Unknown exception encountered.")
            print(e)
            print("Exiting...")
        else:
            goodhostlist.append(host)
            goodportlist.append(port)
    
    return goodhostlist, goodportlist, badhostlist, badportlist


# checkIPAddress(hostlist)