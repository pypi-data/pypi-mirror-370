import unittest
import warnings
from gdal2numpy import *


class Test(unittest.TestCase):
    """
    Tests
    """
    def setUp(self):
        warnings.simplefilter("ignore", ResourceWarning)

    def tearDown(self):
        warnings.simplefilter("default", ResourceWarning)

    def test_isfile_s3(self):
        """
        test_isfile_s3: 
        """
        filetif = "s3://saferplaces.co/fdamage/shared/residential.csv"
        self.assertTrue(isfile(filetif))

    def test_isfile_http(self):
        """
        test_upload_s3: 
        """
        filetif = "https://s3.us-east-1.amazonaws.com/saferplaces.co/packages/gdal2numpy/isfile/CLSA_LiDAR.tif"
        self.assertTrue(israster(filetif))

    def test_isfile_shp(self):
        """
        test_upload_s3: 
        """
        fileshp = "s3://saferplaces.co/packages/gdal2numpy/isfile/CLSA_LiDAR.tif"
        self.assertTrue(israster(fileshp))


if __name__ == '__main__':
    unittest.main()
