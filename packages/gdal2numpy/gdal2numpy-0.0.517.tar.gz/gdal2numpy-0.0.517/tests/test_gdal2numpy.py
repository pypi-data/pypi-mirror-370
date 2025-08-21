import os
import unittest
import warnings
from gdal2numpy import *

workdir = justpath(__file__)


filedem = f"{workdir}/data/CLSA_LiDAR.tif"
fileout = f"{workdir}/test_out.tif"


class Test(unittest.TestCase):
    """
    Tests
    """
    def setUp(self):
        warnings.simplefilter("ignore", ResourceWarning)


    def tearDown(self):
        warnings.simplefilter("default", ResourceWarning)


    def test_raster(self):
        """
        test_raster: 
        """
        mem_usage()
        data, _, _ = GDAL2Numpy(filedem, load_nodata_as=np.nan)
        print(f"Memory read:{data.size*4 / 1024**2:.2f} MB")
        mem_usage()
        self.assertTrue(data.size>0)


    def test_s3(self):
        """
        test_save: 
        """
        filedem = "s3://saferplaces.co/test/lidar_rimini_building_2.tif"
        data, gt, prj = GDAL2Numpy(filedem, load_nodata_as=np.nan)
        print(prj)
        self.assertTrue(data.size>0)


    def test_vsi(self):
        """
        test_save: 
        """
        filedem = "s3://saferplaces.co/Ambiental/Fluvial/Ambiental_Italy_FloodMap_Fluvial_100yr_v1_0.cog.tif"
        bbox = (4523904.479738138, 2325781.4713545926, 4530348.323133135, 2337527.589964536)
        data, gt, prj = GDAL2Numpy(filedem, bbox=bbox, load_nodata_as=np.nan)
        print(data.shape)
        print(prj)
        self.assertTrue(data.size>0)

   
    def test_vsicurl(self):
        """
        test_save: 
        """
        filedem = "https://s3.us-east-1.amazonaws.com/saferplaces.co/test/lidar_rimini_building_2.tif"
        data, gt, prj = GDAL2Numpy(filedem, load_nodata_as=np.nan)
        self.assertTrue(data.size>0)


if __name__ == '__main__':
    unittest.main()



