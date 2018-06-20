'''
    Code to unzip a backup file and hydrate portal with the items inside.
      A zip file is used as it includes the thumbnails and possible data.
      This script uses the content created from backupFolder.ZIP.py
    Calls Manager.py  
    Authentication through the `credentials.ini` file
    Requirements: Python 3+, ArcGIS Python API
    Date: June 20, 2018
'''

from Manager import ODManager
import configparser
import os, sys, json
import shutil

config = configparser.ConfigParser()

localPath = sys.path[0]
configFile  = os.path.join(localPath, "credentials.ini")

config.read(configFile)
user = config['auth']['username']
pword = config['auth']['password']
portal = config['auth']['agol']

zipFile = r"C:\temp\_agoBackup.zip"
outputDir = r"C:\temp\tempextract"
shutil.unpack_archive(zipFile, outputDir)

od = ODManager(user, pword, portal, localPath)

jFile = os.path.join(outputDir, "backup.json")
with open(jFile, 'r') as j:
    jlist = j.read()
    
for i in json.loads(jlist):
    print("Creating: {}".format(i['title']))  
    thumpPath = os.path.join(outputDir, i['thumbnail'])
    response = od.createItem(json = i, data=None, thumbnail=thumpPath)
    print(response)

    # Further work to move the response to a folder or group could happen
