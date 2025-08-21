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
# Name:        module_GDAL2Numpy.py
# Purpose:
#
# Author:      Luzzi Valerio
#
# Created:
# -------------------------------------------------------------------------------
import math
import numpy as np
from osgeo import gdal
from .filesystem import now, total_seconds_from, justfname
from .module_ogr import TransformBBOX
from .module_open import OpenRaster
from .module_log import Logger


def GDAL2Numpy(filename, band=1, dtype=np.float32, load_nodata_as=np.nan, bbox=[], bbox_srs=None):
    """
    GDAL2Numpy
    """
    t0 = now()
    data_type_of = {
        'Float32': np.float32,
        'Float64': np.float64,
        'Byte': np.uint8,
        'Int16': np.int16,
        'Int32': np.int32,
        'UInt16': np.uint16,
        'UInt32': np.uint32,
    }

    ds = OpenRaster(filename)
    if ds:
        band = ds.GetRasterBand(band)
        m, n = ds.RasterYSize, ds.RasterXSize
        gt, prj = ds.GetGeoTransform(), ds.GetProjection()
        no_data = band.GetNoDataValue()
        band_type = data_type_of[gdal.GetDataTypeName(band.DataType)]
        Logger.debug("Data type: %s", band_type)

        if not bbox:
            data = band.ReadAsArray(0, 0, n, m)
        else:
            x0, px, r0, y0, r1, py = gt
            if bbox_srs:
                X0, Y0, X1, Y1 = TransformBBOX(bbox, bbox_srs, prj)
            else:
                X0, Y0, X1, Y1 = bbox

            # calcutate starting indices
            j0, i0 = int((X0 - x0) / px), int((Y1 - y0) / py)
            cols, rows = math.ceil(
                (X1 - X0) / px), math.ceil(abs(Y1 - Y0) / abs(py))
            # assert cols > 0 and rows > 0,
            cols = max(1, cols)
            rows = max(1, rows)

            # print("mxn", m,"x", n)
            # print("cols, rows", cols, "x", rows)
            # print("j0, i0", j0, i0)

            # index-safe
            j0, i0 = min(max(j0, 0), n - 1), min(max(i0, 0), m - 1)

            # index-safe
            j1, i1 = min(j0 + cols, n), min(i0 + rows, m)
            # Re-calculate cols and rows
            cols, rows = j1 - j0, i1 - i0

            # re-arrange gt
            k = math.floor((X0 - x0) / px)
            h = math.floor((Y1 - y0) / py)
            gt = x0 + k * px, px, r0, y0 + h * py, r1, py

            # print("ReadAsArray(%d,%d,%d,%d)" % (j0, i0, cols, rows))

            data = band.ReadAsArray(j0, i0, cols, rows)

        # translate no-data as Nan
        if data is not None:

            # if not np.isnan(load_nodata_as):
            #     data[np.isnan(data)] = load_nodata_as

            # Output datatype
            if dtype and dtype != band_type:
                Logger.debug("Converting data type from %s to %s",
                             band_type, dtype)
                data = data.astype(dtype, copy=False)

            if data.dtype == np.float32:
                no_data = np.float32(no_data)
                if no_data is not None and np.isinf(no_data):
                    data[np.isinf(data)] = load_nodata_as
                elif no_data is not None:
                    data[data == no_data] = load_nodata_as
                data[np.isnan(data)] = np.float32(load_nodata_as)

            elif data.dtype == np.float64:
                no_data = np.float64(no_data)
                if no_data is not None and np.isinf(no_data):
                    data[np.isinf(data)] = load_nodata_as
                elif no_data is not None:
                    data[data == no_data] = load_nodata_as
                data[np.isnan(data)] = np.float64(load_nodata_as)

            # , np.int16, np.uint16, np.int32, np.uint32):
            elif data.dtype == np.uint8:
                if no_data != load_nodata_as:
                    data[data == no_data] = np.uint8(
                        min(255, abs(load_nodata_as)))

            # , np.int16, np.uint16, np.int32, np.uint32):
            elif data.dtype == np.uint16:
                if no_data != load_nodata_as:
                    data[data == no_data] = np.uint16(
                        min(65535, abs(load_nodata_as)))

            # , np.int16, np.uint16, np.int32, np.uint32):
            elif data.dtype == np.uint32:
                if no_data != load_nodata_as:
                    data[data == no_data] = np.uint32(
                        min(4294967295, abs(load_nodata_as)))

            # , np.int16, np.uint16, np.int32, np.uint32):
            elif data.dtype == np.int8:
                if no_data != load_nodata_as:
                    data[data == no_data] = np.uint8(
                        min(127, abs(load_nodata_as)))

            # , np.int16, np.uint16, np.int32, np.uint32):
            elif data.dtype == np.int16:
                if no_data != load_nodata_as:
                    data[data == no_data] = np.uint16(
                        min(32767, abs(load_nodata_as)))

            # , np.int16, np.uint16, np.int32, np.uint32):
            elif data.dtype == np.int32:
                if no_data != load_nodata_as:
                    data[data == no_data] = np.uint32(
                        min(2147483647, abs(load_nodata_as)))

        band = None
        ds = None
        Logger.debug("Reading %s in %ss.", justfname(
            filename), total_seconds_from(t0))
        return data, gt, prj
    Logger.error(f"file <%s> not exists!", filename)
    return None, None, None
