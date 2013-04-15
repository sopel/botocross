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

import boto
import botocross.iam
import logging

class AccountInfo:
    """
    Represents an AWS Account
    """

    def __init__(self, iam_connection):
        self.connection = iam_connection
        self.log = logging.getLogger('boto_cli.iam.AccountInfo')
        self.user = None
        # populate those attributes not leaked via the exception, if user has no permission for iam:ListAccountAliases
        self.alias = botocross.iam.RESOURCE_UNAUTHORIZED
        self.id  = None

    def __repr__(self):
        return '<AccountInfo - alias:%s id:%s>' % (self.alias, self.id)

    def describe(self, user=None):
        try:
            alias = self.connection.get_account_alias()
            aliases = alias['list_account_aliases_response']['list_account_aliases_result']['account_aliases']
            # Is there an alias at all? If so, use the first one (currently only one alias is supported).
            if len(aliases):
                self.alias = alias['list_account_aliases_response']['list_account_aliases_result']['account_aliases'][0]
            else:
                self.alias = botocross.iam.RESOURCE_NONEXISTENT
        except boto.exception.BotoServerError, e:
            # NOTE: given some information can be deduced from the exception still, the lack of permissions is
            # considered a normal condition still and the exception handled/logged accordingly.
            if e.error_code != 'AccessDenied':
                raise
            self.log.debug(e.error_message)
        try:
            # REVIEW: there should be a better way to retrieve the account id, which is 'leaked in the exception anyway
            # eventually; see http://stackoverflow.com/questions/10197784 for a respective question.
            if not self.user:
                from userinfo import UserInfo
                userInfo = UserInfo(self.connection)
                self.user = userInfo.describe()
            self.id = self.user.arn.replace('arn:aws:iam::', '').partition(':')[0]
        except boto.exception.BotoServerError, e:
            # NOTE: given some information can be deduced from the exception still, the lack of permissions is
            # considered a normal condition still and the exception handled/logged accordingly.
            if e.error_code != 'AccessDenied':
                raise
            self.id = e.error_message.replace('User: arn:aws:iam::', '').partition(':')[0]
            self.log.debug(e.error_message)
        self.log.debug(self)
        return self

# Sample exercise of class functionality (requires AWS credentials to be provided externally)
if __name__ == "__main__":
    try:
        iam = boto.connect_iam()
        accountInfo = AccountInfo(iam)
        account = accountInfo.describe()
        print account
    except boto.exception.BotoServerError, e:
        logging.exception(e.error_message)
