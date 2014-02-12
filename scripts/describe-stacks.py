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
import boto.cloudformation
import botocross as bc
import logging

# configure command line argument parsing
parser = argparse.ArgumentParser(description='Describe CloudFormation stacks in all/some available CloudFormation regions',
                                 parents=[bc.build_region_parser(), bc.build_common_parser()])
parser.add_argument("-s", "--stack_name_or_id", default='', help="Name or id (ARN) of stack to describe")
parser.add_argument("--xml", action='store_true', help="Return result as XML")
args = parser.parse_args()

# process common command line arguments
log = logging.getLogger('botocross')
bc.configure_logging(log, args.log_level)
credentials = bc.parse_credentials(args)
regions = bc.filter_regions(boto.cloudformation.regions(), args.region)

# execute business logic
log.info("Describing CloudFormation stacks:")

if args.xml:
    print "<describe-stacks>"
for region in regions:
    if args.xml:
        print "<region name='" + region.name + "'>"
    else:
        pprint(region.name, indent=2)
    try:
        cfn = boto.connect_cloudformation(region=region, **credentials)
        stacks = cfn.describe_stacks(args.stack_name_or_id)

        for stack in stacks:
            if not args.xml:
                print stack.stack_name
            if args.xml:
                print stack.connection._pool.host_to_pool.values()[0].queue[0][0]._HTTPConnection__response._cached_response.replace("xmlns=\"http://cloudformation.amazonaws.com/doc/2010-05-15/\"", "")
            if args.verbose:
                pprint(vars(stack), indent=2)
            log.debug(vars(stack))
    except boto.exception.BotoServerError, e:
        log.error(e.error_message)
    if args.xml:
        print "</region>"
if args.xml:
    print "</describe-stacks>"
