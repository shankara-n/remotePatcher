# CSV FILE FORMATS

## General guidelines

This is for running exec_port.py

For exec.py, the format of IP.csv has only the IP addresses, one on each line.

Remove any excess spaces before and after the commas. They may cause errors in the program.

## To be added

* Take login credentials both with and without ports. As of now, the IP.csv must have a port.

## FTP.csv

Contains the source and destination files. 

Since the program starts it's execution in the remotePatcher folder, give the source path with respect to the contents of remotePatcher.

The destination path starts from inside /etc/home/pi/ of the destination pc. 

It is possible to override this, for example, giving 
```
/etc/defaults/
```
as the destination path will send the file to /etc/defaults/ of the destination pc.

## IPs.CSV

Be sure to eliminate spaces before and after the commas.

The order to follow is 

```
hostname,username,password,port
```

We are trying to add functionality for both port and non port, but as of now every line needs to have a port.

## Post transfer.csv and Pre transfer.csv

The format is 
```
command,timeout
```
If the timeout is given 0, the process waits until it finishes executing.

Else it will break out and show error if the time exceeds the timeout.

