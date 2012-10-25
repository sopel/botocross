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
log = logging.getLogger('botocross')
import unittest

class TestPackage(unittest.TestCase):

    def test_configure_logging(self):
	from botocross import configure_logging
        
	self.assertTrue(0 == len(log.handlers))
	self.assertEquals(getattr(logging, 'NOTSET'), log.getEffectiveLevel())
	
	configure_logging(log, 'DEBUG')
        
	self.assertEquals(type(log.handlers[0]), logging.StreamHandler)
	self.assertEquals(10, log.getEffectiveLevel())

    def test_exit_codes(self):
	from botocross import ExitCodes
	
	self.assertTrue(0 == ExitCodes.OK)
	self.assertTrue(1 == ExitCodes.FAIL)
