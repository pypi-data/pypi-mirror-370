import json
import unittest
import warnings
from gdal2numpy import *

workdir = justpath(__file__)

filetif = f"{workdir}/data/CLSA_LiDAR.tif"


class Test(unittest.TestCase):
    """
    Tests
    """
    def setUp(self):
        warnings.simplefilter("ignore", ResourceWarning)


    def tearDown(self):
        warnings.simplefilter("default", ResourceWarning)


    def test_xml(self):
        """
        test_xml: 
        """
        fileshp = "tests/pourpoints.shp"
        fileqmd = f"tests/OSM_BUILDINGS_091244.qmd"
        #data = parseXML(f"tests/{fileqmd}")

        writeQMD(fileqmd, {"hello": "world"})
                
        #writeQMD(fileshp)
        self.assertTrue(True)




if __name__ == '__main__':
    unittest.main()



