import os
import unittest
import warnings
from gdal2numpy import *

workdir = justpath(__file__)


filedem = f"s3://saferplaces.co/packages/gdal2numpy/multibanda/CLSA_LiDAR.tif"
fileout = f"{workdir}/test_out.tif"


class Test(unittest.TestCase):
    """
    Tests
    """
    def setUp(self):
        warnings.simplefilter("ignore", ResourceWarning)


    def tearDown(self):
        warnings.simplefilter("default", ResourceWarning)


    def test_2d(self):
        """
        test_save: 
        """
        data, gt, prj = GDAL2Numpy(filedem, load_nodata_as=np.nan)       
        Numpy2GTiffMultiBanda(data, gt, prj, fileout)
        self.assertTrue(os.path.exists(fileout))
        os.remove(fileout)


    def test_3d(self):
        """
        test_save: 
        """
        banda1, gt, prj = GDAL2Numpy(filedem, load_nodata_as=np.nan)
        banda2 = banda1.copy()
        data = np.stack([banda1, banda2])
        print(data.shape)
        fileout = forceext(filedem, "multi.tif")
        Numpy2GTiffMultiBanda(data, gt, prj, fileout, save_nodata_as=-9999.0)
        self.assertTrue(isfile(fileout))

    def test_radar(self):
        """
        test_save: 
        """
        fileb1 = "s3://saferplaces.co/packages/safer-map-vite/Rimini/radarhera/RADAR_HERA_150M_5MIN__rainrate__band_1.cog.tif"
        fileb2 = "s3://saferplaces.co/packages/safer-map-vite/Rimini/radarhera/RADAR_HERA_150M_5MIN__rainrate__band_2.cog.tif"
        fileb3 = "s3://saferplaces.co/packages/safer-map-vite/Rimini/radarhera/RADAR_HERA_150M_5MIN__rainrate__band_3.cog.tif"
        fileb4 = "s3://saferplaces.co/packages/safer-map-vite/Rimini/radarhera/RADAR_HERA_150M_5MIN__rainrate__band_4.cog.tif"
        banda1, gt, prj = GDAL2Numpy(fileb1, load_nodata_as=np.nan)
        banda2, _, _    = GDAL2Numpy(fileb2, load_nodata_as=np.nan)
        banda3, _, _    = GDAL2Numpy(fileb3, load_nodata_as=np.nan)
        banda4, _, _    = GDAL2Numpy(fileb4, load_nodata_as=np.nan)
    
        data = np.stack([banda1, banda2, banda3, banda4])
        fileout = "s3://saferplaces.co/packages/safer-map-vite/Rimini/radarhera/RADAR_HERA_150M_5MIN.tif"
        Numpy2GTiffMultiBanda(data, gt, prj, fileout, save_nodata_as=-9999.0)
        self.assertTrue(isfile(fileout))


if __name__ == '__main__':
    unittest.main()



