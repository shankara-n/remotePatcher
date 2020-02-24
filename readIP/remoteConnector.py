import csv
import platform
import subprocess

def ping(host):
    """
    Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
    """
    # Option for the number of packets as a function of
    param = '-n' if platform.system().lower()=='windows' else '-c'
    # Building the command. Ex: "ping -c 1 google.com"
    command = ['ping', param, '1', host]
    return subprocess.call(command) == 0

with open('Patch Automation - IPs CSV.csv', mode='r') as csv_file:
    IPlist=[]
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if line_count==0:
            line_count+=1
            continue
        else:
            result = ping(row[0])
            print(result)
            if(row[0]==''):
                print('No IP found', row[0])
            elif(result==False):
                print('Bad IP address', row[0])
            else:
                IPlist.append(row[0])
                print('Successfully connected to IP ',row[0])
print(IPlist)
        
