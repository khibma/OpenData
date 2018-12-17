# -*- coding: utf-8 -*-
from arcgis.gis import GIS
#from arcgis.gis import server
import configparser
import os
import csv
import sys
import datetime

class ODManager(object):

    def __init__(self, username, password, portal, outputDir):
        self.username = username
        self.password = password
        self.poral = portal
        self.outDir = outputDir
        self.gis = GIS(portal, username, password)
        self.me = self.gis.users.me
        self.folders = self.me.folders
        self.groups = self.gis.groups.search("owner:{}".format(self.username))

    def convertDate(self, adate):
        ''' Convert Epoch into human readable date '''
        fmt = "%Y-%m-%d %H:%M:%S"
        t = datetime.datetime.fromtimestamp(float(adate)/1000.)
        #t_utc = datetime.datetime.utcfromtimestamp(float(adate)/1000.)        
        return t.strftime(fmt) 


    def findGroups(self, outputPath=None):
        '''Get all groups owned by the authenticated user and save to csv
            Returns a file if outputPath supplied, otherwise returns the Group obj.
        '''

        if outputPath != None:
            if ".csv" not in outputPath:
                outputPath = os.path.join(outputPath, "groups.csv")

            with open(outputPath, 'w') as f:
                headers = self.groups[0].keys()
                w = csv.DictWriter(f, headers)
                w.writeheader()    
                for g in self.groups:                    
                    w.writerow(g)
            return outputPath
        
        else:
            return self.groups
    

    def listItemsByFolder(self, folderName):
        ''' List all items in a folder '''
  
        folderItems = self.me.items(folderName)
        if folderItems:
            return folderItems
        else:
            return None

    def listItemsByGroup(self, groupName):
        ''' List all Items in a group '''

        for g in self.groups:
            if g.title == groupName:
                return g

        return None

    def audit(self, agolitem, lang="EN"):

        def _fixExtent(ai):
            ext = [[-76.3555907112863, 44.9616839016198], [-75.2466242192526, 45.5371104704101]]
            update = ai.update(item_properties={'extent': ext})
            return update

        enLicense = "URL TO LICENSE"
        frLicense = "URL TO LICENSE"
        enTags = ["environment", "transportation", "parks", "infrastructure", "health", "local gov", "business", "geospatial"]
        frTags = ["environnement", "transport", "parcs", "infrastructure", "santé", "administration municipale", "affaires", "géospatial"]

        report = {}

        if agolitem.access == "private": return

        if lang == "EN":
            if enLicense not in agolitem['licenseInfo']:                
                report['liceseInfo'] = agolitem['licenseInfo']
            if not set([i.lower() for i in agolitem['tags']]).intersection(enTags):                
                report['tags'] = agolitem['tags']

        elif lang == "FR":
            if "NO" in agolitem['title']:                
                report['title'] =agolitem['title']
            if frLicense not in agolitem['licenseInfo']:                                     
                report['liceseInfo'] = agolitem['licenseInfo']
            if not set([i.lower() for i in agolitem['tags']]).intersection(frTags):                
                report['tags'] = agolitem['tags']

        if not agolitem['extent']:
            u = _fixExtent(agolitem)
            if not u:
                report['extent'] = "No extent set"
            else:
                print("INFO: Fixed extent for {}".format(agolitem['title']))

        if not agolitem['title']:            
            report['title'] =agolitem['title']
        if not agolitem['description']:            
            report['desctiption'] = agolitem['description']
        if not agolitem['thumbnail']:            
            report['thumbnail'] = agolitem['thumbnail']
        if not agolitem['typeKeywords']:            
            report['typeKeywords'] = agolitem['typeKeywords']
        if not agolitem['accessInformation']:            
            report['accessInfo'] = agolitem['accessInformation']
        if not agolitem['access']:
            report['access'] = agolitem['access']
        #if not agolitem['groupDesignations']:
        #    doesPass = False
        #    report['groups'] = None

        if len(report) > 0:
            report['url'] = agolitem.homepage

        return report

    def setTableThumbnail(self, agolitem):
        tableThumb = r"c:\path2Table\table.png"

        if agolitem.type in ['Microsoft Excel', 'CSV'] or "Table" in agolitem.typeKeywords:
            if agolitem.thumbnail != 'thumbnail/table.png':
                print("Updating thumbnail of {}".format(agolitem.title))
                update = agolitem.update(thumbnail=tableThumb)
                print(update)

        return

    def touchUpdate(self, agolitem):
        ''' Simply touches an item on portal, forcing the 'updated date' to refresh
            This function could be enhanced to accept a metadata payload for metadata edits
         '''
        result = agolitem.update()

        return result


if __name__ == "__main__":

    config = configparser.ConfigParser()

    localPath = sys.path[0]
    configFile  = os.path.join(localPath, "credentials.ini")

    config.read(configFile)
    user = config['auth']['username']
    pword = config['auth']['password']
    portal = config['auth']['agol']

    od = ODManager(user, pword, portal, localPath)

    ''' TEST TEST TEST '''
    gitems = od.listItemsByGroup("OD_Data_FR")
    for pi in gitems:
        print(pi)
