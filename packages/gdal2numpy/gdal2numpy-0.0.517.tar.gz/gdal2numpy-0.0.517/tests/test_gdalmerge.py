import os,warnings
import unittest
from gdal2numpy import *
import inspect

workdir = justpath(__file__)


def average(in_ar, out_ar, xoff, yoff, xsize, ysize, raster_xsize, raster_ysize, buf_radius, gt, **kwargs):
    """
    average - average the input arrays
    """
    nodata_value = -9999.0
    # Initialize the output array with NoData value
    tmp = np.empty_like(out_ar)
    tmp.fill(nodata_value)
    for arr in in_ar:
        arr[np.isnan(arr)] = nodata_value
        tmp[tmp == nodata_value] = arr[tmp == nodata_value]
    out_ar[:] = tmp[:]

class Test(unittest.TestCase):
    """
    Tests
    """
    def setUp(self):
        warnings.simplefilter("ignore", ResourceWarning)

    def tearDown(self):
        warnings.simplefilter("default", ResourceWarning)



    def test_gdal_merge(self):
        """
        test_gdal_merge
        """
        #set_log_level(verbose=True,debug=True)
        
        file1 = f"{workdir}/12_2k_0015.tif"
        file2 = f"{workdir}/12_2k_0016.tif"
        fileout = f"{workdir}/12_2k_0015_0016.tif"

        wkdir = "c:\\users\\vlr20\\Downloads"
        file1 = f"{wkdir}/water_depth_bacino4.tif"
        file2 = f"{wkdir}/water_depth_bacino5.tif"
        fileout = f"{wkdir}/water_depth_bacino4_5.tif"
        fileout = gdal_merge([file1, file2], fileout)
        #gdal.BuildVRT(f"{wkdir}/tmp.vrt", [file1, file2], **{"srcNodata": -9999, "VRTNodata": -9999, "resampleAlg": "hello"})

        



if __name__ == '__main__':
    unittest.main()



