FUNCTIONALITY

This diagnostics script runs every 60 seconds and logs the following data
   1> DB Server Status - Memory stats & Connection stats
   2> DB Collection Stats
   3> DB File Sizes (under /var/lib/mongodb and /data/db)
   4> Journalling Status on DB
   5> Capping on all collections
   6> Overall Disk Usage
   7> Log file sizes  (daemon.log, sys.log, mongodb.log)

Additionally Email Alerts are generated under the follwing conditions
1. DB crash
2. Creation of voyagerDB.5 file either at /data/db or /var/lib/mongodb locations


CONFIG INSTRUCTIONS
To configure how often the script runs and to whom the email alerts are sent, edit the diagnostics.service file

Modify the 'ExecStart' line according to the below format
Usage:  "/home/pi/mongoDiagnostics/diagnostics --time CHECKING_PERIOD --m0 SENDER'S ADDRESS --p PASSWORD --m1 MAIL_1 --m2 MAIL_2 --m3 MAIL_3 ..."
If user wishes to enter any particular field enter the corresponding value such as '--m0' for sender's address. Otherwise the user need not enter it since it as an optional argument. However value for checking period(--time) needs to be entered every time.

GRANTING EXECUTABLE PERMISSIONS

chmod u+x diagnostics

SETUP INSTRUCTIONS

1. Transfer the tar file to /home/pi directory
2. Extract the tar file using "tar -xvf diagnostics.tar.gz"
3. Run "sudo cp diagnostics/diagnostics.service /etc/systemd/system/."
4. Run "sudo systemctl enable diagnostics.service"
5. Run "sudo systemctl start diagnostics.service"


