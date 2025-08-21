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

    def test_address(self):
        """
        test_address: 
        """
        address = "via delle Piante 4, Rimini"
        result = geolocate(address)
        print(result)
        self.assertFalse(not result)
        

    
   

if __name__ == '__main__':
    unittest.main()



