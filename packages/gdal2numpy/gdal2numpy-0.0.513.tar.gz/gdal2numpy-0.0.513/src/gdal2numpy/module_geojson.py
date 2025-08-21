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
# Name:        module_flow.py
# Purpose:
#
# Author:      Luzzi Valerio
#
# Created:     06/07/2023
# -------------------------------------------------------------------------------
import os
import json
import numpy as np
from osgeo import ogr
from .filesystem import justpath
from .module_ogr import GetSpatialRef
from .module_s3 import *

def isInteger(value):
    """
    isInteger
    """
    return isinstance(value, (int, np.int8, np.int16, np.int32, np.int64, np.uint8, np.uint16, np.uint32, np.uint64))

def isFloat(value):
    """
    isFloat
    """
    return isinstance(value, (float, np.float32, np.float64))


def infer_geometry_type(features):
    """
    infer_geometry_type
    """
    if features:
        first = features[0]
        geom = ogr.CreateGeometryFromJson(json.dumps(first["geometry"]))
        geom_type = geom.GetGeometryType()
        geom.Destroy()
        return geom_type
    return ogr.wkbUnknown


def infer_width(features, fieldname, default_width=6):
    """
    infer_width
    """
    width = default_width
    int_part = 0
    precision = 0
    coma = 0
    for feature in features:
        fieldvalue = feature["properties"][fieldname]
        if isinstance(fieldvalue, float) and "." in f"{fieldvalue}":
            coma = 1
            precision = max(len(f"{fieldvalue}".split(".")[-1]), precision)
        int_part = max(len(f"{fieldvalue}".split(".")[0]), int_part)

    width = int_part+coma+precision
    return width, precision


def infer_layerDefn(features):
    """
    infer_layerDefn
    """
    fields = []
    if features:

        first = features[0]

        for fieldname in first["properties"]:
            fid = 0
            fieldvalue = features[fid]["properties"][fieldname]
            while fieldvalue is None and fid < len(features)-1:
                fid += 1
                fieldvalue = features[fid]["properties"][fieldname]

            width, precision = infer_width(features, fieldname)

            # infer field type from value
            if isInteger(fieldvalue):
                fieldtype = ogr.OFTInteger
            elif isFloat(fieldvalue):
                fieldtype = ogr.OFTReal
            else:
                fieldtype = ogr.OFTString

            newfield = ogr.FieldDefn(fieldname, fieldtype)
            newfield.SetWidth(width)
            newfield.SetPrecision(precision)
            fields.append(newfield)
    return fields


def ShapeFileFromGeoJSON(features, fileout="", t_srs=4326):
    """
    ShapeFileFromGeoJSON
    """
    fileshp = fileout or f"{justpath(__file__)}/temp.shp"
    _, fileshp = get_bucket_name_key(fileshp)
    os.makedirs(justpath(fileshp), exist_ok=True)

    if features:

        # case 1: features is a list of features
        if isinstance(features, (list, tuple)):
            pass
        # case 2: features is a dict with type FeatureCollection
        elif isinstance(features, dict) and features["type"] == "FeatureCollection":
            if "crs" in features:
                t_srs = features["crs"]["properties"]["name"]
            features = features["features"]
        # case 3: features is a geojson file name
        elif isinstance(features, str) and isfile(features):
            filetmp = copy(features) if iss3(features) else features
            with open(filetmp, "r") as fp:
                text = fp.read()
                if "FeatureCollection" in text:
                    FeatureCollection = json.loads(text)
                    if "crs" in FeatureCollection:
                        t_srs = FeatureCollection["crs"]["properties"]["name"]
                    features = FeatureCollection["features"]
                else:
                    features = text.split("\n")
                    features = [json.loads(feature)
                                for feature in features if feature]
        else:
            Logger.error(f"features type not supported: {type(features)}")
            return
        # detect geometry type from first feature
        first = features[0]
        geom = ogr.CreateGeometryFromJson(json.dumps(first["geometry"]))
        geom_type = geom.GetGeometryType()
        geom.Destroy()
        # create spatial reference
        t_srs = GetSpatialRef(t_srs)

        # create shapefile
        # - if exists, delete
        driver = ogr.GetDriverByName("ESRI Shapefile")
        if os.path.exists(fileshp):
            driver.DeleteDataSource(fileshp)

        # - create new shapefile
        ds = driver.CreateDataSource(fileshp)
        layer = ds.CreateLayer(fileshp, geom_type=geom_type, srs=t_srs)

        # Create the cpg file
        with open(forceext(fileshp,"cpg"), "w") as fp:
            fp.write("UTF-8")
        
        # create fields from first feature
        fields = infer_layerDefn(features)
        for field in fields:
            layer.CreateField(field)

        featureDefn = layer.GetLayerDefn()
        for feature in features:
            # Create the feature and set value
            geom = feature["geometry"]
            geom = ogr.CreateGeometryFromJson(json.dumps(geom))
            ogr_feature = ogr.Feature(featureDefn)
            ogr_feature.SetGeometry(geom)
            for field in fields:
                fieldname = field.GetName()
                fieldvalue = feature["properties"][fieldname]
                ogr_feature.SetField(fieldname, fieldvalue)

            layer.CreateFeature(ogr_feature)
            ogr_feature = None

        ds.Destroy()

        if iss3(fileout):
            move(fileshp, fileout)
