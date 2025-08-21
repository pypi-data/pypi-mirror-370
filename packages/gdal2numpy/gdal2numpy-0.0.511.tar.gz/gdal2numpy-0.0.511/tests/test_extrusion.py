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


    def test_extrusion(self):
        """
        test_extrusion: 
        """
        filetif = f"{workdir}/data/CLSA_LiDAR.tif"
        fileshp = f"{workdir}/data/bluespots3035.shp"
        fileout = f"{workdir}/data/CLSA_LiDAR(1).tif"
        # Extrusion
        
        dem, gt, prj = raster_edit(filetif, fileshp, fileout, fieldname="height", mode="add", format="COG")
 
        self.assertTrue(True)




if __name__ == '__main__':
    unittest.main()



