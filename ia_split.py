import xml.etree.ElementTree as ET      # To read the TOC and other xml files
import glob                             # To get lists of files from folders
from subprocess import call             # To tar and untar files
import shutil
import csv_to_mods
import csv
import codecs

def move_file(orig,dest):
    """ orgi->(string) path of the file to move
        dest->(string) destination path (including filename)

        Wrapper for shutil move. Probably unnecessary"""

    shutil.move(orig,dest)

def rename_file(old,new):
    """old->(String) path to file (including filename duh)
       new->(String) path to new file (including new filename)
       
       This is just using the move command to rename the file."""

    shutil.move(old,new)

def untarball(tarfile, dest):
    """tarfile->(String) path to tarfile to be uncompressed
       dest->(String) folder path to uncompress tar into

       Uncompresses a tarfile of the .tar variety using the -xzf flag.
       The dest path will be created if it does not exist."""

    call(['mkdir','-p',dest])
    call(['tar','-xvf',tarfile,"-C",dest])

def get_tarname(path):
    """path->(String) directory path 
        
        Gets the full path of the first tarfile in the directory with .tar extension"""

    return glob.glob(path+"/*.tar")[0]

def get_scandata(path):
    """path->(String)
       
        Gets the full pathof a file *scandata.xml in the directory"""

    return glob.glob(path+"/*scandata.xml")[0]

def move_toc(start,finish):
    """start->(String) path to starting directory with TOC files to move out
       finish->(String) path to put TOC files in

       move all of the TOC files from a folder to another fold"""

    for f in glob.glob(start+"*TOC*"):
        move_file(f,finish+f.split("/")[-1])

def create_dest_folders(name,range_start,range_end,padding):
    """name->(String) full path of folders to create minus the numbering
       range_start->(int) first number in folder naming range
       range_end->(int) the end of the range of folder naming
       padding->(int) size of zero padding in the name, ex 4 -> XXXX so 0023

        create a series of folders with nameXXX
        Range_start inclusive, range_end exclusive
        padding is zero padding on the number
        ex. 001 is 3, 0001 is 4...etc

        returns the list of folders created"""

    number_format = "%0"+str(padding)+"d"
    folders = []
    for a in range(range_start,range_end):
        call(['mkdir','-p',name+number_format%(a)])
        folders.append(name+number_format%(a))
    return folders

def new_folders(dest,names):
    """dest->(String) destination folder for the new folders to reside in
       names->(list(string)) list of folder names to make

       create a bunch of directories in dest using names"""

    for name in names:
       call(['mkdir','-p',dest+"/"+name]) 

def create_mods_file(xmltree,folder):
    """xmltree->(ElementTree) modsfile element tree
       folder->(String) path to folder where MODS file will be written
       
        Generates a MODS.xml file in the specified folder from the given xmltree """

    tree = ET.ElementTree()
    if(type(xmltree) != type(tree)):
        tree._setroot(xmltree)
        tree.write(folder+"/MODS.xml")
    else:
        xmltree.write(folder+"/MODS.xml")

def make_folder_into_compound(folder,destination,scandata,toc,metapath,ext=".jp2"):
    """folder->(String) path to folder containing files to make into compounds
       destination->(String) path to folder where compounds will be made
       scandata->(String) path to scandata file containing leaf nums and menu splitting
       toc->(String) path to table of contents text file
       (OPT)ext->(String) file extension for files to split into compound
        
        Turn a folder containing ext type files
        folder -> files
        into
        folder->firstchild->OBJ.jp2,secondchild->OBJ.jp2
        according to the islandor compound batch tool
        with mods files generated as well
        """

    files = glob.glob(folder+"/*"+ext) # Get list of files of the specified type in the folder
    padding = len(str(len(files))) # This makes sure that they will be ordered

    leafNums = scandata_leafnums(scandata)
    date = scan_date(scandata)
    
    identifiers = []
    for entry in toc:
        if len(entry) > 1:
            identifiers.append(entry)

    for a in range(0,len(leafNums)):
        identifier = identifiers[a]
        folders = create_dest_folders(destination+"/"+identifier+"/"+identifier+"_child_",0,len(leafNums[a]),padding) # Create dest folders

        for b in range(0,len(folders)):
            move_file(files[leafNums[a][b]],folders[b]+"/OBJ.jp2") # Move and rename the files into their respective folder
            modfile = generate_mods(metapath,identifier,folders[b]+"/MODS.xml",date)
        copy_file(folders[0]+"/MODS.xml",destination+"/"+identifier+"/MODS.xml")

def scandata_leafnums(scandata):
    """scandata->(String) path to scandata file 
        
       returns a nested list in the form [[1,2,3],[4,5]] etc
       Goes through a scandata file and make a nested list of leaf nums.
       New menus split on "Chapter" pagetype and only "Normal" and "Chapter" pagetypes are added"""

    leafnums = []
    tree = ET.parse(scandata)
    root = tree.getroot()
    tmp = []
    for item in root.iter('page'): 
        if(item.find("pageType").text == "Chapter"):
            if(len(tmp) != 0):
                leafnums.append(tmp)
            tmp = []
        if(item.find("pageType").text == "Chapter" or item.find("pageType").text == "Normal"):
            tmp.append(int(item.attrib['leafNum']))
    if(len(tmp) != 0):
        leafnums.append(tmp)
    return leafnums

def copy_file(start,finish):
    """ start->(string) start path of file
        finish->(string) finish path of file
        
        Wrapper for shutil copy"""

    shutil.copy(start,finish) 

def generate_mods(metapath,identifier,dest,date):
    """metapath->(String) path to directory contating meta data files
       indentifier->(String) Identifier to be made into a mod file
       dest->(String) Destination path of folder for MODS.xml file to be put into
       date->(String) Scan date for batch

       generate a MODS.xml file from a csv meta data file for a given identifier"""

    files = glob.glob(metapath+"*.csv") # Get list of files in the directory given
    for f in files: # lets look at the all the files
        key = []
        reader = csv.reader(codecs.open(f,encoding="utf-8"))
        for row in reader:
            if len(key) == 0:
                key = row
            else:
                if(identifier in row):
                    csv_to_mods.csv_row_to_mods(row,key,dest,date)
                    return 
    
def get_toc(path,boxid):
    """path->(String) path to directory containing table of contents
       boxid->(String) box id for group of scans (also filename of TOC file)

       returns list of identifiers for the given box""" 
    
    toc = []
    path = path.rstrip("/")
    with open(path+"/"+boxid+"_TOC.txt") as f:
        for line in f:
            toc.append(line.rstrip("\n"))
    return toc

def scan_date(scandata):
    """scandata->(String) path to scandata file

       YYYY-MM-DD
       returns a string of the date from the scandata file"""


    tree = ET.parse(scandata)
    root = tree.getroot()
    for item in root.iter('scanLog'): 
        scanevent = item.find("scanEvent")
        endTimeStamp = scanevent.find("endTimeStamp")
        date = endTimeStamp.text
        return("%s-%s-%s"%(date[:4],date[4:6],date[6:8]))

if __name__ == "__main__":
    
#    split_by_chapter("eightconceptsofb00gilb/eightconceptsofb00gilb_scandata.xml")
    
# untarball("testarchive/testarchive.tar","newarchive")
#    split_into_folders("testarchive/testarchive.tar","TOC.xml","newarchive")
#    move_file("testarchive/testfile.txt","newarchive")

#    create_dest_folders("/Users/armst179/workspace/internetarchive_scripts/bleh",0,11,0)

# make_folder_into_compound("newarchive")

#    new_folders("blergfolder/",['glergfolder'])

#    root = ET.Element("blerg")
#    create_mods_file(root,"newarchive")

#print(find_mods("MODS/",""))

#print scandata_leafnums("spiller_006-1-4-3-21_scandata.xml")

    pass
    
