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
parser = argparse.ArgumentParser(description='Deregister EC2 images in all/some available EC2 regions',
                                 parents=[bc.build_region_parser(), bc.build_filter_parser('EC2 image'), bc.build_common_parser()])
args = parser.parse_args()

# process common command line arguments
log = logging.getLogger('botocross')
bc.configure_logging(log, args.log_level)
credentials = bc.parse_credentials(args)
regions = bc.filter_regions(boto.ec2.regions(), args.region, args.include_govcloud, args.only_govcloud)
filter = bc.build_filter(args.filter, args.exclude)
log.info(args.resource_ids)

# execute business logic
log.info("Deregistering EC2 images")

for region in regions:
    try:
        ec2 = boto.connect_ec2(region=region, **credentials)
        images = ec2.get_all_images(image_ids=args.resource_ids, owners=['self'], filters=filter['filters'])
        if filter['excludes']:
            exclusions = ec2.get_all_images(owners=['self'], filters=filter['excludes'])
            images = bc.filter_list_by_attribute(images, exclusions, 'id')
        print region.name + ": " + str(len(images)) + " EC2 images"
        for image in images:
            if args.verbose:
                print image.id
            else:
                ec2.deregister_image(image.id, delete_snapshot=True)
    except boto.exception.BotoServerError, e:
        log.error(e.error_message)
