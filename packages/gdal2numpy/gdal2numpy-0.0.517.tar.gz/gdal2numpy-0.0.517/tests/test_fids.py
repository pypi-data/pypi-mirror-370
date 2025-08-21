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


    def test_poly_from_fid(self):
        """
        test_poly_from_shape 
        """
        fileshp = "https://s3.us-east-1.amazonaws.com/saferplaces.co/packages/gdal2numpy/open/OSM_BUILDINGS_102258.shp|layername=OSM_BUILDINGS_102258|fid=1,3,7"
        geom = PolygonFrom(fileshp)
        self.assertTrue(geom.GetGeometryName() == "MULTIPOLYGON")
       

  
        

if __name__ == '__main__':
    unittest.main()
