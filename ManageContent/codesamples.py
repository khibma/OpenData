'''
    Code snippets to help manage items in ArGIS.COM/Portal.
    Calls Manager.py  
    Authenication through the `credentials.ini` file
    Requirements: Python 3+, ArcGIS Python API
    Date: May 30, 2018
'''

from Manager import ODManager
import configparser
import os, sys, json

config = configparser.ConfigParser()

localPath = sys.path[0]
configFile  = os.path.join(localPath, "credentials.ini")

config.read(configFile)
user = config['auth']['username']
pword = config['auth']['password']
portal = config['auth']['agol']

od = ODManager(user, pword, portal, localPath)


# Get and display all groups
grps = od.findGroups()
for g in grps:
    print("{} ({}) - {}".format(g.title, len(g.content()), g.id)) 

# Save all the groups from the logged in user to a CSV
csv = od.findGroups(localPath)


# List all the items in a folder
foldItems  =od.listItemsByFolder("Unnecessary")
print("{} items in {}".format(len(foldItems), "Unnecessary"))
print("Title, ItemURL, ServerURL")
for fi in foldItems:        
    print("{}, {}, {}".format(fi.title, fi.homepage, fi.url))   


# Move items from one folder to another, based on a sistem item existing in a similiar folder.
# Specifically, some ENGLISH items have been moved to "Unnecessary"
#  We need to identify the French items that live in "_stagingFR" and move them to "Unnecessary_FR"
un_en = od.listItemsByFolder("Unnecessary")
urls = [x.url for x in un_en]
stage_fr = od.listItemsByFolder("_stagingFR")
for stg in stage_fr:
    if stg.url in urls:
        stg.move("Unnecessary_FR")


# Find items that exist in a folder and identify the sister items in another folder
# Specifically, items have been vetted into ToBeRevied_EN. We need to identify the list of 
#  matching French items, vet them and eventually get them into a ToBeReviewed_FR folder
print("title, englishurl, frenchurl")
goodEN = od.listItemsByFolder("ToBeReviewed_EN")
urls = [x.url for x in goodEN]
stage_fr = od.listItemsByFolder("_stagingFR")
for stg in stage_fr:
    if stg.url in urls:
        for good in goodEN:
            if stg.url == good.url:
                print("{},{},{}".format(good.title, good.homepage, stg.homepage))
          

# Get the counts of items in a folder and groups.
# We've defined a process that items in a group should match whats in a folder
gitems = od.listItemsByGroup("OD_Data_EN")
fitems = od.listItemsByFolder("Data_EN")
print("{} items in group: {}".format(len(gitems.content()), "OD_Data_EN"))
print("{} items in folder: {}".format(len(fitems), "Data_EN"))

# Find and report items that exist in the Public groups, but are not shared publicly.
# IE. An item should not be shared to the group until its ready to go public. Why is it there?
gitems = od.listItemsByGroup("OD_Data_FR")
gcontent = gitems.content()
print("{} items found in group".format(len(gcontent)))
print("Following items are NOT public:")
for itm in gcontent:
    if itm.access != "public":
        print("  {} : {}".format(itm.title, itm.access))    


# Perform a metadata audit by all items in a folder.
# If the item does not have a value, its report as a failure.
auditItems = od.listItemsByFolder("ToBeReviewed_EN")
for ai in auditItems:
    success, report = od.audit(ai, True)
    if not success:
        print("{} : {}".format(ai['title'], report))
print("Audit: {} services".format(len(auditItems)))

