import numpy as np
from .filesystem import justfname
from .module_s3 import isfile
from .module_features import GetFieldNames
from .rasterizelike import RasterizeLike
from .module_GDAL2Numpy import GDAL2Numpy
from .module_Numpy2GTiff import Numpy2GTiff
from .module_log import Logger


def raster_edit(filetif, fileshp, fileout=None, fieldname=None, mode="add", format="GTiff"):
    """
    raster_edit - edit a raster file with a shapefile
    filetif: str - input raster file
    fileshp: str - input shapefile 
    fileout: str - output raster file
    fieldname: str - fieldname
    mode: str - mode
    format: str - format GTiff/COG
    """
    mode = mode.lower() if mode else "add"
    if mode not in ["add", "level"]:
        Logger.error(f"mode {mode} not supported")
        return None, None, None
    if format not in ["GTiff", "COG"]:
        Logger.error(f"output format {format} not supported")
        return None, None, None
    if not isfile(filetif):
        Logger.error(f"file {filetif} not found")
        return None, None, None
    if not isfile(fileshp):
        Logger.error(f"file {fileshp} not found")
        return None, None, None
    if not fieldname:
        Logger.error(f"fieldname {fieldname} is empty")
        return None, None, None
    if not fieldname in GetFieldNames(fileshp):
        Logger.error(f"fieldname {fieldname} not found in {fileshp}")
        return None, None, None
    if fileout == filetif:
        Logger.warning(f"Inplace editing for {justfname(filetif)}")

    # Rasterizing the shapefile
    features_raster, gt, prj = RasterizeLike(
        fileshp, filetif, burn_fieldname=fieldname, nodata=0)
    dem, _, _ = GDAL2Numpy(filetif, load_nodata_as=np.nan)
    if mode == "add":
        dem[~np.isnan(dem)] += features_raster[~np.isnan(dem)]
    elif mode == "level":
        # with RasterizeLike( ...nodata=0) the nodata value is 0
        # so put le the level onlly where the features_raster>0
        dem[features_raster>0] = features_raster[features_raster>0]
    if fileout:
        Numpy2GTiff(dem, gt, prj, fileout, save_nodata_as=-9999, format=format)
    return dem, gt, prj
