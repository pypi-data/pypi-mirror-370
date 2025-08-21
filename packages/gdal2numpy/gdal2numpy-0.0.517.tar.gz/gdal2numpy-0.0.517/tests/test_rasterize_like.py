import os
import unittest
import numpy as np
from gdal2numpy import *

workdir = justpath(__file__)


class Test(unittest.TestCase):
    """
    Tests
    """
  
    def test_rasterlike(self):
        """
        test_rasterlike  
        """
        #filedem = f"s3://saferplaces.co/test/valerio.luzzi@gecosistema.com/test_dem_1689868333.tif"
        #fileobm = f"s3://saferplaces.co/test/valerio.luzzi@gecosistema.com/test_building_1689868333.shp"
        workdir = f"D:/Users/vlr20/Projects/GitHub/saferplaces-4.0/mnt/efs/projects/valluzzi@gmail.com/Siviglia"
        filedem = f"{workdir}/IGN_ES_085954.tif"
        fileobm = f"{workdir}/OSM_BUILDINGS_090028.shp"
        fileout = f"{workdir}/IGN_ES_085954.obmx.tif"
        data, gt, prj = RasterizeLike(fileobm, filedem, fileout=None, z_value=10)
        print(np.nanmin(data), np.nanmax(data))
        #self.assertEqual(GetPixelSize(fileout), GetPixelSize(filetpl))

if __name__ == '__main__':
    unittest.main()



