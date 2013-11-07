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

from boto.s3.connection import Location
from botocross.s3 import RegionMap, class_iterator
from pprint import pprint
import argparse
import boto
import boto.s3
import botocross as bc
import logging

# configure command line argument parsing
parser = argparse.ArgumentParser(description='Delete a S3 bucket in all/some available S3 regions',
                                 parents=[bc.build_region_parser(), bc.build_common_parser()])
parser.add_argument("bucket", help="A bucket name (will get region suffix)")
parser.add_argument("-f", "--force", action="store_true", help="Delete all keys in the bucket first.")
args = parser.parse_args()

# process common command line arguments
log = logging.getLogger('botocross')
bc.configure_logging(log, args.log_level)
credentials = bc.parse_credentials(args)
locations = bc.filter_regions_s3(class_iterator(Location), args.region, args.include_govcloud, args.only_govcloud)

# execute business logic
log.info("Deleting S3 buckets named '" + args.bucket + "':")

s3 = boto.connect_s3(**credentials)

for location in locations:
    region = RegionMap[location]
    pprint(region, indent=2)
    try:
        bucket_name = args.bucket + '-' + region
        bucket = s3.get_bucket(bucket_name)
        print 'Deleting bucket ' + bucket_name
        if args.force:
            print '... --force used, deleting all keys in ' + bucket_name
            result = bucket.delete_keys([key.name for key in bucket])
            log.debug(result.deleted)
        s3.delete_bucket(bucket_name)
    except boto.exception.BotoServerError, e:
        log.error(e.error_message)
