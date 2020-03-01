
import os
import sys

# Compression of logs
import shutil
import subprocess

import time
from datetime import datetime

# E-Mail
import smtplib
from email import encoders
from email.message import Message
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from os import listdir
from os.path import isfile, join
from shutil import copyfile

# DB Connection
from pymongo import MongoClient

# Argument parser
import argparse

# Logging setup
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler

log_formatter = logging.Formatter(' %(message)s')

processName = Path(__file__).stem
logsPath = '/home/pi/Voyager-Zone-Controller/logs/'
logFile = logsPath + processName + '.log'

rotatingFileHandler = RotatingFileHandler(
    logFile, mode='a', maxBytes=5 * 1024 * 1024, backupCount=5, encoding=None, delay=0)
rotatingFileHandler.setFormatter(log_formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(rotatingFileHandler)


# Table Column Sizes
COL_WIDTH = 30
SMALL_COL_WIDTH = 13

# Email Auth
MY_ADDRESS = 'developforftc@gmail.com'
PASSWORD = 'Sunshine99$'

# Default Values
zoneID = "Unknown Zone"
plantName = "Unknown Plant"
ip = "Unknown IP"


# copies all required files to a temporary directory and compress the directory
def compressLogs():

    tempDir = logsPath + "/"+processName

    # remove old logs zip
    if os.path.exists(tempDir + ".zip"):
        os.remove(tempDir + ".zip")
    # remove old logs temp directory
    if os.path.isdir(tempDir):
        shutil.rmtree(tempDir)

    # make new temp dir
    os.mkdir(tempDir)

    # Iterate over all files in logs  directory
    for fileName in listdir(logsPath):
        # check if fileName in this iteration is equal to required file type
        if isfile(join(logsPath, fileName)) and processName in fileName:
            shutil.copyfile(logsPath + "/" + fileName,
                            tempDir + "/" + fileName)

    # writing files to a zipfile
    shutil.make_archive(logsPath+"/"+processName, 'zip', tempDir)
    shutil.rmtree(tempDir)

    return logsPath+"/"+processName + ".zip"


def sendEmail(subject):

    conn = smtplib.SMTP('imap.gmail.com', 587)
    conn.ehlo()
    conn.starttls()
    conn.login(MY_ADDRESS, PASSWORD)

    message = MIMEMultipart()
    message['To'] = toMailIDs
    message['From'] = MY_ADDRESS
    message['Subject'] = subject + " at " + zoneID + ", " + plantName

    zipfilename = compressLogs()

    file = open(zipfilename, 'rb')

    payload = MIMEBase('application', 'octet-stream')
    payload.set_payload((file).read())

    encoders.encode_base64(payload)
    payload.add_header("Content-Disposition", "attachment; filename=logs.zip")

    message.attach(payload)

    message.attach(MIMEText(ip, 'plain'))

    msg = message.as_string()

    print(toMailIDs)
    conn.sendmail(MY_ADDRESS, toMailIDs, msg)
    print("Finished sending Email")

    conn.quit()


def loadIdentity():
    global zoneID, plantName, ip
    try:
        try:
            client = MongoClient()

            db = client.voyagerDB

            zoneID = db['zone_data'].find()[0]["zoneID"]
            plantName = db['plant_data'].find()[0]["name"]
            ip = subprocess.check_output(["./checkIP.sh"], shell=True).decode()

            print(zoneID + ", " + plantName)
            print(ip)
            client.close()
        except:
            logger.info("   ***   Cannot connect to DB!!   ***")
            sendEmail(" DB Connection Lost !")
    except:
        print("Could not send email!!! Please check your connection")


def logDBStats():

    try:
        try:

            client = MongoClient()

            db = client.voyagerDB

            totalStorageSize = 0
            logger.info("File size from mongo ".ljust(COL_WIDTH) +
                        ":" + str(db.command("dbstats")['fileSize']))
            serverStatus = db.command("serverStatus")
            logger.info("DB Connections ".ljust(COL_WIDTH) +
                        ":" + str(serverStatus['connections']))
            logger.info("DB Mem  ".ljust(COL_WIDTH) +
                        ":" + str(serverStatus['mem']))
            logger.info("DB Page Fault  ".ljust(COL_WIDTH) + ":" +
                        str(serverStatus['extra_info']['page_faults']))
            ret = subprocess.check_output(["./checkJournal.sh"], shell=True)
            logger.info(ret.decode())
            ret = subprocess.check_output(["./checkDiskUsage.sh"], shell=True)
            logger.info(ret.decode())

            # Collections
            logger.info("\nCOLLECTION".ljust(COL_WIDTH) + "\tSTORAGE_SIZE".ljust(
                SMALL_COL_WIDTH) + "\tCAPPED".ljust(SMALL_COL_WIDTH) + "\tFragmentation\n")
            for coll in db.collection_names():
                stats = db.command("collstats", coll)

                totalStorageSize += stats['storageSize']
                if 'capped' in list(stats):
                    cap = True
                else:
                    cap = False
                frag = stats['storageSize'] / \
                    (stats['size'] + stats['totalIndexSize'])
                frag = round(frag, 2)

                logger.info(coll.ljust(COL_WIDTH) + "\t" + str(stats['storageSize']).ljust(
                    SMALL_COL_WIDTH) + "\t" + str(cap).ljust(SMALL_COL_WIDTH) + "\t" + str(frag))

            logger.info("\nTOTAL STORAGE_SIZE : "+str(totalStorageSize))

            client.close()
        except:
            logger.info("   ***   Cannot connect to DB!!   ***")
            sendEmail(" DB Connection Lost !")
    except:
        print("Could not send email!!! Please check your connection")


def logFileSizes():

    # Flag for finding creation of voyagerDB.5
    isDB5created = False

    logger.info('Database File Sizes')
    for (path, dirs, files) in os.walk('/data/db'):
        for fileName in files:
            filePath = os.path.join(path, fileName)
            file1 = open(logFile, 'a')
            logger.info('{0: <14}'.format(
                str(os.path.getsize(filePath)))+" : "+filePath)
            if(fileName == "voyagerDB.5"):
                isDB5created = True

    logger.info('Log File Sizes')
    for (path, dirs, files) in os.walk('/var/log'):
        for fileName in files:
            filePath = os.path.join(path, fileName)
            file1 = open(logFile, 'a')
            if (fileName.startswith('syslog')) or (fileName.startswith('daemon')):
                logger.info('{0: <14}'.format(
                    str(os.path.getsize(filePath)))+" : "+filePath)

    for (path, dirs, files) in os.walk('/var/log/mongodb'):
        for fileName in files:
            filePath = os.path.join(path, fileName)
            file1 = open(logFile, 'a')
            logger.info('{0: <14}'.format(
                str(os.path.getsize(filePath)))+" : "+filePath)

    try:
        if isDB5created:
            sendEmail("voyagerDB.5 created !")
    except:
        print("Could not send email!!! Please check your connection")


def main():
    global toMailIDs

    # Getting the command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--time', type=int, help='Checking Period')
    parser.add_argument(
        '--m0', type=str, default='developforftc@gmail.com', help='Sender\'s Email ID')
    parser.add_argument('--p', type=str, default='Sunshine99$',
                        help='Sender\'s Password')

    flg = 0
    if(sys.argv[3]=='m0'):
        MY_ADDRESS = args.m0
        PASSWORD = args.p
        flg = 1
    
    if flg==1:
        l = len(sys.argv)-7
    else: 
        l = len(sys.argv)-3
    
    for i in range(1, l):
        x = '--m'+str(i)
        parser.add_argument(x, help='Receiver\'s mail ID')
    args = parser.parse_args()

    # Send mail to ourselves atleast
    toMailIDs = MY_ADDRESS

    if len(sys.argv) < 2:
        print("Usage : diagnostics --time CHECKING_PERIOD --m0 SENDER'S_EMAIL_ID --p SENDER'S_PASSWORD --m1 MAIL_1 --m2 MAIL_2 --m3 MAIL_3 ...")
        sys.exit()
    else:
        checkingPeriod = args.time
        if flg == 1:
            mailIDcount = (len(sys.argv) - 7)/2
            i = 6
        else:
            mailIDcount = (len(sys.argv) - 3)/2
            i = 2

    mailIDcount = int(mailIDcount)
    i = int(i)+2
    for index in range(1, mailIDcount+1):
        toMailIDs = toMailIDs + "," + sys.argv[i]
        i = i+2

    print(toMailIDs)

    loadIdentity()

    while True:
        logDBStats()
        logFileSizes()
        time.sleep(int(checkingPeriod))


if __name__ == "__main__":
    main()
