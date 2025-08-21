import unittest
from gdal2numpy import *

fileshp = f"{justpath(__file__)}/data/pourpoints.shp"
class TestOGR(unittest.TestCase):
    """
    Tests for the TestFeatures function
    """

    def test_GetSpatialRef(self):
        """
        test_get_fieldnames: test that the function returns the correct field names
        """
        srs = GetSpatialRef("EPSG:4326")
        print(srs)
        self.assertTrue(srs is not None)


    


if __name__ == '__main__':
    unittest.main()



