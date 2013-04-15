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

class UserInfo:
    """
    Represents an AWS User
    """

    def __init__(self, iam_connection):
        self.connection = iam_connection
        self.log = logging.getLogger('boto_cli.iam.UserInfo')
        # populate those attributes not leaked via the exception, if user has no permission for iam:GetUser
        self.path = botocross.iam.RESOURCE_UNAUTHORIZED
        self.create_date = botocross.iam.RESOURCE_UNAUTHORIZED
        self.id = botocross.iam.RESOURCE_UNAUTHORIZED  # TODO: could be deduced from credentials in use instead.

    def __repr__(self):
        template = '<UserInfo - path:%s create_date:%s id:%s arn:%s name:%s>'
        return  template % (self.path, self.create_date, self.id, self.arn, self.name)

    def describe(self):
        try:
            user = self.connection.get_user()
            self.user = user['get_user_response']['get_user_result']['user']
            self.path = self.user['path']
            self.create_date = self.user['create_date']
            self.id = self.user['user_id']
            self.arn = self.user['arn']
            self.name = self.user['user_name']
        except boto.exception.BotoServerError, e:
            # NOTE: given some information can be deduced from the exception still, the lack of permissions is
            # considered a normal condition still and the exception handled/logged accordingly.
            if e.error_code != 'AccessDenied':
                raise
            self.arn = e.error_message.rpartition(' ')[2]
            self.name = e.error_message.rpartition('/')[2]
            self.log.debug(e.error_message)
        self.log.debug(self)
        return self

# Sample exercise of class functionality (requires AWS credentials to be provided externally)
if __name__ == "__main__":
    try:
        iam = boto.connect_iam()
        userInfo = UserInfo(iam)
        user = userInfo.describe()
        print user
    except boto.exception.BotoServerError, e:
        logging.exception(e.error_message)
