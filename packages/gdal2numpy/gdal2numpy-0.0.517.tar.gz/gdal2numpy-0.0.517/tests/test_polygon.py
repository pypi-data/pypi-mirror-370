import os
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

    

    def test_poly_from_string(self):
        """
        test_poly_from_string: 
        """
        coords = "12,44,12.05,44.05"
        
        geom = PolygonFrom(coords)
        minx, maxx, miny, maxy = geom.GetEnvelope()
        self.assertTrue(geom.GetGeometryName() == "POLYGON")
        self.assertTrue(minx == 12)
        self.assertTrue(maxx == 12.05)
        self.assertTrue(miny == 44)
        self.assertTrue(maxy == 44.05)


    def test_poly_from_array(self):
        """
        test_poly_from_array: 
        """
        coords =[12,44,12.05,44.05]

        geom = PolygonFrom(coords)
        minx, maxx, miny, maxy = geom.GetEnvelope()
        self.assertTrue(geom.GetGeometryName() == "POLYGON")
        self.assertTrue(minx == 12)
        self.assertTrue(maxx == 12.05)
        self.assertTrue(miny == 44)
        self.assertTrue(maxy == 44.05)


    def test_poly_from_wkt(self):
        """
        test_poly_from_wkt: 
        """
        wkt = "POLYGON((12 44, 12.05 44.05))"
        
        geom = PolygonFrom(wkt)
        minx, maxx, miny, maxy = geom.GetEnvelope()
        self.assertTrue(geom.GetGeometryName() == "POLYGON")
        self.assertTrue(minx == 12)
        self.assertTrue(maxx == 12.05)
        self.assertTrue(miny == 44)
        self.assertTrue(maxy == 44.05)

    def test_poly_from_raster(self):
        """
        test_poly_from_raster 
        """
        filetif = "https://s3.us-east-1.amazonaws.com/saferplaces.co/packages/gdal2numpy/open/CLSA_LiDAR.tif"
        geom = PolygonFrom(filetif)
        minx, maxx, miny, maxy = geom.GetEnvelope()
        #491922.4277283892 493252.4277283892 5215665.338390054 5217040.338390054
        self.assertTrue(geom.GetGeometryName() == "POLYGON")
        self.assertTrue(minx == 491922.4277283892)
        self.assertTrue(maxx == 493252.4277283892)
        self.assertTrue(miny == 5215665.338390054)
        self.assertTrue(maxy == 5217040.338390054)

    def test_poly_from_shape(self):
        """
        test_poly_from_shape 
        """
        fileshp = "https://s3.us-east-1.amazonaws.com/saferplaces.co/packages/gdal2numpy/open/OSM_BUILDINGS_102258.shp"
        geom = PolygonFrom(fileshp)
        minx, maxx, miny, maxy = geom.GetEnvelope()
        #12.4731569 12.6481555 44.0088292 44.1213122
        self.assertTrue(geom.GetGeometryName() == "POLYGON")
        self.assertTrue(minx == 12.4731569)
        self.assertTrue(maxx == 12.6481555)
        self.assertTrue(miny == 44.0088292)
        self.assertTrue(maxy == 44.1213122)

    def test_poly_from_fid(self):
        """
        test_poly_from_shape 
        """
        fileshp = "https://s3.us-east-1.amazonaws.com/saferplaces.co/packages/gdal2numpy/open/OSM_BUILDINGS_102258.shp|layername=OSM_BUILDINGS_102258|fid=0"
        geom = PolygonFrom(fileshp)
        minx, maxx, miny, maxy = geom.GetEnvelope()
        #12.5611214 12.5619476 44.0597426 44.0605159
        self.assertTrue(geom.GetGeometryName() == "POLYGON")
        self.assertTrue(minx == 12.5611214)
        self.assertTrue(maxx == 12.5619476)
        self.assertTrue(miny == 44.0597426)
        self.assertTrue(maxy == 44.0605159)

    def test_poly_from_nominatim(self):
        """
        test_poly_from_nominatim
        """
        query = "Rome"
        geom = PolygonFrom(query)
        minx, maxx, miny, maxy = geom.GetEnvelope()
        #12.2344669 12.8557603 41.6556417 42.1410285
        self.assertTrue(geom.GetGeometryName() == "MULTIPOLYGON")
        self.assertTrue(minx == 12.2344669)
        self.assertTrue(maxx == 12.8557603)
        self.assertTrue(miny == 41.6556417)
        self.assertTrue(maxy == 42.1410285)

    def test_poly_increase(self):
        """
        test_poly_increase
        """
        coords = "12,44,12.05,44.05"
        geom = PolygonFrom(coords, delta=0.1)
        minx, maxx, miny, maxy = geom.GetEnvelope()
        self.assertTrue(geom.GetGeometryName() == "POLYGON")
        self.assertTrue(minx == 11.995000000000001)
        self.assertTrue(maxx == 12.055)
        self.assertTrue(miny == 43.995)
        self.assertTrue(maxy == 44.055)
       
    def test_poly_into4326(self):
        """
        test_poly_into4326
        """
        filetif = "https://s3.us-east-1.amazonaws.com/saferplaces.co/packages/gdal2numpy/open/CLSA_LiDAR.tif"
        geom = PolygonFrom(filetif, t_srs="EPSG:4326")
        minx, maxx, miny, maxy = geom.GetEnvelope()
        print(minx, miny, maxx, maxy)
        

if __name__ == '__main__':
    unittest.main()
