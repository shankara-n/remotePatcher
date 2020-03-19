
import os
import sys
from datetime import datetime

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

#Checking processor consumption
import psutil

# DB Connection
from pymongo import MongoClient

# Argument parser
import argparse

#To read json configuration file
import json

# Logging setup
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler

import traceback

log_formatter = logging.Formatter('%(message)s')

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

# Default Config (will be overwritten by contents of config.json)
MY_EMAIL_ADDRESS = "developforftc@gmail.com"
PASSWORD = "Sunshine99$"
toMailIDs = ""
checkingPeriod = 60

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
    logger.info("Sending Email to :"+toMailIDs)

    conn = smtplib.SMTP('imap.gmail.com', 587)
    conn.ehlo()
    conn.starttls()
    conn.login(MY_EMAIL_ADDRESS, PASSWORD)

    message = MIMEMultipart()
    message['To'] = toMailIDs
    message['From'] = MY_EMAIL_ADDRESS
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

    conn.sendmail(MY_EMAIL_ADDRESS, toMailIDs.split(','), msg)
   
    conn.quit()
    
    logger.info("[!] E-Mail Alert Sent!")


def loadIdentity():
    global zoneID, plantName, ip
    try:
        try:
            client = MongoClient()

            db = client.voyagerDB

            zoneID = db['zone_data'].find()[0]["zoneID"]
            plantName = db['plant_data'].find()[0]["name"]
            ip = subprocess.check_output(["./checkIP.sh"], shell=True).decode()

            logger.info(zoneID + ", " + plantName)
            logger.info(ip)
            client.close()
        except:
            logger.info("   ***   Cannot connect to DB!!   ***")
            sendEmail(" DB Connection Lost !")
    except:
        logger.info("Could not send email!!! Please check the internet connection.")


def logDBStats():

    logger.info("\n~~~~~~ MongoDB Stats ~~~~~~")

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
    except Exception as e:
        logger.error("   ***   Error connecting to DB!!   ***")
        logger.error("type error: " + str(e))

        try:
            sendEmail(" DB Connection Lost !")
        except Exception as e:
            logger.info("Could not send email!!! Please check the internet connection.")
            logger.error("type error: " + str(e))


def logFileSizes():
    
    logger.info("\n~~~~~~ Log File Stats ~~~~~~")

    # Flag for finding creation of voyagerDB.5
    isDB5created = False

    logger.info('Database File Sizes')
    for (path, dirs, files) in os.walk('/data/db'):
        for fileName in files:
            filePath = os.path.join(path, fileName)
            logger.info('{0: <14}'.format(
                str(os.path.getsize(filePath)))+" : "+filePath)
            if(fileName == "voyagerDB.5"):
                logger.error("[!] WARNING!!! db.5 file created !!!")
                isDB5created = True

    logger.info('Log File Sizes')
    for (path, dirs, files) in os.walk('/var/log'):
        for fileName in files:
            filePath = os.path.join(path, fileName)
            if (fileName.startswith('syslog')) or (fileName.startswith('daemon')):
                logger.info('{0: <14}'.format(
                    str(os.path.getsize(filePath)))+" : "+filePath)

    for (path, dirs, files) in os.walk('/var/log/mongodb'):
        for fileName in files:
            filePath = os.path.join(path, fileName)
            logger.info('{0: <14}'.format(
                str(os.path.getsize(filePath)))+" : "+filePath)

    if isDB5created:
        try:
            sendEmail("voyagerDB.5 created !")
        except Exception as e:
            logger.error("Could not send email!!! Please check the internet connection.")
            logger.error("type error: " + str(e))
            logger.error(traceback.format_exc())

def logSystemStats():

    logger.info("~~~~~~ System Stats ~~~~~~")
    # temp
    cpuTemp = subprocess.check_output(["vcgencmd measure_temp"] , shell=True).decode()
    logger.info("CPU Temperature :" +str(cpuTemp))

    # processor consumption
    cpuConsumption = psutil.cpu_percent(percpu=True)
    logger.info('[*] Processor consumption :' +str(cpuConsumption))

    # memory consumption
    logger.info('[*] Virtual memory usage:')
    logger.info(psutil.virtual_memory())
    logger.info('[*] Swap memory usage:')
    logger.info(psutil.swap_memory())

    # disk usage
    disk = psutil.disk_usage('/')
    logger.info("[*] Disk usage :"+str(disk))

def loadConfiguration():
    global toMailIDs, checkingPeriod, MY_EMAIL_ADDRESS, PASSWORD

    with open('config.json') as configFile:
        config = json.load(configFile)

    checkingPeriod=config['time']
    MY_EMAIL_ADDRESS=config['m0']
    PASSWORD=config['p']
    toMailIDs=','.join(config['recepients'])

    loadIdentity()


if __name__ == "__main__":

    logger.info("\n*********************** ^^^ *********************** Diagnostics Started *********************** ^^^ ***********************\n")
    loadConfiguration()

    while True:
        now = datetime.now() 
        logger.info("\n*********************** Starting checks at: "+now.strftime("%m/%d/%Y, %H:%M:%S")+ "\n")

        logSystemStats()
        logDBStats()
        logFileSizes()

        time.sleep(checkingPeriod)
