import os,warnings
import unittest
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

    def test_query_by_point(self):
        """
        test_query_by_point: 
        """
        fileshp = f"{workdir}/OSM_BUILDINGS_091244.shp"
        
        fid = QueryByPoint(fileshp, [ 11.338511, 44.497934])
        print(fid)

        

if __name__ == '__main__':
    unittest.main()



