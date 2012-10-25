import logging
log = logging.getLogger('botocross')
import unittest

class TestBotocrossPackage(unittest.TestCase):

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
