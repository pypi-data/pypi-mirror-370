import os
import unittest
import warnings
from gdal2numpy import *

workdir = justpath(__file__)

filetif = f"{workdir}/CLSA_LiDAR.tif"


class Test(unittest.TestCase):
    """
    Tests
    """
    def setUp(self):
        warnings.simplefilter("ignore", ResourceWarning)


    def tearDown(self):
        warnings.simplefilter("default", ResourceWarning)


    def test_download_s3(self):
        """
        test_s3: 
        """
        #fileshp = copy("s3://saferplaces.co/test/barrier.shp")
        #print("fileshp is:", fileshp)
        #self.assertTrue(os.path.exists(fileshp))
        pass


    def test_download_tif(self):
        """
        test_s3: 
        """
        filetif = copy("s3://saferplaces.co/test/lidar_rimini_building_2.tif")
        filetif = copy("s3://saferplaces.co/test/lidar_rimini_building_2.tif")
        print("filetif is:", filetif)
        self.assertTrue(os.path.exists(filetif))

    



if __name__ == '__main__':
    unittest.main()



