import os
import unittest
import warnings
from gdal2numpy import *


filetif = f"s3://saferplaces.co/packages/gdal2numpy/isfile/CLSA_LiDAR.tif"


class Test(unittest.TestCase):
    """
    Tests
    """

    def setUp(self):
        warnings.simplefilter("ignore", ResourceWarning)

    def tearDown(self):
        warnings.simplefilter("default", ResourceWarning)

    def test_raster_shape(self):
        """
        test_raster: 
        """
        data, _, _ = GDAL2Numpy(filetif, load_nodata_as=np.nan)
        self.assertEqual(data.shape, (1375, 1330))

    def test_pixel_size(self):
        """
        test_pixel_size:
        """
        self.assertEqual(GetPixelSize(filetif), (1.0, 1.0))

    def test_extent(self):
        """
        test_extent: 
        """
        bbox = (491922.4277283892, 5215665.338390054, 493252.4277283892, 5217040.338390054)
        self.assertEqual(GetExtent(filetif), bbox)

    def test_isvalid(self):
        """
        test_isvalid: 
        """
        self.assertTrue(IsValid(filetif))

    def test_cog(self):
        """
        test_cog: 
        """
        fileout = f"{tempdir()}/{justfname(filetif)}"
        data, gt, prj = GDAL2Numpy(filetif, load_nodata_as=np.nan)
        Numpy2GTiff(data, gt, prj, fileout, save_nodata_as=-9999,
                    format="COG", metadata={"UM": "meters", "type": "DTM"})
        cog, _, _ = GDAL2Numpy(fileout, load_nodata_as=np.nan)
        metadata = GetMetaData(fileout)
        os.remove(fileout)
        
        self.assertEqual(metadata["metadata"]["type"], "DTM")
        self.assertEqual(metadata["metadata"]["UM"], "meters")
        self.assertEqual(data.shape, cog.shape)
        

if __name__ == '__main__':
    unittest.main()
