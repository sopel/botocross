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
parser = argparse.ArgumentParser(description='Delete a EC2 security group in all/some available EC2 regions',
                                 parents=[bc.build_region_parser(), bc.build_common_parser()])
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("-n", "--name", help="The security group name")
group.add_argument("-i", "--id", help="The security group id (required in VPC)")
parser.add_argument("-f", "--force", action="store_true", help="Delete security groups even when assigned to instances.")
args = parser.parse_args()

# process common command line arguments
log = logging.getLogger('botocross')
bc.configure_logging(log, args.log_level)
credentials = bc.parse_credentials(args)
regions = bc.filter_regions(boto.ec2.regions(), args.region, args.include_govcloud, args.only_govcloud)

# execute business logic
groupname = args.name if args.name else ""
group_id = args.id if args.id else ""
log.info("Deleting EC2 security groups '" + groupname + group_id + "':")

groupnames = [args.name] if args.name else None
group_ids = [args.id] if args.id else None

for region in regions:
    pprint(region.name, indent=2)
    try:
        ec2 = boto.connect_ec2(region=region, **credentials)
        groups = ec2.get_all_security_groups(groupnames=groupnames, group_ids=group_ids)
        for group in groups:
            num_instances = " with " + str(len(group.instances())) + " instances assigned" if len(group.instances()) else ""
            if group.instances() and not args.force:
                print 'NOT deleting security group ' + group.name + "(" + group.id + ")" + num_instances + " (use --force to override)"
            else:
                print 'Deleting security group ' + group.name + "(" + group.id + ")" + num_instances
                ec2.delete_security_group(name=args.name, group_id=args.id)
    except boto.exception.BotoServerError, e:
        log.error(e.error_message )
