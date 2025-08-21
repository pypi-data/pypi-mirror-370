# -------------------------------------------------------------------------------
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
# Name:        module_xml.py
# Purpose:
#
# Author:      Luzzi Valerio
#
# Created:     20/06/2024
# -------------------------------------------------------------------------------
import xmltodict
from .filesystem import forceext, listify
from .module_s3 import isfile, isshape
from .module_ogr import GetSpatialRef, AutoIdentify, GetExtent

def parseXML(filename):
    """
    parseXML - parse an XML file and return a Python dictionary
    """
    try:
        # Open and read the XML file
        with open(filename, 'r') as f:
            xml = f.read()

        # Convert XML to a Python dictionary
        return xmltodict.parse(xml)
    except Exception as e:
        print(f"Error: {e}")
    return {}


def parseQMD(filename):
    """
    parseQMD - parse a QMD file and return a Python dictionary
    """
    res = {"metadata": {}}
    fileqmd = forceext(filename, "qmd")
    metadata = parseXML(fileqmd)
    if metadata:
        qgis = metadata["qgis"] if "qgis" in metadata else {}
        if qgis and "keywords" in qgis:
            keywords = listify(qgis["keywords"])
            for item in keywords:
                key = item["@vocabulary"]
                value = item["keyword"]
                res["metadata"][key] = value
    return res


def writeXML(data, filename):
    """
    writeXML - write a Python dictionary to an XML file
    """
    try:
        # Convert Python dictionary to XML
        xml = xmltodict.unparse(data, pretty=True,)
        xml = xml.replace("<?xml version=\"1.0\" encoding=\"utf-8\"?>",
                          "<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>")
        # Write the XML to a file
        with open(filename, 'w') as f:
            f.write(xml)

    except Exception as e:
        print(f"Error: {e}")


def writeQMD(filename, metadata=None):
    """
    writeQMD - write a QMD file
    """
    fileshp = forceext(filename, "shp")
    fileqmd = forceext(filename, "qmd")
    if isshape(fileshp):
        # Create a Python dictionary
        srs = GetSpatialRef(fileshp)
        authid = AutoIdentify(fileshp)
        minx, miny, maxx, maxy = GetExtent(fileshp)

        keywords = []
        metadata = metadata if metadata else {}

        # integrate the metadata with parsed data
        if isfile(fileqmd):
            qmd = parseQMD(fileshp)
            metadata.update(qmd["metadata"])

        # Convert metadata to keywords
        for key, value in metadata.items():
            keywords.append({"@vocabulary": key, "keyword": value})

        data = {
            "qgis": {
                "@version": "3.28.0-Firenze",
                "identifier": None,
                "parentidentifier": None,
                "language": None,
                "type": "dataset",
                "title": None,
                "abstract": None,
                "keywords": keywords,
                "contact": {
                    "name": None,
                    "organization": None,
                    "position": None,
                    "voice": None,
                    "fax": None,
                    "email": None,
                    "role": None
                },
                "links": None,
                "history": None,
                "fees": None,
                "rights": [],
                "license": [],
                "encoding": None,
                "crs": {
                    "spatialrefsys": {
                        "@nativeFormat": "Wkt",
                        "wkt":   srs.ExportToWkt(),
                        "proj4": srs.ExportToProj4(),
                        "srsid": None,
                        "srid": authid.split(":")[1],
                        "authid": authid,
                        "description": srs.GetName(),
                        "projectionacronym": "longlat",
                        "ellipsoidacronym": "EPSG:7030",
                        "geographicflag": True if srs.IsGeographic() else False
                    }
                },
                "extent": {
                    "spatial": {
                        "@dimensions": "2",
                        "@crs": authid,
                        "@minx": minx,
                        "@maxy": maxy,
                        "@maxx": maxx,
                        "@maxz": 0,
                        "@miny": miny,
                        "@minz": 0
                    },
                    "temporal": {
                        "period": {
                            "start": None,
                            "end": None
                        }
                    }
                }# end extent
            }# end qgis
        }# end data

        # Write the QMD file
        writeXML(data, fileqmd)


def SetTagQMD(filename, tagname, tagvalue):
    """
    SetTag - set a tag in metadata of the file or of the band if specified
    """
    fileshp = forceext(filename, "shp")
    fileqmd = forceext(filename, "qmd")
    if isshape(fileshp):
        # read the xml file if it exists
        if not isfile(fileqmd):
            writeQMD(fileqmd)

        data = parseXML(fileqmd)
        #data[tagname] = tagvalue
        if "keywords" not in data["qgis"]:
            data["qgis"]["keywords"] = []

        data["qgis"]["keywords"].append({
            "@vocabulary": tagname,
            "keyword": tagvalue
        })
        writeXML(data, fileqmd)
