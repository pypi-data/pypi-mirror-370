# -------------------------------------------------------------------------------
# MIT License:
# Copyright (c) 2012-2021 Luzzi Valerio
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
#
# Name:        rasterlike.py
# Purpose:
#
# Author:      Luzzi Valerio, Lorenzo Borelli
#
# Created:     16/06/2021
# -------------------------------------------------------------------------------
import numpy as np
from .filesystem import tempfilename, remove
from .module_ogr import SamePixelSize, SameSpatialRef, GetSpatialRef, GetExtent, SameExtent
from .module_ogr import Rectangle, GetPixelSize
from .module_s3 import isfile, israster
from .module_GDAL2Numpy import GDAL2Numpy
from .module_Numpy2GTiff import Numpy2GTiff
from .gdalwarp import gdalwarp
from .module_log import Logger
from .gdal_translate import gdal_translate

# TODO: integrate RasterizeLike and RasterLike into a single function
# def RasterizeLike(fileshp, filedem, fileout="",  burn_fieldname=None, z_value=None, factor=1.0, nodata=None, buf=0.0, all_touched=False):

def RasterLike(filename, filetpl, fileout=None, dtype=None, resampleAlg="near",
                nodata=None,
                #burn_fieldname=None, z_value=None, factor=1.0, buf=0.0, all_touched=False,
                format="GTiff",
                verbose=False):
    """
    RasterLike: adatta un raster al raster template ( dem ) ricampionando, 
    riproiettando estendendo/clippando il file raster se necessario.
    """
    Logger.debug("0)RasterLike...")
    fileout = fileout if fileout else tempfilename(suffix=".tif")

    # is raster file
    if israster(filename):
        if SameSpatialRef(filename, filetpl) and \
            SamePixelSize(filename, filetpl, decimals=2) and \
                SameExtent(filename, filetpl, decimals=3):
            Logger.debug("Files have the same srs, pixels size and extent!")
            fileout = filename
            return fileout

        srs_tpl = GetSpatialRef(filetpl)
        # Tiff extent
        tif_minx, tif_miny, tif_maxx, tif_maxy = GetExtent(filename, srs_tpl)
        # Template extent
        tpl_minx, tpl_miny, tpl_maxx, tpl_maxy = GetExtent(filetpl)
        # Template extent 10% larger
        delta = 0.1
        tif_rectangle = Rectangle(tif_minx, tif_miny, tif_maxx, tif_maxy)
        tpl_rectangle = Rectangle(tpl_minx, tpl_miny, tpl_maxx, tpl_maxy)
        crp_rectangle = Rectangle(tpl_minx, tpl_miny, tpl_maxx, tpl_maxy, delta)


        # 0) Preliminary first coarse crop to speed up the process
        # Just if the tif is 4 times larger than the template
        if tif_rectangle.Intersects(tpl_rectangle) and \
            tif_rectangle.GetArea()/tpl_rectangle.GetArea() > 4:
                crp_minx, crp_maxx, crp_miny, crp_maxy = crp_rectangle.GetEnvelope()
                file_warp0 = gdal_translate(filename, projwin=(crp_minx, crp_maxy, crp_maxx, crp_miny), projwin_srs=srs_tpl)
                remove_file_warp0 = True
        else:
            #Otherwise just use the original tif
            file_warp0 = filename
            remove_file_warp0 = False

        # 1) Second gdalwarp to resample and reproject the tif to the template
        # defined the fileout because the gdalwarp otherwise will work inplace
        file_warp1 = tempfilename(suffix=".warp1.tif")
        file_warp1 = gdalwarp([file_warp0], fileout=file_warp1, dstSRS=srs_tpl,
                            pixelsize=GetPixelSize(filetpl, um=None),
                            resampleAlg=resampleAlg)

        tif_minx, tif_miny, tif_maxx, tif_maxy = GetExtent(file_warp1)
        tif_rectangle = Rectangle(tif_minx, tif_miny, tif_maxx, tif_maxy)

        # 2) Final fine crop to the template extent
        # Note that the projwin has tpl_maxy an tpl_miny inverted
        if tif_rectangle.Intersects(tpl_rectangle):
            fileout = gdal_translate(file_warp1, fileout=fileout, projwin=tpl_rectangle, projwin_srs=srs_tpl,  ot=dtype, a_nodata=nodata)
        else:
            wdata, gt, prj = GDAL2Numpy(
                filetpl, band=1, dtype=dtype, load_nodata_as=np.nan)
            wdata.fill(np.nan)
            Numpy2GTiff(wdata, gt, prj, fileout, save_nodata_as=nodata, format=format)

        # Create temp files
        if remove_file_warp0:
            remove(file_warp0)

        remove(file_warp1)
    
    return fileout if isfile(fileout) else None