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
# Name:        polygonize.py
# Purpose:
#
# Author:      Luzzi Valerio
# Created:     11/11/2024
# -----------------------------------------------------------------------------
from osgeo import gdal, ogr
from .module_open import OpenRaster
from .module_log import Logger
from .module_ogr import GetSpatialRef
from .filesystem import tempfilename, juststem


def Polygonize(filetif, fileout=None, fieldname="DN", threshold=0, format="ESRI Shapefile"):
    """
    Poligonize: convert a raster file to a polygon shapefile.
    """
    fileout = fileout if fileout else tempfilename(suffix=".shp")

    src_ds = OpenRaster(filetif)
    if src_ds:
        srs = GetSpatialRef(filetif)
        src_band = src_ds.GetRasterBand(1)
        # Create a memory OGR datasource to put results in.
        driver = ogr.GetDriverByName(format)
        out_ds = driver.CreateDataSource(fileout)
        #layer = ds.CreateLayer(juststem(fileshp), srs, geom_type=geom_type)
        layer = out_ds.CreateLayer(juststem(fileout), srs, ogr.wkbPolygon, options=['ENCODING=UTF-8'])
        fd = ogr.FieldDefn(fieldname, ogr.OFTInteger)
        layer.CreateField(fd)

        # Use 8-connectedness
        options = ['8CONNECTED=8']

        # Create a mask for pixels > 0
        mask_data = src_band.ReadAsArray() >= threshold  # Mask for values > 0
        
        Logger.debug("0)Mask...")
        # Convert the mask to a temporary GDAL memory raster
        mask_ds = gdal.GetDriverByName('MEM').Create('', src_band.XSize, src_band.YSize, 1, gdal.GDT_Byte)
        
        mask_ds.SetGeoTransform(src_ds.GetGeoTransform())
        mask_ds.SetProjection(src_ds.GetProjection())
        mask_band_out = mask_ds.GetRasterBand(1)
        mask_band_out.WriteArray(mask_data)
        mask_band_out.SetNoDataValue(0)  # Set the mask no-data value

        # run the algorithm.
        fieldidx = layer.GetLayerDefn().GetFieldIndex(fieldname)
        Logger.debug("1)Poligonize...")
        #result = gdal.Polygonize(src_band, src_band.GetMaskBand() , layer, fieldidx, options)
        result = gdal.Polygonize(mask_band_out, mask_band_out, layer, fieldidx, options)

        # Close the datasets
        mask_ds = None
        out_ds = None
        src_ds = None

        if result != 0:
            Logger.error("Error in Polygonize!")
            return None

    return fileout