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
from botocross import configure_logging
from botocross.ec2 import *
import logging
log = logging.getLogger('botocross')
from pprint import pprint

# configure command line argument parsing
parser = argparse.ArgumentParser(description='Create snapshots of EBS volumes in all/some available EC2 regions')
parser.add_argument("-f", "--filter", action="append", help="An EBS volume filter. [can be used multiple times]")
parser.add_argument("-i", "--id", dest="resource_ids", action="append", help="An EBS volume id. [can be used multiple times]")
parser.add_argument("-d", "--description", help="A description for the EBS snapshot [default: <provided>]")
parser.add_argument("-bs", "--backup_set", default=DEFAULT_BACKUP_SET, help="A backup set name (determines retention correlation). [default: 'default'")
parser.add_argument("-r", "--region", help="A region substring selector (e.g. 'us-west')")
parser.add_argument("--access_key_id", dest='aws_access_key_id', help="Your AWS Access Key ID")
parser.add_argument("--secret_access_key", dest='aws_secret_access_key', help="Your AWS Secret Access Key")
parser.add_argument("-l", "--log", dest='log_level', default='WARNING',
                    choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                    help="The logging level to use. [default: WARNING]")
args = parser.parse_args()

configure_logging(log, args.log_level)

def isSelected(region):
    return True if region.name.find(args.region) != -1 else False

# execute business logic    
credentials = {'aws_access_key_id': args.aws_access_key_id, 'aws_secret_access_key': args.aws_secret_access_key}
heading = "Snapshotting EBS volumes"
regions = boto.ec2.regions()
if args.region:
    heading += " (filtered by region '" + args.region + "')"
    regions = filter(isSelected, regions)

filters = None
if args.filter:
    filters = dict([filter.split('=') for filter in args.filter])
log.info(args.filter)
log.debug(filters)
log.info(args.resource_ids)

backup_set = args.backup_set if args.backup_set else DEFAULT_BACKUP_SET
log.debug(backup_set)

print heading + ":"
for region in regions:
    try:
        ec2 = boto.connect_ec2(region=region, **credentials)
        volumes = ec2.get_all_volumes(volume_ids=args.resource_ids, filters=filters)
        print region.name + ": " + str(len(volumes)) + " volumes"
        create_snapshots(ec2, volumes, backup_set, args.description)
    except boto.exception.BotoServerError, e:
        log.error(e.error_message)
