import os
import unittest
import warnings
from gdal2numpy import *

workdir = justpath(__file__)

filetif = f"{workdir}/CLSA_LiDAR.tif"
fileshp = f"s3://saferplaces.co/test/barrier.shp|barrier"


class Test(unittest.TestCase):
    """
    Tests
    """
    def setUp(self):
        warnings.simplefilter("ignore", ResourceWarning)


    def tearDown(self):
        warnings.simplefilter("default", ResourceWarning)


    # def test_open(self):
    #     """
    #     test_open: 
    #     """
    #     ds = OpenShape(fileshp)
    #     self.assertTrue(ds is not None)


    # def test_features(self):
    #     """
    #     test_srs: 
    #     """
    #     features = GetFeatures(fileshp)
    #     for feature in features:
    #         print(feature)

    
    def test_srs(self):
        """
        test_srs: 
        """
        srs = GetSpatialRef(fileshp)
        print(srs)
        self.assertTrue(srs is not None)


    # def test_copy(self):
    #     """
    #     test_copy
    #     """
    #     fileout = "s3://saferplaces.co/test/barrier_copy.shp"
    #     copy(fileshp, fileout)
    #     self.assertTrue(s3_exists(fileout))

    # def test_upload_s3(self):
    #     """
    #     test_upload_s3: 
    #     """
    #     filetif = f"{workdir}/lidar_rimini_building_2.tif"
    #     filer = "s3://ead.saferplaces.co/test/lidar_rimini_building_2.tif"
    #     # v # self.assertEqual(etag1, etag2)


    # def test_load_from_s3(self):
    #     """
    #     test_s3: 
    #     """
    #     #data, _, _ = GDAL2Numpy("https://s3.us-east-1.amazonaws.com/saferplaces.co/lidar-rer-100m.tif", load_nodata_as=np.nan)
    #     #self.assertEqual(data.shape, (1458, 3616))


    # def test_save_on_s3(self):
    #     """
    #     test_save_on_s3: 
    #     """
    #     print("Save on s3...")
    #     data, gt, prj = GDAL2Numpy(filetif, load_nodata_as=np.nan)
        
    #     fileout = "s3://saferplaces.co/test/test.tif"
    #     Numpy2GTiff(data, gt, prj, fileout, save_nodata_as=-9999, format="GTiff")
    #     self.assertTrue(s3_exists(fileout))


    # def test_save_json(self):
    #     """
    #     test_save_json
    #     """
    #     fileout = "s3://saferplaces.co/test/features.shp"
    #     features = [
    #         {
    #             "type": "Feature",
    #             "properties": {
    #                 "name": "Coors Field",
    #                 "amenity": "Baseball Stadium",
    #             },
    #             "geometry": {
    #                 "type": "Point",
    #                 "coordinates": [-104.99404, 39.75621]
    #             }
    #         }     
    #     ]
    #     ShapeFileFromGeoJSON(features, fileout, t_srs=4326)

    def test_list(self):
        """
        test_list
        """
        #files = s3_list("s3://saferplaces.co/test/*/rain/*.shp")
        files = s3_list("s3://saferplaces.co/eedem/catalog/*.db", etag=True)
        for file in files:
            print(file)
        self.assertEqual(1,1)

if __name__ == '__main__':
    unittest.main()



