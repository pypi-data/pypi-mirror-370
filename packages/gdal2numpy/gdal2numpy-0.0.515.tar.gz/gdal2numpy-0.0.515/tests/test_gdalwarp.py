import os
import warnings
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

    # def test_gdalwarp(self):
    #     """
    #     test_gdalwarp:
    #     """
    #     print("test_gdalwarp")
    #     filedem = f"{workdir}/lidar_rimini_building_2.tif"
    #     fileout = f"{workdir}/lidar_rimini_building_2.warp.tif"
    #     gdalwarp(filedem, fileout, dstSRS=3857)
    #     self.assertTrue(isfile(fileout))

    # def test_gdalwarp_inplace(self):
    #     """
    #     test_gdalwarp_inplace
    #     """
    #     print("test_gdalwarp_inplace")
    #     filedem = f"{workdir}/lidar_rimini_building_2.warp.tif"
    #     gdalwarp(filedem, dstSRS=7791)
    #     srs = GetSpatialRef(filedem)
    #     srsTarget = GetSpatialRef(7791)
    #     self.assertTrue(srs.IsSame(srsTarget))

    # def test_gdalwarp_s3(self):
    #     """
    #     test_gdalwarp_s3
    #     """
    #     print("test_gdalwarp_s3")
    #     filedem = f"s3://saferplaces.co/lidar-rer-100m.tif"
    #     fileout = f"{workdir}/lidar-rer-100m.warp.tif"
    #     gdalwarp(filedem, fileout, dstSRS=7791, format="COG")
    #     self.assertTrue(isfile(fileout))

    # def test_gdalwarp_s3_2_s3(self):
    #     """
    #     test_gdalwarp_s3_2_s3
    #     """
    #     print("test_gdalwarp_s3_2_s3")
    #     filedem = f"s3://saferplaces.co/lidar-rer-100m.tif"
    #     fileout = f"s3://saferplaces.co/lidar-rer-100m.warp.tif"
    #     gdalwarp(filedem, fileout, format="COG")
    #     self.assertTrue(isfile(fileout))

    # def test_gdalwarp(self):
    #     """
    #     test_gdalwarp:
    #     """
    #     set_log_level(verbose=True,debug=True)
    #     filedem = r"G:\\Drive condivisi\\GECOsDRIVE_2023\\Parma_safer\\dtm\\parma_dtm_2m_merge-25832.tif"
    #     fileout = f"{workdir}/parma_dtm_2m_merge-25832.tif"
    #     gdalwarp(filedem, fileout, dstSRS=filedem, format="COG")

    #     self.assertTrue(isfile(fileout))

    def test_gdalwarp_bbox(self):
        """
        test_gdalwarp_bbox
        """
        # set_log_level(verbose=True,debug=True)
        filedem = r"G:\\Drive condivisi\\GECOsDRIVE_2023\\Parma_safer\\dtm\\parma_dtm_2m_merge-25832.tif"
        filedem = "s3://saferplaces.co/test/lidar_rimini_building_2_wd.tif"
        fileout = f"{workdir}/lidar_rimini_building_2_wd.cropped.tif"
        file1 = f"{workdir}/12_2k_0015.tif"
        file2 = f"{workdir}/12_2k_0016.tif"
        fileout = f"{workdir}/12_2k_0015_0016.tif"
        # fileaux = f"{workdir}/12_2k_0015_0016.tif.aux.xml"
        # , cutline=[783785, 4885325 , 784795, 4886006])
        gdalwarp([file1, file2], fileout, dstSRS=filedem, format="GTiff")
        self.assertTrue(isfile(fileout))
        # self.assertTrue(isfile(fileaux))

    # def test_if_is_cog(self):
    #     """
    #     test_if_is_cog
    #     """
    #     print("test_if_is_cog")
    #     filedem = f"{workdir}/lidar-rer-100m.warp.tif"
    #     self.assertTrue(is_cog(filedem))


if __name__ == '__main__':
    unittest.main()
