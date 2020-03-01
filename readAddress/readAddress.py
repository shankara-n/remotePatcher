from os import path
import csv
frompath = []
topath = []

filepointer = open('Patch Automation - FTP.csv', 'r')
contents = csv.reader(filepointer)
for row in contents:
    frompath.append(row[0])
    topath.append(row[1])
filepointer.close()

for pathf in topath:
    print(path.exists(pathf))
print(frompath)
print(topath)