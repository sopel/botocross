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
import sys

# configure command line argument parsing
parser = argparse.ArgumentParser(description='Validates a CloudFormation stack template',
                                 parents=[bc.build_region_parser(), bc.build_common_parser()])
parser.add_argument("template", help="A stack template local file or a S3 URL. Substitutions for {REGION} and {ACCOUNT} are available to support S3 URL construction.")
args = parser.parse_args()

# process common command line arguments
log = logging.getLogger('botocross')
bc.configure_logging(log, args.log_level)
credentials = bc.parse_credentials(args)
regions = bc.filter_regions(boto.cloudformation.regions(), args.region, args.include_govcloud, args.only_govcloud)

def processArgument(argument, region_name):
    return argument.replace('{REGION}', region_name)

def printResult(name, template):
    print "Template '" + name + "' is valid."
    if args.verbose:
        print "\rDescription: " + template.description
        print "\rParameters: "
        for parameter in template.template_parameters:
            pprint (vars(parameter), indent=2)

# execute business logic
log.info("Validating CloudFormation template '" + args.template + "':")

try:
    # Is this a HTTP(S) template?
    if args.template.startswith('http'):
        for region in regions:
            pprint(region.name, indent=2)
            cfn = boto.connect_cloudformation(region=region, **credentials)
            template_url = processArgument(args.template, region.name)
            # handle S3 legacy issue regarding region 'US Standard', see e.g. https://forums.aws.amazon.com/message.jspa?messageID=185820
            if region.name == 'us-east-1':
                template_url = template_url.replace('-us-east-1', '', 1)
            template = cfn.validate_template(template_url=template_url)
            printResult(template_url, template)
    else:
        cfn = boto.connect_cloudformation(region=regions[0], **credentials)
        template_file = open(args.template, 'r')
        template_body = template_file.read()
        template = cfn.validate_template(template_body=template_body)
        printResult(args.template, template)
except boto.exception.BotoServerError, e:
    log.exception(e)
    sys.exit(bc.ExitCodes.FAIL)
