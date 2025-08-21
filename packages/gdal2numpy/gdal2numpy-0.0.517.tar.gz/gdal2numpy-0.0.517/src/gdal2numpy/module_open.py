# -------------------------------------------------------------------------------
# MIT License:
# Copyright (c) 2012-2023 Luzzi Valerio
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
# Name:        module_features.py
# Purpose:
#
# Author:      Luzzi Valerio
#
# Created:     31/12/2022
# -------------------------------------------------------------------------------
import os
from osgeo import ogr, gdal
from .filesystem import filetostr, normshape
from .module_log import Logger
from .module_s3 import isshape, israster, s3_get
from .module_http import http_get

def get(uri):
    """
    OpenText
    """
    if isinstance(uri, str):
        if os.path.isfile(uri):
            return filetostr(uri)
        elif uri.startswith("http"):
            return http_get(uri, mode="text")
        elif uri.startswith("s3://"):
            return s3_get(uri)
    return None

def is_cog(filename):
    """
    is_cog - check if the file is a COG
    """
    ds = OpenRaster(filename)
    if ds:
        img_struct = ds.GetMetadata("IMAGE_STRUCTURE") or {}
        res = img_struct.get("LAYOUT", "").upper() == "COG"
        Logger.debug("is_cog(%s) = %s", filename, res)
        ds = None
        return res
    return False

def OpenShape(fileshp, exclusive=False):
    """
    OpenDataset
    """
    if not fileshp:
        Logger.debug("0) %s...", fileshp)
        ds = None
    elif isinstance(fileshp, str) and fileshp.startswith("http")  and ".shp" in fileshp.lower():
        Logger.debug("1) Inspect file from https...")
        fileshp = normshape(fileshp)
        ds = ogr.Open(f"/vsicurl/{fileshp}",exclusive)
    elif isinstance(fileshp, str) and os.path.isfile(fileshp) and ".shp" in fileshp.lower():
        Logger.debug("2) Opening local %s...", fileshp)
        fileshp = normshape(fileshp)
        ds = ogr.Open(fileshp, exclusive)
    elif isinstance(fileshp, str) and isshape(fileshp):
        Logger.debug("3) Get file from s3...")
        fileshp = fileshp.replace("s3://", "/vsis3/")
        fileshp = normshape(fileshp)
        ds = ogr.Open(fileshp, exclusive)
    elif isinstance(fileshp, ogr.DataSource) and GetAccess(fileshp) >= exclusive:
        Logger.debug("4) Dataset already open...")
        ds = fileshp
    elif isinstance(fileshp, ogr.DataSource) and GetAccess(fileshp) < exclusive:
        Logger.debug("5) Change the open mode: Open(%s)", exclusive)
        ds = ogr.Open(fileshp.GetName(), exclusive)
    else:
        Logger.debug("999) %s is not a valid shapefile", fileshp)
        ds = None
    return ds


def GetAccess(ds):
    """
    GetAccess - return the open mode exclusive or shared
    trying to create/delete a field
    """
    res = -1
    if ds:
        ogr.UseExceptions()
        try:
            layer = ds.GetLayer()
            layer.CreateField(ogr.FieldDefn("__test__", ogr.OFTInteger))
            j = layer.GetLayerDefn().GetFieldIndex("__test__")
            layer.DeleteField(j)
            res = 1
        except Exception as ex:
            Logger.error(ex)
            res = 0
        ogr.DontUseExceptions()
    return res


def OpenRaster(filename, update=0):
    """
    OpenRaster
    """
    if not filename:
        return None
    elif isinstance(filename, str) and israster(filename):
       
        if os.path.isfile(filename):
            pass
        elif filename.lower().startswith("/vsis3/"):
            pass
        elif filename.lower().startswith("http"):
            filename = f"/vsicurl/{filename}"
        elif filename.lower().startswith("s3://"):
            filename = filename.replace("s3://", "/vsis3/")
        elif ".zip/" in filename.lower():
            filename = f"/vsizip/{filename}"
        elif ".gz/" in filename.lower():
            filename = f"/vsigzip/{filename}"
        elif ".tar/" in filename.lower():
            filename = f"/vsitar/{filename}"
        elif ".tar.gz/" in filename.lower():
            filename = f"/vsitar/{filename}"
        elif ".tgz/" in filename.lower():
            filename = f"/vsitar/{filename}"
        elif ".7z/" in filename.lower():
            filename = f"/vsi7z/{filename}"
        elif ".rar/" in filename.lower():
            filename = f"/vsirar/{filename}"
    elif isinstance(filename, gdal.Dataset):
        return filename
    else:
        return None
    
    gdal.UseExceptions()
    if update and is_cog(filename):
        # open in update mode
        ds = gdal.OpenEx(filename, update, open_options=['IGNORE_COG_LAYOUT_BREAK=YES'])
    else:
        # open in read-only mode
        ds = gdal.Open(filename, update)

    return ds
