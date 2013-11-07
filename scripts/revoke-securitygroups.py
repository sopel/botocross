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

# TODO: enable cross account usage via src_security_group_owner_id?
def revokeSource():
    ec2.revoke_security_group(group_name=args.name, group_id=args.id, ip_protocol=args.ip_protocol,
                                 from_port=args.from_port, to_port=args.to_port,
                                 src_security_group_name=args.security_group_name, src_security_group_group_id=args.security_group_id)

def revokeIp():
    ec2.revoke_security_group(group_name=args.name, group_id=args.id, ip_protocol=args.ip_protocol,
                                 from_port=args.from_port, to_port=args.to_port, cidr_ip=args.cidr_ip)

# configure command line argument parsing
parser = argparse.ArgumentParser(description='Remove an existing rule from an existing security group in all/some available EC2 regions',
                                 parents=[bc.build_region_parser(), bc.build_common_parser()])
target_group = parser.add_mutually_exclusive_group(required=True)
target_group.add_argument("-n", "--name", help="The security group name")
target_group.add_argument("-i", "--id", help="The security group id (required in VPC)")
parser.add_argument("--ip_protocol", choices=['tcp', 'udp', 'icmp'], required=True, help="The IP protocol you are enabling")
parser.add_argument("--from_port", type=int, required=True, help="The beginning port number you are enabling")
parser.add_argument("--to_port", type=int, required=True, help="The ending port number you are enabling")
# sub-commands
subparsers = parser.add_subparsers(title='sub-commands', help='All available sub-commands')
# sub-command 'source'
parser_source = subparsers.add_parser('group', help='Authorize by security group')
source_group = parser_source.add_mutually_exclusive_group(required=True)
source_group.add_argument("--security_group_name", help="The name of the security group you are granting access to")
source_group.add_argument("--security_group_id", help="The id of the security group you are granting access to")
# parser_source.add_argument("--security_group_owner_id", required=True, help="The ID of the owner of the security group you are granting access to")
parser_source.set_defaults(func=revokeSource)
# sub-command 'ip'
parser_ip = subparsers.add_parser('cidr', help='Authorize by CIDR address')
parser_ip.add_argument("--cidr_ip", required=True, help="The CIDR block you are providing access to")
parser_ip.set_defaults(func=revokeIp)
args = parser.parse_args()

# process common command line arguments
log = logging.getLogger('botocross')
bc.configure_logging(log, args.log_level)
credentials = bc.parse_credentials(args)
regions = bc.filter_regions(boto.ec2.regions(), args.region, args.include_govcloud, args.only_govcloud)

# execute business logic
group_name = args.name if args.name else ""
group_id = args.id if args.id else ""
log.info("Revoking EC2 security groups '" + group_name + group_id + "':")

groupnames = [args.name] if args.name else None
group_ids = [args.id] if args.id else None

for region in regions:
    pprint(region.name, indent=2)
    try:
        ec2 = boto.connect_ec2(region=region, **credentials)
        args.func()
    except boto.exception.BotoServerError, e:
        log.error(e.error_message )
