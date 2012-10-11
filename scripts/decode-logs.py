#!/usr/bin/python
# Copyright (c) 2012 David Laing http://davidlaing.com/
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
import base64
from StringIO import StringIO
from gzip import GzipFile

# configure command line argument parsing
parser = argparse.ArgumentParser(description='Decode a base64 encoded gzipped file')
parser.add_argument("source", help="The source content (or filename for --encode")
parser.add_argument("-e", "--encode", action='store_true', help="Gzip then base64 encode file")

args = parser.parse_args()

output = ""
if args.encode:
	out = StringIO()
	f = GzipFile(fileobj=out, mode='w')
	f.write(open(args.source, 'r').read())
	f.close()
	output = base64.b64encode(out.getvalue())
else:
	base64_content = args.source
	gzipped_content = base64.b64decode(base64_content)
	output = GzipFile('', 'r', 0, StringIO(gzipped_content)).read()

print output

