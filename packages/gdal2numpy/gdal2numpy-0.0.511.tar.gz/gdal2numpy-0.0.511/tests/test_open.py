import os
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

    def test_open_shape(self):
        """
        test_open: 
        """
        ds = OpenShape(fileshp)
        self.assertTrue(ds is not None)
        self.assertEqual(GetFeatureCount(ds), 23989)
    

    def test_open_raster(self):
        """
        test_open: 
        """
        ds = OpenRaster(filetif)
        self.assertTrue(ds is not None)
        self.assertEqual(ds.RasterCount, 1)

    def test_opentext(self):
        """
        test_opentext: 
        """
        filetxt = f"https://s3.us-east-1.amazonaws.com/saferplaces.co/packages/gdal2numpy/open/residential.csv"
        filetxt = f"s3://saferplaces.co/packages/gdal2numpy/open/residential.csv"

        text = get(filetxt)
        # 0,0.0
        # 0.5,0.25
        # 1,0.4
        # 1.5,0.5
        # 2,0.6
        # 3,0.75
        # 4,0.85
        # 5,0.95
        # 6,1.0
        self.assertTrue(text is not None)


if __name__ == '__main__':
    unittest.main()
