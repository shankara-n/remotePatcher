# remotePatcher

## Description

Repository of code for remotely updating and applying patches to scripts on remote systems. The scripts read inputs from the csv files in the input folder.

## Initialisation

Ensure you have pip. Then run:

```
python3 -m pip install -r requirements.txt
```

## Working

The script is remotePatcher/exec.py.

### Tasks

- [x] Read a csv file, execute the commands on remote system.

- [x] Read IP addresses and login credentials from csv file.

- [ ] Strategy to retry commands

## Using the script

All inputs are given to the csv files inside the inputs folder. A working description of the csv files and their use will be in that folder.

Since paramiko is being used with multiprocessing, the outputs can overlap sometimes. I'm not able to guard against it without adding one second delays before every command, and that doesn't work for high latency connections. 

Run the scripts with 
```
python3 exec.py
```



