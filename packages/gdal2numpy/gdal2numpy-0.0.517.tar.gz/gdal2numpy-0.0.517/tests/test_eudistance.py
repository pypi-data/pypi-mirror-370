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


    def test_distance(self):
        """
        test_distance 
        """
        #fileline = f"{workdir}/lidar_rimini_building_2.shoreline.tif"
        fileline = f"s3://saferplaces.co/test/lidar_rimini_building_2.shoreline.tif"
        fileout  = f"s3://saferplaces.co/test/lidar_rimini_building_2.dist.tif"
        GDALEuclideanDistance(fileline, fileout)

        


if __name__ == '__main__':
    unittest.main()



