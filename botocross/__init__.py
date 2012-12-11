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
import logging
botocross_log = logging.getLogger('botocross')

def configure_logging(logger, level):
    logger.setLevel(getattr(logging, level.upper()))
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logger.getEffectiveLevel())
    logger.addHandler(console_handler)

def create_arn(iam, service, region, resource):
    from botocross.iam.accountinfo import AccountInfo
    accountInfo = AccountInfo(iam)
    account = accountInfo.describe()
    return 'arn:aws:' + service + ':' + region + ':' + account.id + ':' + resource

# TODO: refactor to argparse custom action for inline usage!
def build_filter_params(filter_args):
    from collections import defaultdict

    if not filter_args:
        return None

    params = defaultdict(list)
    filters = [filter_arg.split('=') for filter_arg in filter_args]
    for k, v in filters:
        params[k].append(v)
    botocross_log.info(filter_args)
    botocross_log.debug(params)
    return params

def build_common_parser():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-v", "--verbose", action='store_true')  # TODO: drop in favor of a log formatter?!
    parser.add_argument("--access_key_id", dest='aws_access_key_id', help="Your AWS Access Key ID")
    parser.add_argument("--secret_access_key", dest='aws_secret_access_key', help="Your AWS Secret Access Key")
    parser.add_argument("-l", "--log", dest='log_level', default='WARNING',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help="The logging level to use. [default: WARNING]")
    return parser

def build_region_parser():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-r", "--region", help="A region substring selector (e.g. 'us-west')")
    return parser

def build_filter_parser(resource_name):
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-f", "--filter", action="append", help="An EC2 instance filter. [can be used multiple times]")
    parser.add_argument("-i", "--id", dest="resource_ids", action="append", help="An EC2 instance id. [can be used multiple times]")
    return parser

def parse_credentials(args):
    return {'aws_access_key_id': args.aws_access_key_id, 'aws_secret_access_key': args.aws_secret_access_key}

def is_region_selected(region, name):
    return True if region.name.find(name) != -1 else False

def filter_regions(regions, region):
    if region:
        botocross_log.info("... (filtered by region '" + region + "')")
        regions = filter(lambda x: is_region_selected(x, region), regions)
    return regions

# TODO: remove this S3 legacy induced partial duplication, if possible.
def is_region_selected_s3(region, name):
    from botocross.s3 import RegionMap
    return True if RegionMap[region].find(name) != -1 else False

# TODO: remove this S3 legacy induced partial duplication, if possible.
def filter_regions_s3(regions, region):
    if region:
        botocross_log.info("... (filtered by S3 region '" + region + "')")
        regions = filter(lambda x: is_region_selected_s3(x, region), regions)
    return regions

class ExitCodes:
    (OK, FAIL) = range(0, 2)
