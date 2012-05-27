#!/usr/bin/env python

import sys
import getopt
import boto.ec2
import os
from sys import stderr

# Make sure these are set correctly
username = "kenrick"
sshKeyPath = "~/.ssh/UamuziBora.pem"

# Do not change these!
region = "eu-west-1"
tag = "Name"
conn = None

def usage():
    print >>stderr, """Usage: bifrost [--start COMMIT] [--stop COMMIT] [--list] [--dump] [--ssh]"""
    sys.exit()

def christen(commit):
    """Creates a name for the new instance"""
    name = username + "-" + commit
    return name

def findInstanceURL(name):
    """Returns the URL of the specified instance"""
    
    return url

def activeInstances(label_tag, filters):
    instances = []
    kwargs = {}
    if filters:
        kwargs['filters'] = filters
    reservations = conn.get_all_instances(**kwargs)
    for reservation in reservations:
        for instance in reservation.instances:
            instance_name = instance.tags.get(label_tag)
            if instance.public_dns_name:
                pair = (instance_name, instance.public_dns_name)
                instances.append(pair)
    return instances

def main():
    # Parse arguments with getopt
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hldm:s:S:", ["help", "list", "dump", "ssh=", "start=", "stop="])
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
    
    region = region and boto.ec2.get_region(region, aws_access_key_id = aws_key, aws_secret_access_key = aws_secret)
    conn = boto.ec2.connection.EC2Connection(aws_key, aws_secret, region = region)
    
    
    # Perform the requested actions
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-l", "--list"):
            # List all UB instances
            sys.exit()
        elif opt in ("-d", "--dump"):
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