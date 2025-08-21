import os
import unittest
import numpy as np
from gdal2numpy import *



class Test(unittest.TestCase):
    """
    Tests
    """
    def test_polygonize(self):
        """
        test_polygonize  
        """

        filetif = "s3://saferplaces.co/packages/gdal2numpy/polygonize/wd.tif"
        #filetif= "c:/Users/vlr20/Downloads/WD_RAIN190051.tif"
        fileout = f"{tempdir()}/{juststem(filetif)}.shp"
        fileout = Polygonize(filetif, fileout, threshold=0.5, format="ESRI Shapefile")
        self.assertTrue(os.path.isfile(fileout))
        ogr_remove(fileout)
        


   
if __name__ == '__main__':
    unittest.main()



