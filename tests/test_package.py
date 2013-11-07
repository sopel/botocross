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
import unittest
log = logging.getLogger('botocross')

class TestPackage(unittest.TestCase):
    num_regions = 9;
    num_regions_gov = 1;

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

    def test_build_filter_params_with_no_keys(self):
        from botocross import build_filter_params

        args = None
        params = build_filter_params(args)
        self.assertEquals(None, params)

    def test_build_filter_params_with_differing_keys(self):
        from botocross import build_filter_params

        args = ["tag:Name=boto", "tag:Extension=botocross"]
        params = build_filter_params(args)
        self.assertEquals(2, len(params))
        for k, v in params.iteritems():
            self.assertTrue(isinstance(v, list))
            self.assertEquals(1, len(v))

    def test_build_filter_params_with_identical_keys(self):
        from botocross import build_filter_params

        args = ["tag:Name=boto", "tag:Name=botocross"]
        params = build_filter_params(args)
        self.assertEquals(1, len(params))
        for k, v in params.iteritems():
            self.assertTrue(isinstance(v, list))
            self.assertEquals(2, len(v))

    def test_filter_regions(self):
        from botocross import filter_regions
        import boto.ec2

        log.info("Testing region filter (GovCloud excluded):")
        all_regions = boto.ec2.regions()
        filtered_regions = filter_regions(all_regions, "us-west-1")
        self.assertEquals(1, len(filtered_regions))
        filtered_regions = filter_regions(all_regions, "us-west")
        self.assertEquals(2, len(filtered_regions))
        filtered_regions = filter_regions(all_regions, "west-1")
        self.assertEquals(2, len(filtered_regions))
        filtered_regions = filter_regions(all_regions, "west")
        self.assertEquals(3, len(filtered_regions))
        filtered_regions = filter_regions(all_regions, None)
        self.assertEquals(self.num_regions - self.num_regions_gov, len(filtered_regions))

    def test_filter_regions_gov_included(self):
        from botocross import filter_regions
        import boto.ec2

        log.info("Testing region filter (GovCloud included):")
        all_regions = boto.ec2.regions()
        filtered_regions = filter_regions(all_regions, "us-west-1", True, False)
        self.assertEquals(1, len(filtered_regions))
        filtered_regions = filter_regions(all_regions, "us-west", True, False)
        self.assertEquals(2, len(filtered_regions))
        filtered_regions = filter_regions(all_regions, "west-1", True, False)
        self.assertEquals(3, len(filtered_regions))
        filtered_regions = filter_regions(all_regions, "west", True, False)
        self.assertEquals(4, len(filtered_regions))
        filtered_regions = filter_regions(all_regions, None, True, False)
        self.assertEquals(self.num_regions, len(filtered_regions))

    def test_filter_regions_gov_only(self):
        from botocross import filter_regions
        import boto.ec2

        log.info("Testing region filter (GovCloud only):")
        all_regions = boto.ec2.regions()
        filtered_regions = filter_regions(all_regions, "us-gov-west-1", False, True)
        self.assertEquals(1, len(filtered_regions))
        filtered_regions = filter_regions(all_regions, "us-gov-west", False, True)
        self.assertEquals(1, len(filtered_regions))
        filtered_regions = filter_regions(all_regions, "gov-west", False, True)
        self.assertEquals(1, len(filtered_regions))
        filtered_regions = filter_regions(all_regions, "gov", False, True)
        self.assertEquals(1, len(filtered_regions))
        filtered_regions = filter_regions(all_regions, None, False, True)
        self.assertEquals(self.num_regions_gov, len(filtered_regions))

    def test_filter_regions_s3(self):
        from botocross import filter_regions_s3
        from botocross.s3 import RegionMap

        log.info("Testing S3 region filter (GovCloud excluded):")
        all_regions = RegionMap
        filtered_regions = filter_regions_s3(all_regions, "us-west-1")
        self.assertEquals(1, len(filtered_regions))
        filtered_regions = filter_regions_s3(all_regions, "us-west")
        self.assertEquals(2, len(filtered_regions))
        filtered_regions = filter_regions_s3(all_regions, "west-1")
        self.assertEquals(2, len(filtered_regions))
        filtered_regions = filter_regions_s3(all_regions, "west")
        self.assertEquals(3, len(filtered_regions))
        filtered_regions = filter_regions_s3(all_regions, None)
        self.assertEquals(self.num_regions - self.num_regions_gov, len(filtered_regions))

    def test_filter_regions_s3_gov_included(self):
        from botocross import filter_regions_s3
        from botocross.s3 import RegionMap

        log.info("Testing S3 region filter (GovCloud included):")
        all_regions = RegionMap
        filtered_regions = filter_regions_s3(all_regions, "us-gov-west-1", True, False)
        self.assertEquals(1, len(filtered_regions))
        filtered_regions = filter_regions_s3(all_regions, "us-gov-west", True, False)
        self.assertEquals(1, len(filtered_regions))
        filtered_regions = filter_regions_s3(all_regions, "gov-west", True, False)
        self.assertEquals(1, len(filtered_regions))
        filtered_regions = filter_regions_s3(all_regions, "gov", True, False)
        self.assertEquals(1, len(filtered_regions))
        filtered_regions = filter_regions_s3(all_regions, None, True, False)
        self.assertEquals(self.num_regions, len(filtered_regions))

    def test_filter_regions_s3_gov_only(self):
        from botocross import filter_regions_s3
        from botocross.s3 import RegionMap

        log.info("Testing S3 region filter (GovCloud only):")
        all_regions = RegionMap
        filtered_regions = filter_regions_s3(all_regions, "us-gov-west-1", False, True)
        self.assertEquals(1, len(filtered_regions))
        filtered_regions = filter_regions_s3(all_regions, "us-gov-west", False, True)
        self.assertEquals(1, len(filtered_regions))
        filtered_regions = filter_regions_s3(all_regions, "gov-west", False, True)
        self.assertEquals(1, len(filtered_regions))
        filtered_regions = filter_regions_s3(all_regions, "gov", False, True)
        self.assertEquals(1, len(filtered_regions))
        filtered_regions = filter_regions_s3(all_regions, None, False, True)
        self.assertEquals(self.num_regions_gov, len(filtered_regions))
