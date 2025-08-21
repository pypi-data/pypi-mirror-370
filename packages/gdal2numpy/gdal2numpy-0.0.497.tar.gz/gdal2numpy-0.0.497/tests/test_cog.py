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


    def test_download_cog(self):
        """
        test_secret: 
        """
        filetif = f"s3://saferplaces.co/packages/gdal2numpy/isfile/CLSA_LiDAR.tif"
        bbox = [492437, 5216447, 492806, 5216610]
        bbox_srs = "EPSG:26914"
        fileout = CogDownload(filetif, bbox, bbox_srs)
        self.assertTrue(os.path.exists(fileout))

if __name__ == '__main__':
    unittest.main()
