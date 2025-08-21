import os
import unittest
import numpy as np
from gdal2numpy import *


filetif = "s3://saferplaces.co/packages/gdal2numpy/open/CLSA_LiDAR.tif"
fileshp = "s3://saferplaces.co/packages/gdal2numpy/open/OSM_BUILDINGS_102258.shp"


class Test(unittest.TestCase):
    """
    Tests
    """

    def test_gdal_translate(self):
        """
        test_gdal_translate  
        """
        fileout = tempdir() + "/CLSA_LiDAR.cog.tif"
        # def gdal_translate(filein, fileout=None, ot=None, a_nodata=None, projwin=None, projwin_srs=None, format="GTiff"):
        # fileout = gdal_translate(filerain, fileout=fileout, projwin=projWin, projwin_srs=projWinSrs, format="GTiff")
        fileout = gdal_translate(filetif, fileout, format="COG")
        self.assertTrue(isfile(fileout))
        self.assertEqual(GetRasterShape(fileout), GetRasterShape(filetif))
        self.assertEqual(GetPixelSize(fileout), GetPixelSize(filetif))
        self.assertEqual(GetExtent(fileout), GetExtent(filetif))
        self.assertTrue(IsValid(fileout))
        self.assertEqual(AutoIdentify(fileout), AutoIdentify(filetif))
        self.assertTrue(SameSpatialRef(fileout, filetif))
        os.remove(fileout)

    def test_crop(self):
        """
        test_crop  
        """
        bbox = (492253, 5216180, 492758, 5216518)
        srs = "EPSG:26914"
        fileout = tempdir() + "/CLSA_LiDAR.crop.tif"
        # def gdal_translate(filein, fileout=None, ot=None, a_nodata=None,
        #                       projwin=None, projwin_srs=None, format="GTiff"):
        fileout = gdal_translate(
            filetif, fileout, projwin=bbox, projwin_srs=srs, format="GTiff")
        self.assertTrue(isfile(fileout))
        self.assertEqual(GetRasterShape(fileout), (338, 505))
        self.assertEqual(GetPixelSize(fileout), (1.0, 1.0))
        os.remove(fileout)


if __name__ == '__main__':
    unittest.main()
