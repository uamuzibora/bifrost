#!/usr/bin/env python

import sys
from sys import stderr
import getopt
import boto.ec2
import os
import git

# Make sure these are set correctly
username = "kenrick" # i.e. your firstname
sshKeyPath = "~/.ssh/UamuziBora.pem" # Path to wherever you put the UmauziBora.pem key
nafasiPath = "~/Documents/Projects/UamuziBora/Code/nafasi" # Path to your local repo of Nafasi

# Do not change these!
conn = None
ami = "ami-7b93a90f" # The AMI ID of our base instance on EC2
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
        opts, args = getopt.getopt(sys.argv[1:], "hld:m:s:S:", ["help", "list", "dump=", "ssh=", "start=", "stop="])
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
            # Check are deploy the specified commit
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