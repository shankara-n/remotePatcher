import paramiko

ssh_client = paramiko.SSHClient()


ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh_client.connect(hostname='local', username='reaper', password='password')

ftp_client=ssh_client.open_sftp()
#get is used to fetch files from remote system
ftp_client.get('remotefiletomove','locallocationtostore')

#put is used to place files on remote system
ftp_client.put('localfiletomove', 'remotelocationtostore')

#the local directory path can be specified from root, but by default starts in same folder as the python script.
ftp_client.close()