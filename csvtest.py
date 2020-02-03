#FTC-11
#Read source and destination directory from csv
#Approach: navigate to the directory in ssh, and see if it returns an error. If it doesn't, fair game.
import csv
sourcepath = []
destpath = []
filepointer = open('Patch Automation - FTP.csv', 'r')
contents = csv.reader(filepointer)
for row in contents:
    sourcepath.append(row[0])
    destpath.append(row[1])
filepointer.close()
for item in sourcepath:
    print(item)
