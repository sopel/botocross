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

from pprint import pprint
import argparse
import boto
import boto.ec2
import botocross as bc
import logging

# configure command line argument parsing
parser = argparse.ArgumentParser(description='Describe EBS snapshots in all/some available EC2 regions',
                                 parents=[bc.build_region_parser(), bc.build_filter_parser('EBS snapshots'), bc.build_common_parser()])
args = parser.parse_args()

# process common command line arguments
log = logging.getLogger('botocross')
bc.configure_logging(log, args.log_level)
credentials = bc.parse_credentials(args)
regions = bc.filter_regions(boto.ec2.regions(), args.region)
filter = bc.build_filter(args.filter, args.exclude)
log.info(args.resource_ids)

# execute business logic
log.info("Describing EBS snapshots:")

for region in regions:
    try:
        ec2 = boto.connect_ec2(region=region, **credentials)
        snapshots = ec2.get_all_snapshots(snapshot_ids=args.resource_ids, owner='self', filters=filter['filters'])
        if filter['excludes']:
            exclusions = ec2.get_all_snapshots(owner='self', filters=filter['excludes'])
            snapshots = bc.filter_list_by_attribute(snapshots, exclusions, 'id')
        print region.name + ": " + str(len(snapshots)) + " snapshots"
        for snapshot in snapshots:
            if args.verbose:
                pprint(vars(snapshot))
            else:
                print snapshot.id
    except boto.exception.BotoServerError, e:
        log.error(e.error_message)
