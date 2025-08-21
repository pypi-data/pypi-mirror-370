import unittest
import warnings
from gdal2numpy import *


filetif = "s3://saferplaces.co/packages/gdal2numpy/open/CLSA_LiDAR.tif"
fileshp = "s3://saferplaces.co/packages/gdal2numpy/open/OSM_BUILDINGS_102258.shp"

class Test(unittest.TestCase):
    """
    Tests
    """
    def setUp(self):
        warnings.simplefilter("ignore", ResourceWarning)

    def tearDown(self):
        warnings.simplefilter("default", ResourceWarning)

    def test_GetSpatialRef(self):
        """
        test_GetSpatialRef 
        """
        srs = GetSpatialRef(filetif)
        code = AutoIdentify(srs)
        self.assertEqual(code, "EPSG:26914")

    def test_AutoIdentify(self):
        """
        test_AutoIdentify 
        """
        code = AutoIdentify(filetif)
        self.assertEqual(code, "EPSG:26914")

    def test_AutoIdentifySHP(self):
        """
        test_AutoIdentifySHP 
        """
        code = AutoIdentify(fileshp)
        self.assertEqual(code, "EPSG:4326")


if __name__ == '__main__':
    unittest.main()



