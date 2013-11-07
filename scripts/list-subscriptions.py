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
parser = argparse.ArgumentParser(description='Describe SNS subscriptions in all/some available EC2 regions',
                                 parents=[bc.build_region_parser(), bc.build_common_parser()])
parser.add_argument("-t", "--topic", help="A topic name. [default: None]")
args = parser.parse_args()

# process common command line arguments
log = logging.getLogger('botocross')
bc.configure_logging(log, args.log_level)
credentials = bc.parse_credentials(args)
regions = bc.filter_regions(boto.sns.regions(), args.region, args.include_govcloud, args.only_govcloud)

# execute business logic
log.info("Describing SNS topics:")

if args.topic:
    iam = boto.connect_iam(**credentials)
for region in regions:
    try:
        sns = boto.connect_sns(region=region, **credentials)

        subscriptions = []
        next_token = None
        while True:
            if not args.topic:
                result = sns.get_all_subscriptions(next_token)
                subscriptions.extend(result['ListSubscriptionsResponse']['ListSubscriptionsResult']['Subscriptions'])
                next_token = result['ListSubscriptionsResponse']['ListSubscriptionsResult']['NextToken']
            else:
                arn = bc.create_arn(iam, 'sns', region.name, args.topic)
                result = sns.get_all_subscriptions_by_topic(arn, next_token)
                subscriptions.extend(result['ListSubscriptionsByTopicResponse']['ListSubscriptionsByTopicResult']['Subscriptions'])
                next_token = result['ListSubscriptionsByTopicResponse']['ListSubscriptionsByTopicResult']['NextToken']
            if not next_token:
                break
        print region.name + ": " + str(len(subscriptions)) + " subscriptions"
        for subscription in subscriptions:
            if args.verbose:
                pprint(subscription)
            else:
                print subscription['Endpoint']
    except boto.exception.BotoServerError, e:
        log.error(e.error_message)
