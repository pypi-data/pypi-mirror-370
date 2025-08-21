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

    def test_secret(self):
        """
        test_secret: 
        """

        filesecret = f"/run/secrets/hello.txt"
        secret =  load_secret(filesecret, "HELLO")
        self.assertEqual(secret, "supercalifragilistichespiralidoso")
        self.assertTrue(os.environ.get("HELLO") == "supercalifragilistichespiralidoso")

if __name__ == '__main__':
    unittest.main()
