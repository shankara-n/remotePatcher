import paramiko
# HOSTNAME = '192.168.43.112'
# USERNAME = 'pi'
# PASSWORD = 'sunshine'

HOSTNAME = 'raspberrrypi.local'
USERNAME = 'pi'
PASSWORD = 'sunshine'

def execute(command):
    ssh_client = paramiko.SSHClient()
    HOSTNAME = 'raspberrrypi.local'
    USERNAME = 'pi'
    PASSWORD = 'sunshine'
    try:
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=HOSTNAME, username=USERNAME, password=PASSWORD)
        print("Connection succesful, executing now")
        stdin,stdout,stderr=ssh_client.exec_command(command)
        for line in stdout.readlines():
            print(line, end="")
        for line in stderr.readlines():
            print(line, end="")
        
        
    except Exception as e:
        print(e)
        print("Exiting...")

for i in range(6):
    print("Enter command")
    command = input()
    execute(command)
    print("\n\n")