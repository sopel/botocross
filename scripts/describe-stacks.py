#!/usr/bin/python
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
import boto.cloudformation
from botocross import configure_logging
import logging
log = logging.getLogger('botocross')
from pprint import pprint

# configure command line argument parsing
parser = argparse.ArgumentParser(description='Describe CloudFormation stacks in all/some available CloudFormation regions')
parser.add_argument("-r", "--region", help="A region substring selector (e.g. 'us-west')")
parser.add_argument("-s", "--stack_name_or_id", default='', help="Name or id (ARN) of stack to describe")
parser.add_argument("--xml", action='store_true', help="Return result as XML")
parser.add_argument("--access_key_id", dest='aws_access_key_id', help="Your AWS Access Key ID")
parser.add_argument("--secret_access_key", dest='aws_secret_access_key', help="Your AWS Secret Access Key")
parser.add_argument("-v", "--verbose", action='store_true') # TODO: drop in favor of a log formatter?!
parser.add_argument("-l", "--log", dest='log_level', default='WARNING',
                    choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                    help="The logging level to use. [default: WARNING]")
args = parser.parse_args()

configure_logging(log, args.log_level)

def isSelected(region):
    return True if region.name.find(args.region) != -1 else False

# execute business logic
credentials = {'aws_access_key_id': args.aws_access_key_id, 'aws_secret_access_key': args.aws_secret_access_key}
heading = "Describing CloudFormation stacks"
regions = boto.cloudformation.regions()
if args.region:
    heading += " (filtered by region '" + args.region + "')"
    regions = filter(isSelected, regions)

if args.xml:
    print "<describe-stacks>"
else:
    print heading + ":"
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
