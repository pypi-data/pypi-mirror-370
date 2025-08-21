# -------------------------------------------------------------------------------
# MIT License:
# Copyright (c) 2012-2022 Valerio for Gecosistema S.r.l.
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
# Name:        module_metadata.py
# Purpose:
#
# Author:      Luzzi Valerio, Lorenzo Borelli
#
# Created:
# -------------------------------------------------------------------------------
import os
import numpy as np
from osgeo import gdal, gdalconst
from .filesystem import forceext, filetojson, remove
from .module_s3 import isfile, israster, isshape
from .module_GDAL2Numpy import GDAL2Numpy
from .module_Numpy2GTiff import Numpy2GTiff
from .module_features import GetRange
from .module_ogr import GetExtent
from .module_open import OpenRaster
from .module_xml import parseQMD, writeQMD

def GetRasterShape(filename):
    """
    GetRasterShape
    """
    ds = OpenRaster(filename)
    if ds:
        m, n = ds.RasterYSize, ds.RasterXSize
        return m, n
    return 0, 0


def GetTransform(filename):
    """
    GetTransform
    """
    ds = OpenRaster(filename)
    if ds:
        gt = ds.GetGeoTransform()
        return gt
    return None


def GetNoData(filename, band=1):
    """
    GetNoData
    """
    ds = OpenRaster(filename)
    if ds:
        # check if band exists
        if band > 0 and band <= ds.RasterCount:
            bandx = ds.GetRasterBand(band)
            return bandx.GetNoDataValue()
    return None


def SetNoData(filename, nodata):
    """
    SetNoData
    """
    ds = OpenRaster(filename, gdalconst.GA_Update)
    if ds:
        band = ds.GetRasterBand(1)
        nodata = band.SetNoDataValue(nodata)
        data, band, ds = None, None, None
    return None


def GDALFixNoData(filename, format="GTiff", nodata=-9999):
    """
    GDALFixNoData
    """
    if isfile(filename):
        data, gt, prj = GDAL2Numpy(filename, load_nodata_as=nodata)
        data[abs(data) >= 1e10] = nodata
        Numpy2GTiff(data, gt, prj, filename,
                    format=format, save_nodata_as=nodata)
        return filename
    return False


def IsEmpty(filename, nodata=-9999):
    """
    IsEmpty - check all values are nodata
    """
    if isfile(filename):
        ds = OpenRaster(filename)
        if ds:
            band = ds.GetRasterBand(1)
            nodata = band.GetNoDataValue()
            data = band.ReadAsArray()
            data[np.isnan(data)] = nodata
            data[abs(data) >= 1e10] = nodata
            ds = None
            return np.all(data == nodata)
    return False


def GetMinMax(filename, fieldname=None):
    """
    GetMinMax
    """
    if israster(filename):
        data, _, _ = GDAL2Numpy(filename)
        return np.nanmin(data), np.nanmax(data)
    elif isshape(filename):
        return GetRange(filename, fieldname)

    return np.Inf, -np.Inf


def read_metadata(filename):
    """
    read_metadata
    """
    filemta = forceext(filename, "mta")
    fileqmd = forceext(filename, "qmd")
    # legacy
    if os.path.isfile(filemta):
        return filetojson(filemta)
    # standard qgis metadata = qmd
    elif os.path.isfile(fileqmd):
        return parseQMD(fileqmd)
    return {"metadata": {}}


def save_metadata(metadata, filename):
    """
    save_metadata
    """
    if filename:
        # legacy
        # filemeta = forceext(filename, "mta")
        # jsontofile(metadata, filemeta)
        # --- save to .qmd ---
        writeQMD(filename, metadata)
        #
        #patch
        fileqmd = forceext(filename, "qmd")
        if isfile(fileqmd):
            filemeta = forceext(filename, "mta")
            remove(filemeta)
        # --- end patch ---

def GetMetaData(filename):
    """
    GetMetaData - get metadata from filename
    :param filename: the pathname
    :return: returns a dictionary with metadata
    """
    if israster(filename):
        ds = OpenRaster(filename)
        if ds:
            m, n = ds.RasterYSize, ds.RasterXSize
            band = ds.GetRasterBand(1)
            gt = ds.GetGeoTransform()
            wkt = ds.GetProjection()
            meta = ds.GetMetadata()
            nodata = band.GetNoDataValue()
            minx, px, _, maxy, _, py = gt
            maxx = minx + n * px
            miny = maxy + m * py
            miny, maxy = min(miny, maxy), max(miny, maxy)
            ds = None
            return {
                "m": m,
                "n": n,
                "px": px,
                "py": py,
                "wkt": wkt,
                "nodata": nodata,
                "extent": [minx, miny, maxx, maxy],
                "metadata": meta
            }
    elif isshape(filename):
        return read_metadata(filename)

    return {}


def GetTag(filename, tagname, band=0):
    """
    GetTag - get a tag in metadata of the file or of the band if specified
    """
    if israster(filename):
        ds = OpenRaster(filename)
        if ds:
            if not band:
                metadata = ds.GetMetadata()
            elif 0 < band <= ds.RasterCount:
                metadata = ds.GetRasterBand(band).GetMetadata()
            else:
                metadata = {}
            if tagname in metadata:
                ds = None
                return metadata[tagname]
            ds = None
    elif isshape(filename):
        meta = read_metadata(filename)
        if meta and "metadata" in meta and tagname in meta["metadata"]:
            return meta["metadata"][tagname]

    return None


def SetTag(filename, tagname, tagvalue="", band=0):
    """
    SetTag - set a tag in metadata of the file or of the band if specified
    """
    if israster(filename):
        gdal.DontUseExceptions()
        ds = OpenRaster(filename) #, gdalconst.GA_Update)
        if ds:
            if tagname:
                if not band:
                    metadata = ds.GetMetadata()
                    metadata[tagname] = f"{tagvalue}"
                    ds.SetMetadata(metadata)
                elif 0 < band <= ds.RasterCount:
                    metadata = ds.GetRasterBand(band).GetMetadata()
                    metadata[tagname] = f"{tagvalue}"
                    ds.GetRasterBand(band).SetMetadata(metadata)
            ds.FlushCache()
            ds = None

    elif isshape(filename):
        filemeta = forceext(filename, "mta")
        meta = {"metadata": {}}
        if os.path.isfile(filemeta):
            meta = read_metadata(filename)
        if "metadata" in meta:
            meta["metadata"][tagname] = tagvalue
            save_metadata(meta, filename)


def SetTags(filename, meta, band=0):
    """
    SetTags - set tags metadata of the file or of the band if specified
    """
    if israster(filename):
        ds = OpenRaster(filename, gdalconst.GA_Update)
        if ds:
            for tagname in meta:
                tagvalue = meta[tagname]
                if not band:
                    metadata = ds.GetMetadata()
                    metadata[tagname] = f"{tagvalue}"
                    ds.SetMetadata(metadata)
                elif 0 < band <= ds.RasterCount:
                    metadata = ds.GetRasterBand(band).GetMetadata()
                    metadata[tagname] = f"{tagvalue}"
                    ds.GetRasterBand(band).SetMetadata(metadata)
            ds.FlushCache()
            ds = None

    elif isshape(filename):
        mta = read_metadata(filename)
        # update mta from meta
        for tagname in meta:
            tagvalue = meta[tagname]
            if "metadata" in mta:
                mta["metadata"][tagname] = tagvalue
        save_metadata(mta, filename)


def setExtent(fileshp):
    """
    setExtent - set extent of a shapefile
    """
    if isshape(fileshp):
        extent = GetExtent(fileshp)
        mta = read_metadata(fileshp)
        if "metadata" in mta:
            mta["metadata"]["extent"] = {
                "minx": extent[0],
                "miny": extent[1],
                "maxx": extent[2],
                "maxy": extent[3]
            }
        save_metadata(mta, fileshp)
