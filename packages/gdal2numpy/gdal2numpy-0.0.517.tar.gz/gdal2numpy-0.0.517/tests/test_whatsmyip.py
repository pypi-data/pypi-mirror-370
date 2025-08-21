import os
import unittest
import warnings
from gdal2numpy import *

workdir = justpath(__file__)


class Test(unittest.TestCase):
    """
    Tests
    """
    def setUp(self):
        warnings.simplefilter("ignore", ResourceWarning)


    def tearDown(self):
        warnings.simplefilter("default", ResourceWarning)

    def test_localip(self):
        """
        test_localip: 
        """
        myip = local_ip()
        self.assertTrue(myip is not None)
        self.assertTrue(len(myip.split("."))==4)

    def test_whatsmyip(self):
        """
        test_whatsmyip: 
        """
        myip = whatsmyip()
        self.assertTrue(myip is not None)
        self.assertTrue(len(myip.split("."))==4)



if __name__ == '__main__':
    unittest.main()



