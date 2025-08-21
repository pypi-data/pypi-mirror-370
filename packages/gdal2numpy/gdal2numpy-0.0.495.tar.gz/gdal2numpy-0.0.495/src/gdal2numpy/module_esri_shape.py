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
# Name:        module_esri_shape.py
# Purpose:
#
# Author:      Luzzi Valerio
#
# Created:     31/12/2022
# -------------------------------------------------------------------------------
import os
from osgeo import ogr
from .filesystem import justpath, listify, tempfilename
from .module_open import OpenShape
from .module_s3 import iss3, move, tempname4S3


def CopySchema(fileshp, fileout=None):
    """
    CopySchema
    """
    dsr = OpenShape(fileshp, 0)
    driver = ogr.GetDriverByName("ESRI Shapefile")
    fileout = fileout if fileout else tempfilename(suffix=".shp")
    filetmp = tempname4S3(fileout) if iss3(fileout) else fileout
    os.makedirs(justpath(filetmp), exist_ok=True)
    dsw = driver.CreateDataSource(filetmp)
    if dsr:
        layer1 = dsr.GetLayer()
        layer2 = dsw.CreateLayer(
            layer1.GetName(), layer1.GetSpatialRef(), layer1.GetGeomType())
        # Copying the old layer schema into the new layer
        defn = layer1.GetLayerDefn()
        for j in range(defn.GetFieldCount()):
            layer2.CreateField(defn.GetFieldDefn(j))
    dsr, dsw = None, None
    if iss3(fileout):
        move(filetmp, fileout)
    else:
        fileout = filetmp
    return fileout


def FeatureSelection(fileshp, fileout, fids=None):
    """
    FeatureSelection - Create a new shapefile filtering features
    """
    fileout = CopySchema(fileshp)
    dsr = OpenShape(fileshp, 0)
    dsw = ogr.Open(fileout, 1)
    if dsr and dsw:
        layer1 = dsr.GetLayer()
        layer2 = dsw.GetLayer()
        if fids:
            for fid in listify(fids):
                feature = layer1.GetFeature(int(fid))
                if feature:
                    layer2.CreateFeature(feature)
        else:
            for feature in layer1:
                layer2.CreateFeature(feature)
    dsr, dwr = None, None

    return fileout
