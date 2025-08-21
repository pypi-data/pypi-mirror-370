# gdal2numpy

**gdal2numpy** is a utilty package based on GDAL.

The main function is *GDAL2Numpy()* for reading a GeoTiff 

The simplest use:
```

data, gt, prj = GDAL2Numpy(filetif)

data # is a numpy array
gt   # is the geotransform array (x0, px, _,y0, _, py )
prj  # is the wkt of the spatial reference system
```
More complex uses
```
data, gt, prj = GDAL2Numpy(filetif, dtype=np.float32, load_nodata_as=-9999) 

# Get a bbox from cog
data, gt, prj = GDAL2Numpy(filetif, bbox=[12,44,12.5,44.5])


# Get data from http
data, gt, prj = GDAL2Numpy("https://amazonaws.com/bucketname/filename.tif", bbox=[12,44,12.5,44.5])

```

