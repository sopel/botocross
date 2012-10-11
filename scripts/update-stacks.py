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
import boto.cloudformation
from botocross import configure_logging
import logging
log = logging.getLogger('botocross')
from pprint import pprint

# configure command line argument parsing
parser = argparse.ArgumentParser(description='Create a CloudFormation stack in all/some available CloudFormation regions')
parser.add_argument("stack_name", help="A stack name")
parser.add_argument("template", help="A stack template, either a local file or a S3 URL. Substitutions for {REGION} and {ACCOUNT} are available to support S3 URL construction.")
parser.add_argument("-p", "--parameter", action="append", help="A (key,value) pair for a template input parameter. Substitutions for {REGION} and {ACCOUNT} are available to e.g. support ARN construction. [can be used multiple times]")
parser.add_argument("-n", "--notification_arn", action="append", help="A SNS topic to send Stack event notifications to. Substitutions for {REGION} and {ACCOUNT} are available to e.g. support ARN construction. [can be used multiple times]")
parser.add_argument("-d", "--disable_rollback", action="store_true", help="Indicates whether or not to rollback on failure. [default: false]")
parser.add_argument("-t", "--timeout", type=int, help="Maximum amount of time to let the Stack spend creating itself. If this timeout is exceeded, the Stack will enter the CREATE_FAILED state.")
parser.add_argument("-i", "--enable_iam", action="store_true", help="Enable 'CAPABILITY_IAM'. [default: false]")
#parser.add_argument("-c", "--cababilities", help="The list of capabilities you want to allow in the stack. Currently, the only valid capability is 'CAPABILITY_IAM'")
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

def processParameter(parameter, region_name, account_id):
    replacement = parameter[1].replace('{REGION}', region_name).replace('{ACCOUNT}', account_id)
    processedParameter = tuple([parameter[0], replacement])
    return processedParameter

def processArgument(argument, region_name, account_id):
    return argument.replace('{REGION}', region_name).replace('{ACCOUNT}', account_id)

# execute business logic    
credentials = {'aws_access_key_id': args.aws_access_key_id, 'aws_secret_access_key': args.aws_secret_access_key}
heading = "Updating CloudFormation stacks named '" + args.stack_name + "'"
regions = boto.cloudformation.regions()
if args.region:
    heading += " (filtered by region '" + args.region + "')"
    regions = filter(isSelected, regions)

from botocross.iam.accountinfo import AccountInfo
iam = boto.connect_iam(**credentials)
accountInfo = AccountInfo(iam)
account = accountInfo.describe()

parameters = dict([])
if args.parameter:
    parameters = dict([parameter.split('=') for parameter in args.parameter])

notification_arns = []
if args.notification_arn:
    notification_arns = args.notification_arn

capabilities = []
if args.enable_iam:
    capabilities.append('CAPABILITY_IAM')

print heading + ":"
for region in regions:
    pprint(region.name, indent=2)
    try:
        cfn = boto.connect_cloudformation(region=region, **credentials)
        print 'Updating stack ' + args.stack_name
        processedParameters = dict([processParameter(item, region.name, account.id) for item in parameters.items()])
        processedArns = [processArgument(item, region.name, account.id) for item in notification_arns]
        # Is this a HTTP(S) template?
        if args.template.startswith('http'):
            template_url = processArgument(args.template, region.name, account.id)
            # handle S3 legacy issue regarding region 'US Standard', see e.g. https://forums.aws.amazon.com/message.jspa?messageID=185820  
            if region.name == 'us-east-1':
                template_url = template_url.replace('-us-east-1', '', 1)
            cfn.update_stack(args.stack_name, template_url=template_url, parameters=tuple(processedParameters.items()),
                             notification_arns=processedArns, disable_rollback=args.disable_rollback, timeout_in_minutes=args.timeout, capabilities=capabilities)
        else:
            template_file = open(args.template, 'r')
            template_body = template_file.read()
            cfn.update_stack(args.stack_name, template_body=template_body, parameters=tuple(processedParameters.items()),
                             notification_arns=processedArns, disable_rollback=args.disable_rollback, timeout_in_minutes=args.timeout, capabilities=capabilities)
    except boto.exception.BotoServerError, e:
        log.error(e.error_message)
