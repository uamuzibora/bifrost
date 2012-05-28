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
    print >>stderr, """Usage: bifrost [--start COMMIT] [--stop COMMIT] [--list] [--dump COMMIT] [--ssh COMMIT]"""
    sys.exit()

def activeInstances(label_tag, filters):
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
        print >>sys.stderr, err
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
            print >>sys.stderror, "AWS_ACCESS_KEY_ID not set in environment"
        if not aws_secret:
            print >>sys.stderror, "AWS_SECRET_ACCESS_KEY not set in environment"
        sys.exit(2)
    
    # Perform the requested actions
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-l", "--list"):
            # List all UB instances
            filters = {}
            filters['tag:Project'] = "UB" 
            instances = activeInstances('Project', filters)
            numinstances = len(instances)
            if numinstances == 1:
                print instances[0][1]
                sys.exit()
            elif numinstances == 0  or numinstances > 1:
                for pair in sorted(instances, key=lambda p: p[0]):
                    print "%s\t%s" % pair
                sys.exit()
        elif opt in ("-d", "--dump") and len(arg) == 7:
            # Perform MySQL dump and SCP it to the current working directory
            sys.exit()
        elif opt in ("-m", "--ssh") and len(arg) == 7:
            # Open SSH connection to host
            sys.exit()
        elif opt in ("-s", "--start") and len(arg) == 7:
            # Check are deploy the specified commit
            sys.exit()
        elif opt in ("-S", "--stop") and len(arg) == 7:
            # Stop the specified instance
            sys.exit()
        else:
            print >>stderr, "Unrecognised option or argument."
            usage()
            sys.exit(2)
            
if __name__ == "__main__":
    main()