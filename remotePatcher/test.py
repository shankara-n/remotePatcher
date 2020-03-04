import csv
import platform
import subprocess
import os

def ping(host):
    """
    Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
    """
    # Option for the number of packets as a function of
    param = '-n' if platform.system().lower()=='windows' else '-c'
    # Building the command. Ex: "ping -c 1 google.com -q"
    command = ['ping', param, '1', '-W 100',  '-Q', host]
    return subprocess.call(command) == 0

file_name="../input/Patch Automation - IPs CSV.csv"

#checking if the file exists and was opened properly
try:
    csv_file=open(file_name, mode='r')
except IOError:
    print('File does not exist')
    exit()



goodIPlist=[]
badIPlist=[]
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
    exit()

print('Good IP list:', goodIPlist)
print('Bad IP list:', badIPlist)
