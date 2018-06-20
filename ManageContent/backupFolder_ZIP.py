'''
    Code to find all items in a folder, collect metadata and thumbnail and create
      a backup zip file (json + pngs)
      Note: This is mainly for backing up metadata of items referencing services.
      Content (csv, feature service, etc) is not downloaded.
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

outputDir = r"c:\temp\ago"

od = ODManager(user, pword, portal, localPath)

items = []
gitems = od.listItemsByGroup("OD_Data_EN")
for g in gitems.content():
    print(g.title)
    t = g.download_thumbnail(save_folder=outputDir)
    i = {"title": g.title,
        "type": g.type,
        "url": g.url,
        "typeKeywords": g.typeKeywords,
        "description": g.description,
        "tags": g.tags,
        "snippet": g.snippet,
        "thumbnail": os.path.basename(t),
        "extent": g.extent,
        "spatialReference": g.spatialReference,
        "accessInformation": g.accessInformation,
        "licenseInfo": g.licenseInfo
    }

    items.append(i)


jfile = os.path.join(outputDir, "backup.json")
with open(jfile, 'w') as outfile:
    json.dump(items, outfile)

zfile = os.path.join(outputDir, "../", "_agoBackup")
shutil.make_archive(zfile, 'zip', outputDir)