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
import boto.sns
import botocross as bc
import logging

# configure command line argument parsing
parser = argparse.ArgumentParser(description='Subscribe to a SNS topic in all/some available SNS regions',
                                 parents=[bc.build_region_parser(), bc.build_common_parser()])
parser.add_argument("topic", help="A topic name")
parser.add_argument("protocol", help="The protocol used to communicate with the subscriber. Current choices are: email|email-json|http|https|sqs")
parser.add_argument("endpoint", help="The endpoint to receive notifications.")
args = parser.parse_args()

# process common command line arguments
log = logging.getLogger('botocross')
bc.configure_logging(log, args.log_level)
credentials = bc.parse_credentials(args)
regions = bc.filter_regions(boto.sns.regions(), args.region)

# execute business logic
log.info("Subscribing to SNS topics named '" + args.topic + ' with protocol ' + args.protocol + ' and endpoint ' + args.endpoint + "':")

iam = boto.connect_iam(**credentials)
for region in regions:
    pprint(region.name, indent=2)
    try:
        sns = boto.connect_sns(region=region, **credentials)
        arn = bc.create_arn(iam, 'sns', region.name, args.topic)
        log.debug('Subscribing to topic ' + arn + ' with protocol ' + args.protocol + ' and endpoint ' + args.endpoint)
        result = sns.subscribe(arn, args.protocol, args.endpoint)
        print result['SubscribeResponse']['SubscribeResult']['SubscriptionArn']

    except boto.exception.BotoServerError, e:
        log.error(e.error_message)
