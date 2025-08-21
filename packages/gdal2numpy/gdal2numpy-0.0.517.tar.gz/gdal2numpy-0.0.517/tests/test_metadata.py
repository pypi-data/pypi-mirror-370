import unittest
from gdal2numpy import *

workdir = justpath(__file__)

fileshp = f"{workdir}/OSM_BUILDINGS_091244.shp"
filetif = f"{workdir}/CLSA_LiDAR.tif"

class TestMetadata(unittest.TestCase):
    """
    Tests for the TestMetadata function
    """
    def test_metadata_vector(self):
        """
        test_metadata: 
        """
        tag = "buildings"
        SetTag(fileshp, "type", tag)
        self.assertEqual(GetTag(fileshp, "type"), tag)

    def test_metadata_raster(self):
        """
        test_metadata: 
        """
        tag = "dtm"
        SetTag(filetif, "type", tag)
        self.assertEqual(GetTag(filetif, "type"), tag)
   
    


if __name__ == '__main__':
    unittest.main()



