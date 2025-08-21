import unittest
from gdal2numpy import *

fileshp = f"{justpath(__file__)}/pourpoints.shp"
class TestFeatures(unittest.TestCase):
    """
    Tests for the TestFeatures function
    """
    def test_addfield(self):
        """
        test_addfield: test that the function returns the correct field names
        """
        AddField(fileshp, "fdamage",  dtype=str, defaultValue="hello world") 
        cols = GetFieldNames(fileshp)
        self.assertIn("fdamage", cols)


if __name__ == '__main__':
    unittest.main()



