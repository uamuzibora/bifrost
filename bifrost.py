#!/usr/bin/env python

import sys
from sys import stderr
import getopt
import boto.ec2
import os
from github import Github
import time
from string import Template

# Make sure these are set correctly
username = "kenners" # your GitHub username
sshKeyPath = "~/.ssh/UamuziBora.pem" # Path to wherever you put the UmauziBora.pem key
repoName = "nafasi" # Repo name on GH
orgName = "uamuzibora" # Organisation that owns the repo
awsKeyPair = "UamuziBora"
# Do not change these!
conn = None
ami = "ami-eb76739f" # The AMI ID of our base instance on EC2
dbRootPassword = "Out6Of7Africa42" # Password for root MySQL user on EC2 instance

def usage():
    print >>stderr, """Usage: bifrost [--start] [--stop] [--list] [--dump] [--ssh]"""
    sys.exit()

def activeInstances(label_tag, filters):
    """Returns a list of all EC2 instances specified by <filters> arguments, listed by <label_tag>"""
    instances = []
    kwargs = {}
    if filters:
        kwargs['filters'] = filters
    conn = connectEC2()
    reservations = conn.get_all_instances(**kwargs)
    for reservation in reservations:
        for instance in reservation.instances:
            instance_name = instance.tags.get(label_tag)
            if instance.public_dns_name:
                pair = (instance_name, instance.public_dns_name)
                instances.append(pair)
    return instances

def findMyInstances(user):
    """Returns a list of all EC2 instances with the 'Owner' tag specified by <user>"""
    conn = connectEC2()
    filters = {}
    filters['tag:Project'] = "UB"
    filters['tag:Owner'] =  username
    instances = activeInstances('Name', filters)
    return instances


def connectEC2():
    """Establishs Boto connection with eu-west-1"""
    regions = boto.ec2.regions()
    eu = regions[0]
    conn = eu.connect()
    return conn
    
def main():
    
    # Parse arguments with getopt
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hldmSs:", ["help", "list", "dump", "ssh", "stop", "start="])
    except getopt.GetoptError, err:
        print >>stderr, err
        usage()
        sys.exit(2)
        
    # Check that we've only got one argument    
    if not opts or len(opts) > 1:
        print >>stderr, "Error: none or more than one arguments given"
        sys.exit(2)
    
    aws_key = os.environ.get("AWS_ACCESS_KEY_ID")
    aws_secret = os.environ.get("AWS_ACCESS_KEY_ID")
    
    # Check that we've got our AWS credentials
    if not aws_key or not aws_secret:
        if not aws_key:
            print >>stderr, "AWS_ACCESS_KEY_ID not set in environment"
        if not aws_secret:
            print >>stderr, "AWS_SECRET_ACCESS_KEY not set in environment"
        sys.exit(2)
    
    # Perform the requested actions
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            # Help
            usage()
            sys.exit()
        elif opt in ("-l", "--list"):
            # List all UB instances
            instances = findMyInstances(username)
            if len(instances) == 0:
                print "You have no UB instances running on EC2."
                sys.exit()
            else:
                for pair in sorted(instances, key=lambda p: p[0]):
                    print "%s\t%s" % pair
                sys.exit()
        elif opt in ("-d", "--dump"):
            # Dump MySQL db and SCP it to the current working directory
            instances = findMyInstances(username)
            if len(instances) == 0:
                print >>stderr, "You have no running UB instances on EC2 to connect to."
                sys.exit(2)
            elif len(instances) > 1:
                print >>stderr, "You have >1 running UB instances on EC2 - I don't know which one to connect to. Please kill excess instances."
                sys.exit(2)
            else:
                if os.path.exists(os.getcwd() + '/openmrs.sql'):
                    print >>stderr, "Error: Can't 'openmrs.sql' already exists in your current directory. Aborting."
                    sys.exit(2)
                else:
                    try:
                        os.system('ssh -i ' + sshKeyPath + ' ubuntu@' + instances[0][1] + ' "mysqldump -u root --password=' + dbRootPassword + ' --compact --single-transaction --order-by-primary openmrs > /tmp/openmrs.sql"')
                    except Exception, err:
                        print >>stderr, err
                        sys.exit(2)
                    try:
                        os.system('scp -i ' + sshKeyPath + ' ubuntu@' + instances[0][1] + ':/tmp/openmrs.sql .')
                    except Exception, err:
                        print >>stderr, err
                        sys.exit(2)
            sys.exit()
        elif opt in ("-m", "--ssh"):
            # Open SSH connection to host
            instances = findMyInstances(username)
            if len(instances) == 0:
                print >>stderr, "You have no running UB instances on EC2 to connect to."
                sys.exit(2)
            elif len(instances) > 1:
                print >>stderr, "You have >1 running UB instances on EC2 - I don't know which one to connect to. Please kill excess instances."
                sys.exit(2)
            else:
                try:
                    os.system('ssh -i ' + sshKeyPath + ' ubuntu@' + instances[0][1])
                except Exception, err:
                    print >>stderr, err
                    sys.exit(2)
            sys.exit()
        elif opt in ("-s", "--start"):
            # Housekeeping to interface with GitHub
            commitId = arg
            commitExists = False
            hub = Github()
            repo = hub.get_organization(orgName).get_repo(repoName)
            
            # Grab all the commits
            print "Indexing commits on GitHub..."
            repoCommits = repo.get_commits()
            
            # Find out if we're deploying HEAD or a specified commit
            if not commitId or commitId.lower() == 'head':
                # Set commitId to be the *actual* sha1 hash rather than head
                print "Finding SHA1 hash for HEAD on dev..."
                commitId = repo.get_git_ref("refs/heads/dev").object['sha']
                print "Found: HEAD on dev is " + commitId
            if len(commitId) < 7:
            	print >>stderr, "Error: Commit ID < 7 characters. You must specify 'HEAD' or at least the first 7 digits of the SHA1 commit ID hash in order to launch an instance."
                sys.exit(2)
            # Find if the specified commit id actually exists
            print "Checking to see if commit " + commitId + " exists on GitHub..."
            for commit in repoCommits:
                if commit.sha == commitId:
                    commitExists = True
                    break
                # What about if we're using a short sha1 hash (i.e. first 7 characters)
                elif commit.sha[:7] == commitId[:7]:
                    commitExists = True
                    # And now that we've found a commit, let's set our commitId to be the full length one
                    commitId = commit.sha
                    break
            # Quit if we can't find our commit on GitHub
            if commitExists is False:
                print >>stderr, "Error: Commit is not found on GitHub. Have you pushed your commit?"
                sys.exit(2)
            print "Found commit " + commitId + " on GitHub"
            # Ok, now lets boot the EC2 image, pull this commit into the EC2 image and deploy it onto Tomcat
            print "Creating new EC2 instance based on " + ami
            conn = connectEC2()
            # Let's get our bootstrap.sh script to pass into user_data
            try:
                bootstrap = open('bootstrap.sh', 'r')
            except IOError:
                    print >>stderr, "Error: cannot open bootstrap.sh"
                    exit(2)
            # Parse bootstrap.sh to add in our commit id and db root password for this instance
            userdata = Template(bootstrap.read()).substitute(py_commit_id=commitId, py_db_root_password=dbRootPassword)
            # Now create our instance
            reservation = conn.run_instances(image_id=ami, \
            key_name=awsKeyPair, \
            security_groups=["UBOpenMRS"], \
            instance_type="t1.micro", \
            instance_initiated_shutdown_behavior="terminate",
            user_data=userdata)
            instance = reservation.instances[0]
            # Tag our new instance appropriately
            print "New instance is " + instance.id
            print "Tagging new instance with Name: " + commitId[:7] + ", Owner: " + username + ", Project: UB"
            conn.create_tags([instance.id], {"Name": commitId[:7], "Owner": username, "Project": "UB"})
            # Loop until instance booted
            print "Waiting for instance to finish booting..."
            while instance.update() == 'pending':
            	print "."
                time.sleep(2)
            if instance.state == 'running':
            	print "Instance " + instance.id + " (" + commitId[:7] +") is running. Public DNS is " + instance.public_dns_name
            else:
                print >>stderr, "Error: Unexpected instance state: " + instance.state
                sys.exit(2)
            sys.exit()
        elif opt in ("-S", "--stop"):
            # Stop the all the instances belonging to you
            instances = findMyInstances(username)
            if len(instances) == 0:
                print "You have no running UB instances on EC2."
                sys.exit()
            else:
                print "You have the following UB instances running on EC2:"
                for pair in sorted(instances, key=lambda p: p[0]):
                    print "%s\t%s" % pair
                print "Terminating the above instances..."
                conn = connectEC2()
                kwargs = {}
                filters = {}
                filters['tag:Project'] = "UB"
                filters['tag:Owner'] =  username
                kwargs['filters'] = filters
                conn.terminate_instances([reservation.instances[0].id for reservation in conn.get_all_instances(**kwargs)])
            sys.exit()
        else:
            print >>stderr, "Unrecognised option or argument."
            usage()
            sys.exit(2)
            
if __name__ == "__main__":
    main()