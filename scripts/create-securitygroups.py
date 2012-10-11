#!/usr/bin/env python
# Copyright (c) 2012 Steffen Opel http://opelbrothers.net/
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish, dis-
# tribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the fol-
# lowing conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABIL-
# ITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
# SHALL THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

import argparse
import boto
import boto.ec2
from pprint import pprint

# configure command line argument parsing
parser = argparse.ArgumentParser(description='Create a EC2 security group in all/some available EC2 regions')
parser.add_argument("group", help="A group name")
parser.add_argument("-d", "--description", help="Override the groups description [default: group name + 'security group']")
parser.add_argument("--vpc_id", help="The ID of the VPC to create the security group in, if any.")
parser.add_argument("-r", "--region", help="A region substring selector (e.g. 'us-west')")
parser.add_argument("--access_key_id", dest='aws_access_key_id', help="Your AWS Access Key ID")
parser.add_argument("--secret_access_key", dest='aws_secret_access_key', help="Your AWS Secret Access Key")
args = parser.parse_args()

credentials = {'aws_access_key_id': args.aws_access_key_id, 'aws_secret_access_key': args.aws_secret_access_key}

def isSelected(region):
    return True if region.name.find(args.region) != -1 else False

# execute business logic
heading = "Creating EC2 security groups named '" + args.group + "'"
regions = boto.ec2.regions()
if args.region:
    heading += " (filtered by region '" + args.region + "')"
    regions = filter(isSelected, regions)

description = args.description if args.description else args.group + " security group"

print heading + ":"
for region in regions:
    pprint(region.name, indent=2)
    try:
        ec2 = boto.connect_ec2(region=region, **credentials)
        print 'Creating security group ' + args.group
        group = ec2.create_security_group(args.group, description=description, vpc_id=args.vpc_id)
        print('... group ID is ' + group.id)
    except boto.exception.BotoServerError, e:
        print e.error_message
