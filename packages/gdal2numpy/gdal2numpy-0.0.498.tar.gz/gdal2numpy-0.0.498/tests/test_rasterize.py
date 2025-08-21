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

    # def test_rasterize_like1(self):
    #     """
    #     test_raster: 
    #     """
    #     #def RasterizeLike(fileshp, filedem, file_tif="", dtype=None, burn_fieldname="", \
    #     #          z_value=None, factor=1.0, nodata=None):
    #     fileshp = f"{workdir}/data/Rimini/barrier.shp"
    #     filedem = f"{workdir}/data/Rimini/MINAMBIENTE_ITALY_173447.bld.tif"
    #     fileout = f"{workdir}/data/Rimini/barrier1.tif"
    #     dem, _, _   = GDAL2Numpy(filedem, load_nodata_as=np.nan)
    #     data, _, _  = RasterizeLike(fileshp, filedem, fileout=None, burn_fieldname="height", nodata=0)
    
    #     print(np.unique(data))

    #     self.assertTrue(np.size(data) > 0)
    #     self.assertEqual(data.shape, dem.shape)


    def test_rasterize_like2(self):
        """
        test_raster: 
        """
        #def RasterizeLike(fileshp, filedem, file_tif="", dtype=None, burn_fieldname="", \
        #          z_value=None, factor=1.0, nodata=None):
        fileshp = f"{workdir}/test_building.shp"
        filedem = f"{workdir}/test_river.tif"
        fileout = f"{workdir}/test_building.tif"
        data, _, _  = RasterizeLike(fileshp, filedem, buf=2.0, fileout=fileout, nodata=0)

        print(np.unique(data))
    

    def test_gdalwarp(self):
        """
        test_rasterlike  
        """
        filedem = f"{workdir}/test_river.tif"
        fileout = f"{workdir}/test_gdalwarped.tif"
        gdalwarp(filedem, fileout, dstSRS=filedem)
        self.assertTrue(isfile(fileout))


if __name__ == '__main__':
    unittest.main()



