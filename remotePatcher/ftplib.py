HOSTNAME = 'raspberrypi.local'
USERNAME = 'pi'
PASSWORD = 'sunshine'
PORT = '22'
import sys
import time
import paramiko
from tqdm import tqdm

'''
How this works:
viewBar is a function to calculate and display the percentage completed at every transfer. 
Paramiko has a parameter for callback, which is basically calling a function every time some action occurs in the function, or every tick.
Paramiko's put has a callback that gives two values, the portion transferred and the total file size. 

So the key part was to make sure every call to the viewBar knew which bar to update, and I found a solution online that uses a function to get everything in one tidy package.
This viewBar was tied directly to pbar, so we don't have to pass it as a param.
'''



def tqdmWrapViewBar(*args, **kwargs):
    pbar = tqdm(*args, **kwargs)  # make a progressbar
    last = [0]  # last known iteration, start at 0
    def viewBar(a, b):
        pbar.total = int(b)
        pbar.update(int(a - last[0]))  # update pbar with increment
        last[0] = a  # update last known iteration
    return viewBar, pbar  # return callback, tqdmInstance

ssh_client =paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh_client.connect(hostname=HOSTNAME,username=USERNAME,password=PASSWORD,port=PORT)
ftp_client = ssh_client.open_sftp()


cbk, pbar = tqdmWrapViewBar(unit='b', unit_scale=True)
ftp_client.put('testfile.txt','test.txt',callback=cbk)
pbar.close()
print("")

cbk, pbar = tqdmWrapViewBar(unit='b', unit_scale=True)
ftp_client.put('testfile.txt','test2.txt',callback=cbk)
pbar.close()



ftp_client.close()
