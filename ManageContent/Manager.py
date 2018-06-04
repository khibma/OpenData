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

        enLicense = "URL TO LICENSE"
        frLicense = "URL TO LICENSE"
        enTags = ["environment", "transportation", "parks", "infrastructure", "health", "local gov", "business", "geospatial"]
        frTags = ["environnement", "transport", "parcs", "infrastructure", "santé", "administration municipale", "affaires", "géospatial"]
        
        report = {}

        if lang == "EN":
            if agolitem['licenseInfo'] != enLicense:                
                report['liceseInfo'] = agolitem['licenseInfo']
            if not set([i.lower() for i in agolitem['tags']]).intersection(enTags):                
                report['tags'] = agolitem['tags']

        elif lang == "FR":
            if "NO" in agolitem['title']:                
                report['title'] =agolitem['title']
            if agolitem['licenseInfo'] != frLicense:                                
                report['liceseInfo'] = agolitem['licenseInfo']
            if not set([i.lower() for i in agolitem['tags']]).intersection(frTags):                
                report['tags'] = agolitem['tags']


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

        return report

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
