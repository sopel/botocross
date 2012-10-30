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

from botocross.iam.accountinfo import AccountInfo
from botocross.iam.userinfo import UserInfo
import argparse
import boto
import botocross as bc
import logging
import sys

# configure command line argument parsing
parser = argparse.ArgumentParser(description='Validates AWS credentials and display account/user information',
                                 parents=[bc.build_common_parser()])
args = parser.parse_args()

# process common command line arguments
log = logging.getLogger('botocross')
bc.configure_logging(log, args.log_level)
credentials = bc.parse_credentials(args)

# execute business logic
log.info("Validating credentials:")

try:
    iam = boto.connect_iam(**credentials)
    userInfo = UserInfo(iam)
    user = userInfo.describe()
    accountInfo = AccountInfo(iam)
    account = accountInfo.describe(user)
    print "User name is '" + user.name + "' with id " + user.id
    print "Account alias is '" + account.alias + "' with id " + account.id
except boto.exception.BotoServerError, e:
    log.exception(e)
    sys.exit(bc.ExitCodes.FAIL)
