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

import logging
s3_log = logging.getLogger('botocross.s3')

RegionMap = {
    'DEFAULT': 'us-east-1',
    'USWest': 'us-west-1',
    'USWest2': 'us-west-2',
    'SAEast': 'sa-east-1',
    'EU': 'eu-west-1',
    'APNortheast': 'ap-northeast-1',
    'APSoutheast': 'ap-southeast-1',
    'APSoutheast2': 'ap-southeast-2',
    'USGovWest': 'us-gov-west-1'}

# NOTE: S3 region handling differs in an unfortunate way (likely a legacy issue) and requires special treatment.
def class_iterator(Class):
    return (element for element in dir(Class) if element[:2] != '__')
