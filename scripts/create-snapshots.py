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
import sys

# configure command line argument parsing
parser = argparse.ArgumentParser(description='Create snapshots of EBS volumes in all/some available EC2 regions',
                                 parents=[bc.build_region_parser(), bc.build_filter_parser('EBS volume'),
                                          bc.build_backup_parser('EBS volume'), bc.build_common_parser()])
args = parser.parse_args()

# process common command line arguments
log = logging.getLogger('botocross')
bc.configure_logging(log, args.log_level)
credentials = bc.parse_credentials(args)
regions = bc.filter_regions(boto.ec2.regions(), args.region)
filter = bc.build_filter(args.filter, args.exclude)

# execute business logic
log.info("Snapshotting EBS volumes:")

# REVIEW: For backup purposes it seems reasonable to only consider all OK vs. FAIL?!
exit_code = bc.ExitCodes.OK
for region in regions:
    try:
        ec2 = boto.connect_ec2(region=region, **credentials)
        volumes = ec2.get_all_volumes(volume_ids=args.resource_ids, filters=filter['filters'])
        if filter['excludes']:
            exclusions = ec2.get_all_volumes(filters=filter['excludes'])
            volumes = bc.filter_list_by_attribute(volumes, exclusions, 'id')

        print region.name + ": " + str(len(volumes)) + " volumes"
        snapshots = create_snapshots(ec2, volumes, args.backup_set, args.description)

        if args.backup_timeout:
            try:
                states = await_snapshots(ec2, snapshots, timeout=args.backup_timeout)
                if not bc.ec2.SNAPSHOT_STATES_SUCCEEDED.issuperset(states):
                    message = "FAILED to create some snapshots: {0}!".format(format_states(states))
                    log.error(message)
                    exit_code = bc.ExitCodes.FAIL
            except bc.BotocrossAwaitTimeoutError, e:
                log.error(e.message)
                exit_code = bc.ExitCodes.FAIL

        if args.backup_retention:
            volume_ids = [volume.id for volume in volumes]
            expire_snapshots(ec2, volume_ids, args.backup_set, args.backup_retention, args.no_origin_safeguard)

    except boto.exception.BotoServerError, e:
        log.error(e.error_message)
        exit_code = bc.ExitCodes.FAIL

sys.exit(exit_code)
