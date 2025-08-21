# -----------------------------------------------------------------------------
# MIT License:
# Copyright (c) 2012-2024 Luzzi Valerio
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
# Name:        dissolve.py
# Purpose:
#
# Author:      Luzzi Valerio
# Created:     11/11/2024
# -----------------------------------------------------------------------------
from osgeo import gdal, ogr
from .filesystem import tempfilename, juststem
from .module_open import OpenShape

def Dissolve(filein, fileout=None, fieldname="DN", format="ESRI Shapefile"):
    """
    Dissolve: convert a polygon shapefile to a dissolved polygon shapefile.
    """
    fileout = fileout if fileout else tempfilename(suffix=".shp")

    src_ds = OpenShape(filein)
    if src_ds:
        srs = src_ds.GetLayer().GetSpatialRef()
        layer = src_ds.GetLayer()
        driver = ogr.GetDriverByName(format)
        out_ds = driver.CreateDataSource(fileout)
        out_layer = out_ds.CreateLayer(juststem(fileout), srs, geom_type=ogr.wkbPolygon)
        fd = ogr.FieldDefn(fieldname, ogr.OFTInteger)
        out_layer.CreateField(fd)

        # Dissolve the polygons make union of all polygons
        out_layer = out_ds.GetLayer()
        out_layer.StartTransaction()
        for feature in layer:
            geom = feature.GetGeometryRef()
            out_layer_defn = out_layer.GetLayerDefn()
            out_feature = ogr.Feature(out_layer_defn)
            out_feature.SetGeometry(geom)
            out_feature.SetField(fieldname, 1)
            out_layer.CreateFeature(out_feature)
            out_feature = None

        out_layer.CommitTransaction()
        out_ds = None
        return fileout
    return None
