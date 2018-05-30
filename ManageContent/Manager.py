from arcgis.gis import GIS
#from arcgis.gis import server
import configparser
import os
import csv
import sys

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

    def audit(self, agolitem, strict=False):

        doesPass = True
        report = {}
        if strict:
            if not agolitem['title']:
                doesPass = False 
                report['title'] =agolitem['title']
            if not agolitem['description']:
                doesPass = False 
                report['desctiption'] = agolitem['description']
            if not agolitem['thumbnail']:
                doesPass = False 
                report['thumbnail'] = agolitem['thumbnail']
            if not agolitem['licenseInfo']:
                doesPass = False 
                report['liceseInfo'] = agolitem['licenseInfo']
            if not agolitem['typeKeywords']:
                doesPass = False 
                report['typeKeywords'] = agolitem['typeKeywords']
            if not agolitem['tags']:
                doesPass = False
                report['tags'] = agolitem['tags']
            if not agolitem['accessInformation']:
                doesPass = False 
                report['accessInfo'] = agolitem['accessInformation']
            if not agolitem['access']:
                doesPass = False 
                report['access'] = agolitem['access']
            #if not agolitem['groupDesignations']:
            #    doesPass = False
            #    report['groups'] = None

        return doesPass, report

    def touchUpdate(self, agolitem):
        ''' Simply touches an item on portal, forcing the 'updated date' to refresh '''

        agolitem.update()

        return


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
