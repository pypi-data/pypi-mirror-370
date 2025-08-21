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
# Name:        gdalwarp.py
# Purpose:
#
# Author:      Luzzi Valerio, Lorenzo Borelli
#
# Created:     16/06/2021
# -------------------------------------------------------------------------------
import os
import subprocess
from osgeo import gdal, gdalconst
from .filesystem import juststem, justpath, tempfilename, listify
from .filesystem import now, total_seconds_from, forceext
from .module_ogr import SameSpatialRef, GetSpatialRef
from .module_meta import GetNoData, GDALFixNoData
from .module_Numpy2GTiff import CalculateStats
from .module_s3 import copy, isfile, move, remove
from .gdal_translate import dtypeOf
from .module_log import Logger


def resampling_method(method):
    """
    reasampling_method translation form text to gdalconst
    """
    algorithms = {
        "near": gdalconst.GRIORA_NearestNeighbour,
        "bilinear": gdalconst.GRIORA_Bilinear,
        "cubic": gdalconst.GRIORA_Cubic,
        "cubicspline": gdalconst.GRIORA_CubicSpline,
        "lanczos": gdalconst.GRIORA_Lanczos,
        "average": gdalconst.GRIORA_Average,
        "rms": gdalconst.GRIORA_RMS,
        "mode": gdalconst.GRIORA_Mode,
        "gauss": gdalconst.GRIORA_Gauss,
    }
    method = method.lower() if isinstance(method, str) else None
    return algorithms.get(method, gdalconst.GRIORA_NearestNeighbour)


def gdalwarp(filelist,
             fileout=None,
             dstSRS="",
             cutline="",
             cropToCutline=False,
             pixelsize=(0, 0),
             resampleAlg="near",
             format="GTiff",
             ot=None,
             dstNodata=None,
             stats=True):
    """
    gdalwarp
    """

    t0 = now()

    filelist = listify(filelist)
    if len(filelist) == 0:
        Logger.warning("gdalwarp: filelist is empty")
        return None

    co = {
        "gtiff": ["BIGTIFF=YES", "TILED=YES", "BLOCKXSIZE=512", "BLOCKYSIZE=512", "COMPRESS=LZW"],
        "cog":   ["BIGTIFF=YES", "COMPRESS=LZW"],
    }

    format = format.lower() if format else "gtiff"

    filetmp = tempfilename(prefix="gdalwarp/tmp_", suffix=".tif")
    # inplace gdalwarp, give the fileout as the first file in the list
    if fileout is None and len(filelist) > 0:
        fileout = filelist[0]
    fileout = fileout if fileout else filetmp

    filelist_tmp = copy(filelist)

    kwargs = {
        # "format": "GTiff",
        # "creationOptions": ["BIGTIFF=YES", "TILED=YES", "BLOCKXSIZE=512", "BLOCKYSIZE=512", "COMPRESS=LZW"],
        "format": format,
        "creationOptions": co.get(format, []),
        # "warpOptions": ["NUM_THREADS=ALL_CPUS", "GDAL_CACHEMAX=512"],
        "resampleAlg": resampling_method(resampleAlg),
        "multithread": True,
    }

    if dstNodata is not None:
        kwargs["dstNodata"] = dstNodata

    # outputType = [-ot {Byte/Int16/UInt16/UInt32/Int32/Float32/Float64/CInt16/CInt32/CFloat32/CFloat64}]
    if ot and ot in dtypeOf:
        ot = ot.lower() if isinstance(ot, str) else ot
        kwargs["outputType"] = dtypeOf[ot]  # gdal.GDT_Float32

    # pixelsize
    pixelsize = listify(pixelsize)
    if len(pixelsize) == 1 and pixelsize[0] != 0:
        kwargs["xRes"] = abs(pixelsize[0])
        kwargs["yRes"] = abs(pixelsize[0])
    elif len(pixelsize) == 2 and pixelsize[0] != 0 and pixelsize[1] != 0:
        kwargs["xRes"] = abs(pixelsize[0])
        kwargs["yRes"] = abs(pixelsize[1])

    if len(filelist) == 1 and SameSpatialRef(filelist_tmp[0], dstSRS):
        Logger.debug("Avoid reprojecting %s", filelist[0])
    elif dstSRS:
        kwargs["dstSRS"] = GetSpatialRef(dstSRS)

    cutline_tmp = None
    if isfile(cutline):
        cutline_tmp = copy(cutline)
        kwargs["cropToCutline"] = cropToCutline
        kwargs["cutlineDSName"] = cutline_tmp
        kwargs["cutlineLayer"] = juststem(cutline_tmp)
    elif isinstance(cutline, (tuple, list)) and len(cutline) == 4:
        kwargs["outputBounds"] = listify(cutline)

    # assert that the folder exists
    os.makedirs(justpath(filetmp), exist_ok=True)
    try:
        gdal.UseExceptions()
        gdal.PushErrorHandler('CPLQuietErrorHandler')
        gdal.Warp(filetmp, filelist_tmp, **kwargs)
    except Exception as ex:
        print("[GDALWARP]",ex)
    finally:
        gdal.PopErrorHandler()

    # patch notdata value
    if dstNodata is not None and GetNoData(filetmp) != dstNodata:
        Logger.debug("gdalwarp: fixing nodata value to %s", dstNodata)
        GDALFixNoData(filetmp, format=format, nodata=dstNodata)

    if stats and isfile(filetmp):
        #subprocess.run(["gdalinfo", "-stats", filetmp], shell=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        #move(f"{filetmp}.aux.xml", f"{fileout}.aux.xml")
        try:
            CalculateStats(filetmp)
        except Exception as ex:
            print(f"[GDALWARP]: error calculating stats: {ex}")
        

    # moving the filetmp to fileout
    move(filetmp, fileout)
    Logger.debug("gdalwarp: converted to %s in %.2fs.",
                 fileout, total_seconds_from(t0))

    # clean the cutline file
    remove(cutline_tmp)

    Logger.debug("gdalwarp: completed in %.2fs.", total_seconds_from(t0))
    # ----------------------------------------------------------------------
    return fileout
