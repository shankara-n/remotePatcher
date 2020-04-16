import os
print("Extracting tar file")
os.system("tar -xvf patchFiles.tar")
#check if log rotate is in cron daily or
if os.path.exists("/etc/cron.daily/logrotate"):
    os.system("sudo mv /etc/cron.daily/logrotate /etc/cron.hourly/logrotate")
    print("Configured hourly rotate")


#copy new config files
os.system("sudo cp /home/pi/mongodb-server /etc/logrotate.d/mongodb-server")
print("enabled mongo logs to rotate hourly")
#todo replace with custom rsyslog
os.system("sudo cp /home/pi/rsyslog /etc/logrotate.d/rsyslog")
print("syslogs and daemon logs to rotate hourly")
os.system("sudo systemctl restart cron")
print("Patch Complete")
os.system("sudo rm patchFiles.tar mongodb-server rsyslog install")
