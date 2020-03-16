import time
import multiprocessing
import threading
import paramiko

HOSTNAME = '192.168.43.112'
USERNAME = 'pi'
PASSWORD = 'sunshine'

commandfinish = multiprocessing.Event()  

# HELPER TO EXECUTE ONE COMMAND, WITH TIMING.
def execute(ssh_client, command):
    global HOSTNAME
    global USERNAME
    global PASSWORD

    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname=HOSTNAME, username=USERNAME, password=PASSWORD)
    stdin, stdout, stderr = ssh_client.exec_command(command)
    commandfinish.set()
    # time.sleep(2)
    print("OUTPUT")
    print(stdout.readlines())
    print("ERROR LOG")
    if not stderr.readlines():
        print("No errors")
    else:
        print(stderr.readlines())
    return (stdin, stdout, stderr)

# EXECUTE COMMANDS IN LIST
def remoteCommandExecutor():
    commands = []
    waittime = []

    global HOSTNAME
    global USERNAME
    global PASSWORD

    ssh_client = paramiko.SSHClient()
    print("Starting...")
    try:
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=HOSTNAME, username=USERNAME, password=PASSWORD)
        print("Connected. Enter input and wait time")
        command = input()
        wtime = int(input())
    
        print(command)
        exec = multiprocessing.Process(target=execute, name="command execution", args=(ssh_client, command))
        exec.start()
        
        for i in range(wtime):
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


for i in range(6):
    remoteCommandExecutor()