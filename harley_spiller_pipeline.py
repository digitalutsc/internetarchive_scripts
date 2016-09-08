# Purpose of this file is to link all of the Internet Archive 
# files together into a pipeline to process the Harley-Spiller 
# collection.
#
#

import ia_getitems, ia_split, ia_redmine, ia_settings
import subprocess
import sys
# **************************
# READ IN VARIABLES
# **************************
config = {}
with open("ia_config.txt") as f:
    for line in f:
       config[line.split("=")[0]] = line.split("=")[1].rstrip("\n")


# **************************
downloaded_path =config['downloaded_path']
preprocess_path =config['preprocess_path']
processed_path =config['processed_path']
tocpath =config['tocpath']
meta_data_path =config['meta_data_path'] 

# **************************
# Download new files from redmine
# **************************
redmine_url = config['redmine_url']
project_id = config['project_id'] 
redmine_name = config['redmine_name']

print("Checking for metadata files")

tickets = ia_redmine.get_assigned_tickets(ia_settings.redmine_username,ia_settings.redmine_password,redmine_url,project_id,redmine_name)
ia_redmine.download_all_files(ia_settings.redmine_username,ia_settings.redmine_password,redmine_url,tickets,meta_data_path)
ia_redmine.update_tickets(ia_settings.redmine_username,ia_settings.redmine_password,redmine_url,tickets,2) # Change to in progress
ia_split.move_toc(meta_data_path,tocpath)

new_pids = ia_redmine.get_pids(ia_settings.redmine_username,ia_settings.redmine_password,redmine_url,tickets)

pid_database = config['pid_db']
old_pids = {}
with open(pid_database) as f:
    for line in f:
        old_pids[line.split("=")[0]]=line.split("=")[1]

old_pids.update(new_pids)

with open(pid_database, "w") as f:
    writestr = ""
    for key,val in old_pids.items():
        writestr += "%s=%s\n"%(key,val)
    f.write(writestr)

# **************************
# CHECK FOR NEW COLLECTIONS
# **************************

collection_id = config['collection_id'] # The collection to watch
collections_db = config['collections_db'] # The text file containing the subcollection (scan boxs, books?) that have already been processed

#TODO uncooment this
#new_collections = ia_getitems.check_for_new_items(ia_settings.ia_username,ia_settings.ia_password,collection_id,collections_db)
new_collections = ['spiller_006-1-4-3-21'] # TODO get rid of this

if (len(new_collections) == 0):
    # No new collections to process!
    sys.exit("No new collections")

ia_split.new_folders(downloaded_path,new_collections) # Prep folders for the download data

# **************************
# DOWNLOAD COLLECTION
# **************************
print("Downloading collection")
dry_run=bool(config['dry_run'])
globs = ['*.tar','*scandata.xml']

for col in new_collections:
    for g in globs:
        ia_getitems.download_collection(ia_settings.ia_username,ia_settings.ia_password,col,downloaded_path,glob=g,dry_run=dry_run) # Download new collections

# **************************
# UNTAR the jp2 archive
# **************************

print("Untar step")
scandatafile = "_scandata.xml" 

ia_split.new_folders(preprocess_path,new_collections) # New folders to uncompress into

for col in new_collections:
    tarfile_name = ia_split.get_tarname(downloaded_path+"/"+col)
    ia_split.untarball(tarfile_name,preprocess_path + col)
    ia_split.move_file(downloaded_path+"/"+col+"/"+col+scandatafile,preprocess_path+"/"+col+"/"+col+scandatafile)

# **************************
# Split the archive into multiple folders and move the jp2 files
# Also generate the MODS files
# **************************

print("Splitting folders and moving files")

ia_split.new_folders(processed_path,new_collections) # New folders to uncompress into
for col in new_collections:
    toc = ia_split.get_toc(tocpath,col.split("_")[1])
    tarfile_name = ia_split.get_tarname(downloaded_path+"/"+col).split("/")[-1]
    scandata = ia_split.get_scandata(preprocess_path+"/"+col)
    ia_split.make_folder_into_compound(preprocess_path+"/"+col+"/"+tarfile_name.rstrip(".tar"),processed_path+"/"+col,scandata,toc,meta_data_path) 


# **************************
# Get pids for ingest location
# **************************
old_pids = {}
with open(pid_database) as f:
    for line in f:
        old_pids[line.split("=")[0]]=line.split("=")[1]


# **************************
# Generate structure.xml
# **************************
print("ISLANDORA REQUIRED PART")

for col in new_collections:
    subprocess.call(['php','create_structure_files.php',processed_path+"/"+col]) #TODO double check this is at the right level

# **************************
# Islandora ingestion
# **************************
islandora_user = config['islandora_user']
islandora_preprocess_path = processed_path
islandora_namespace = config['islandora_namespace']

# Run islandora batch preprocessing
for col in new_collections:
    islandora_parent_pid = old_pids[col.split("_")[1]]    
    subprocess.call(['drush','--v','--user='+islandora_user,'--root=/var/www/drupal','islandora_compound_batch_preprocess','--target='+islandora_preprocess_path+col+"/",'--namespace='+islandora_namespace,'--parent='+islandora_parent_pid])

# Ingest and grab PIDS
ingest_output = subprocess.check_output(['drush','--v','--user='+islandora_user,'--root=/var/www/drupal','islandora_batch_ingest'])
ingest_output = ingest_output.split("\n")
new_objects = []
for line in ingest_output:
    if("Ingested" in line):
        new_objects.append(line.split(" ")[1]) # TODO Check this actually does the thing we want it to

# Get islandora labels for associated PID
labels = []
for pid in new_objects:
    new_label = subprocess.check_output(['./islandora_get_label.drush',pid,'--root=/var/www/drupal'])
    labels.append(new_label.lstrip(".\n"))


# **************************
# Re assign ticket
# **************************

tickets = ia_redmine.get_all_tickets(ia_settings.redmine_username,ia_settings.redmine_password,redmine_url,project_id,redmine_name)
for col in collections:
    localid = col.split("_")[1]
    for ticket in tickets:
        if(localid in ticket.subject or localid in ticket.description):
            ia_redmine.update_tickets(ia_settings.redmine_username,ia_settings.redmine_password,redmine_url,[ticket],4) # Change to feedback
            ia_redmine.reassign_tickets(ia_settings.redmine_username,ia_settings.redmine_password,redmine_url,[ticket],config['qa_id') # Change to feedback to amanda's id
    



# **************************
# Open redmine ticket
# **************************

#issue_subject = config['issue_subject']
#assign_to = config['assign_to']
#issue_description = config['issue_description']
#for a in range(0,len(labels)):
#    issue_description += "new ingested item:" +labels[a]+ "\n"
#ia_redmine.create_redmine_issue(ia_settings.redmine_username,ia_settings.redmine_password,redmine_url,project_id,issue_subject,issue_description,assign_to)
#TODO UNCOMMENT REDMINe ISSUE MAKING
# **************************
# SAVE COLLECTIONS TO DATABASE
# **************************

ia_getitems.add_item_to_db(collections_db,new_collections)

# **************************
# CLEAN UP THE DOWNLOAD AND PROCESS FOLDERS
# **************************

#subprocess.call(['rm','-rf',downloaded_path])
#subprocess.call(['rm','-rf',preprocess_path])
#subprocess.call(['rm','-rf',processed_path])
