'''
    Code snippets to help manage items in ArGIS.COM/Portal.
    Calls Manager.py  
    Authentication through the `credentials.ini` file
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


# Get and display all folders
for f in od.folders:
    print("{} - {}".format(f['title'], f['id']))

# Get and display all groups
grps = od.findGroups()
for g in grps:
    print("{} ({}) - {}".format(g.title, len(g.content()), g.id)) 

# Save all the groups from the logged in user to a CSV
csv = od.findGroups(localPath)


# List all the items in a folder
foldItems = od.listItemsByFolder("Unnecessary")
print("{} items in {}".format(len(foldItems), "Unnecessary"))
print("Title, ItemURL, ServerURL")
for fi in foldItems:        
    print("{}, {}, {}".format(fi.title, fi.homepage, fi.url))   


# Move items from one folder to another, based on a sister item existing in a similiar folder.
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
auditItems = od.listItemsByFolder("Ready_EN")
for ai in auditItems:
    report = od.audit(ai, "EN")
    if report:
        print("{} : {}".format(ai['title'], report))
print("Audit: {} services".format(len(auditItems))) 


# Update an item
# This sample grabs the first item in the given folder and simply touches it. The modified date on Portal is updated.
# Logic to update items that have actually had their data updated needs to be applied.
# This function is used as the data powering the ArcGIS Server services is updated without the Portal items knowledge, thus
#  this will be called by the process updating the actual data, so the item's last modified is current.
foldItems = od.listItemsByFolder("Unnecessary")
anItem = foldItems[0]
print("item: {}, created: {}, modified: {}".format(anItem.title, od.convertDate(anItem.created), od.convertDate(anItem.modified)))
updatedItem = od.touchUpdate(anItem)
print(updatedItem)


# French items were found to have been shared to the OD_Data_EN (english) group.
# These items need to be unshared from the English group and Shared to the French group.
# They can be identified by lookin at ALL content in the OD_Data_EN group, then look at
#  the folder they live in. If they live in the FRENCH folder, then we know they must be moved
# Note - the true AGOL IDs have been replaced below. Group.ID and Folder.ID are required
# en folder:  12345fgh - not used
# en group:   abcdefg456
# fr folder:  qwert0987
# fr group:   zzzz123
wrong = od.listItemsByGroup("OD_Data_EN")
for w in wrong.content():
    if w['ownerFolder'] == "qwert0987":
        print(w['title'])
        w.unshare(groups="abcdefg456")
        w.share(groups="zzzz123")


# Move all the items in the "Ready" folder to the final home of Open Data
# Also share items live to the public
itemsToShare = od.listItemsByFolder("Ready_FR")
for i in itemsToShare:
    print(i['title'])
    i.share(everyone=True)
    i.move("Data_FR")
