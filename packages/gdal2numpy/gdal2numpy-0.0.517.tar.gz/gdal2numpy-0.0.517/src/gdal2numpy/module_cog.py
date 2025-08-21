# -----------------------------------------------------------------------------
# MIT License:
# Copyright (c) 2012-2022 Luzzi Valerio
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
# Name:        module_cog.py
# Purpose:
#
# Author:      Luzzi Valerio
#
# Created:     25/10/2024
# -----------------------------------------------------------------------------
import numpy as np
from .module_ogr import PolygonFrom
from .module_GDAL2Numpy import GDAL2Numpy
from .module_Numpy2GTiff import Numpy2GTiff
from .module_s3 import isfile
from .filesystem import tempfilename

def CogDownload(url, bbox, bbox_srs=4326, format="GTiff", fileout=None):
    """
    CogDownload
    """
    geom = PolygonFrom(bbox)
    fileout = fileout or tempfilename(prefix="gdal2numpy/tmp_", suffix=".tif")
    minlon, maxlon, minlat, maxlat = geom.GetEnvelope()
    data, gt, prj = GDAL2Numpy(
        url, bbox=[minlon, minlat, maxlon, maxlat], bbox_srs=bbox_srs, load_nodata_as=np.nan)
    Numpy2GTiff(data, gt, prj, fileout, save_nodata_as=-9999, format=format)
    return fileout if isfile(fileout) else None
