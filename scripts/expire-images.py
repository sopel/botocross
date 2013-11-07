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

from botocross.ec2 import *
from pprint import pprint
import argparse
import boto
import boto.ec2
import botocross as bc
import logging

# configure command line argument parsing
parser = argparse.ArgumentParser(description='Expire images of EC2 instances in all/some available EC2 regions',
                                 parents=[bc.build_region_parser(), bc.build_filter_parser('EC2 instance'),
                                          bc.build_backup_parser('EC2 instance', True, 1), bc.build_common_parser()])
args = parser.parse_args()

# process common command line arguments
log = logging.getLogger('botocross')
bc.configure_logging(log, args.log_level)
credentials = bc.parse_credentials(args)
regions = bc.filter_regions(boto.ec2.regions(), args.region, args.include_govcloud, args.only_govcloud)
filter = bc.build_filter(args.filter, args.exclude)

# execute business logic
log.info("Expire EC2 images:")

for region in regions:
    try:
        ec2 = boto.connect_ec2(region=region, **credentials)
        # NOTE: Not filtering by id allows expiring images of terminated instances as well.
        reservations = ec2.get_all_instances(filters=filter['filters'])
        if filter['excludes']:
            exclusions = ec2.get_all_instances(filters=filter['excludes'])
            reservations = bc.filter_list_by_attribute(reservations, exclusions, 'id')
        instance_ids = [instance.id for reservation in reservations for instance in reservation.instances]
        num_instances = len(instance_ids)
        if args.resource_ids:
            instance_ids.extend(args.resource_ids)
        print region.name + ": " + str(num_instances) + " instances / " + str(len(instance_ids)) + " instance IDs"
        expire_images(ec2, instance_ids, args.backup_set, args.backup_retention, args.no_origin_safeguard)
    except boto.exception.BotoServerError, e:
        log.error(e.error_message)
