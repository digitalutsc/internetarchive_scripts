from redmine import Redmine

def create_redmine_issue(username,password,redmine_url,project_id,issue_subject,issue_description,assign_to):
    """Create and save a new issue on redmine
        username ->(String) authentication info for redmine
        password ->(String) authentication info for redmine
        project_id ->(String) name of project
        issue_subject ->(String) issue subject
        issue_description ->(String) description of issue
        assign_to ->(String) id of the person the task is assigned to
      
        Creates a new issue/ticket on redmine for the given information.
       """

    redmine = Redmine(redmine_url,username=username,password=password)
    redmine.issue.create(project_id=project_id,subject=issue_subject,description=issue_subject,assigned_to_id=assign_to)

def download_redmine_file(username,password,redmine_url, file_url,dest_path,file_name=None):
    """username->(String) redmine username
       password->(String) redmine password
       redmine_url->(String) redmine server url
       file_url->(Stirng) url of file
       dest_path->(Stirng) local path for file to be downloaded to
       (OPT)file_name->(String) filename for the file to be downloaded to
        """

    redmine = Redmine(redmine_url,username=username,password=password)
    redmine.Redmine.download(file_url,savepath=dest_path,filename=file_name)

def get_assigned_tickets(username,password,redmine_url,project_id,assignee):
    """username->(Stirng) redmine username
       password->(String) redmine password
       redmine_url->(String) redmine server url
       project_id->(Stirng) id of project to get tickets for
       assignee->(String) name of assignee as appears on redmine (not the username)

       return (list(redmine.issue))
       returns a list of all the tickets currently assigned to the user"""

    redmine = Redmine(redmine_url,username=username,password=password) # connect to redmine
    proj = redmine.project.get(project_id)
    issue_list = []
    for issue in proj.issues:
        if(issue.assigned_to['name'] == assignee and issue.status.__str__() == "Assigned"): # Check assignee and issue status
            issue_list.append(issue)
    return(issue_list)

def download_all_files(username,password,redmine_url,issues,savepath):
    """username->(String) redmine username
       password->(String) redmine password
       redmine_url->(String) server address for redmine
       issues->(list (redmine.issue)) list of redmine issues to download files from
       savepath->(String) path to save the files to
       
       downloads all of the files in each issue provided to the given path"""

    redmine = Redmine(redmine_url,username=username,password=password) # connect to redmine

    for issue in issues:
        for f in issue.attachments:
            redmine.download(f['content_url'],savepath=savepath)

def update_tickets(username,password,redmine_url,issues,statusid):
    """username->(String) redmine username
       password->(String) redmine password
       redmine_url->(String) server address for redmine
       issues->(list(redmine.issue)) list of redmine issues to change the status of
       statusid->(int) status id to change the ticket to 
       
       Change the status of the given issues to the provided statusid
       
       statusid new == 1
       statusid in progress == 2
       statusid resolved == 3
       statusid feedback == 4
       statusid closed == 5
       statusid rejected == 6
       Statusid assigned == 7
       statusid Re-opened == 8

       """

    redmine = Redmine(redmine_url,username=username,password=password) # connect to redmine

    for issue in issues:
        redmine.issue.update(issue.id,status_id=statusid)

def get_pids(username,password,redmine_url,issues):
    """username->(String) redmine username
       password->(Stirng) redmine password
       redmine_url->(String) url of redmine server
       issue->(String) Issue to look in for the namespace

       looks in the description of the given ticket for a line containing:

        boxid=pid

        ex.

        006-1-2-3-4=spiller:XXX
       (spaces get removed, and split on = )
        
       returns a dictionary of boxid,pids
       """

    redmine = Redmine(redmine_url,username=username,password=password) # connect to redmine
    pids = {}
    for issue in issues:
        for line in issue.description.split("\n"):
            if "=" in line:
                line = line.replace(" ","")
                pids[line.split("=")[0]] = line.split("=")[1]    
    return pids

def get_all_tickets(username,password,redmine_url,project_id,assignee):
    """username->(Stirng) redmine username
       password->(String) redmine password
       redmine_url->(String) redmine server url
       project_id->(Stirng) id of project to get tickets for
       assignee->(String) name of assignee as appears on redmine (not the username)

       return (list(redmine.issue))
       returns a list of all the tickets currently assigned to the user"""

    redmine = Redmine(redmine_url,username=username,password=password) # connect to redmine
    proj = redmine.project.get(project_id)
    issue_list = []
    for issue in proj.issues:
        if(issue.assigned_to['name'] == assignee): # Check assignee and issue status
            issue_list.append(issue)
    return(issue_list)

def reassign_tickets(username,password,redmine_url,issues,assignee):
    """username->(String) redmine username
       password->(String) redmine password
       redmine_url->(String) server address for redmine
       issues->(list(redmine.issue)) list of redmine issues to change the status of
       assignee->(int) person id to change the ticket to 
       

       changes the assignee to the given id number
       """

    redmine = Redmine(redmine_url,username=username,password=password) # connect to redmine

    for issue in issues:
        redmine.issue.update(issue.id,assigned_to_id=assignee)

if __name__ == "__main__":

# Password and username input is for testing, I didn't want to leave my password up on github
# Ideally when this is deployed, an external library will be imported with the settings.

    username = input("username:") # Redmine user info
    password = input("password:")
    redmine_url = "https://digitalscholarship.utsc.utoronto.ca/redmine" # Location of redmine 
    proj = 'harley-j-spiller-processing'

    redmine = Redmine(redmine_url,username=username,password=password) # connect to redmine
    redmine.auth()
#    test_proj = redmine.project.get('')

#tickets = get_assigned_tickets(username,password,redmine_url,'kim-pham',"Caden Armstrong")
    tickets = get_assigned_tickets(username,password,redmine_url,proj,"Caden Armstrong")
    pids = get_pids(username,password,redmine_url,tickets)
    print(pids)
    reassign_tickets(username,password,redmine_url,tickets,139)
    update_tickets(username,password,redmine_url,tickets,4)
#download_all_files(username,password,redmine_url,tickets,"/Users/armst179/workspace/internetarchive_scripts/TOC/")
#    update_tickets(username,password,redmine_url,tickets,1)

#    print(test_proj)

#    create_redmine_issue(username,password,redmine_url,'test-project-kim2',"TEST SUBJECT", "TEST DESCRIPTION")

#    projects = redmine.project.all()
#    for proj in projects:
#        print(proj.name)
#        print(proj.identifier)

