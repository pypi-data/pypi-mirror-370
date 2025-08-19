## Example: Calculating max spots from the horizontal gradient magnitude

In this example, we show how to use **pymaxspots** to calculate the max spots of a gridded potential-field dataset.  We will use the aeromagnetic data from northeastern Oregon (Earney and others, 2022).  We will use the published horizontal gradient magnitude (HGM) from this dataset.

For a demonstration of how to use **pymaxspots** to calculate the HGM, see the example for [Calculating the horizontal gradient magnitude](./01_horizontal_gradient_magnitude.md).

First we import the necessary packages, load the HGM data, and read the values that define the coordinates and spacing of the grid.

```python
import numpy as np
import rasterio
import pymaxspots
import pathlib
import matplotlib.pyplot as plt
import geopandas as gpd

# loading the HGM data from the Umatilla dataset
hgm_raster_path = pathlib.Path("../data/Umatilla_final_220308/Magnetics/Umatilla_aeromag_HGM.tif")
hgm_umatilla_dataset = rasterio.open(hgm_raster_path)
masked_img = hgm_umatilla_dataset.read(1, masked=True) # get the first band from the file
hgm_umatilla = masked_img.filled(np.nan) # replace all instances of the nodata value with np.nan

# get the geotransform which defines the coordinates and spacing of the grid
ulx, dx, rr, uly, cr, dy = hgm_umatilla_dataset.get_transform()
dy_abs = np.abs(dy) # ensuring that dy is represented as a positive value
```

Next we visualize the HGM data:

```python
fig, ax = plt.subplots()
ax.imshow(hgm_umatilla)
ax.set_aspect("equal")
```

![HGM](figures/02_hgm_umatilla.png)

Now we are ready to use `pymaxspots.maxspots()` to calculate the maxspots:

```python
max_spots = pymaxspots.maxspots(hgm_umatilla, ulx, uly, dx, dy_abs)
```

`pymaxspots.maxspots()` returns a structured numpy array, with each row representing a different point.  The columns are as follows:
- `ID` (str): string description of shape of curvature of max point.
- `X` (float): x-coordinate.
- `Y` (float): y-coordinate.
- `HGM` (float): value of horizontal gradient magnitude at the max spot.
- `elong` (float): elongation ratio (e1/e2).
- `strike` (float): azimuth of principle direction of elongation.
- `e1` (float): big eigenvalue.
- `e2` (float): small eigenvalue.
- `type` (int): integer number denoting curvature shape.

```python
>>> max_spots
array([('ridge', 351300.59136375, 5102490.58646568, 3.91140333e-05, 0.0827273 ,  86.40536918, -2.84109752e-11, -3.43429264e-10, 1),
       ('ridge', 351398.13219327, 5102482.39275601, 3.78067395e-05, 0.01505793, -83.94461182,  4.73604365e-12, -3.14521459e-10, 1),
       ('ridge', 351496.34300229, 5102469.71748769, 3.65447067e-05, 0.04811832, -83.11415177,  1.34694658e-11, -2.79923886e-10, 1),
       ...,
       ('trough', 414813.43449654, 5023999.93391037, 2.77807136e-05, 1.93701034,   0.28185843,  2.79716871e-11, -1.44406493e-11, 2),
       ('ridge', 415435.72084393, 5023974.25497102, 3.06893771e-05, 0.22864455,  35.78136585, -1.41095998e-11, -6.17097591e-11, 1),
       ('ridge', 415471.32812438, 5024023.03248557, 3.08920618e-05, 0.37883381,  38.77535992, -2.55994299e-11, -6.75743005e-11, 1)],
      shape=(151764,), dtype=[('ID', '<U10'), ('X', '<f8'), ('Y', '<f8'), ('HGM', '<f8'), ('elong', '<f8'), ('strike', '<f8'), ('e1', '<f8'), ('e2', '<f8'), ('type', '<i8')])
```

### Visualizing the max spots at "ridges"

Typically we are most interested in points where the curvature shape is classified as a "ridge" because these points form linear features that can be associated with geologic structures, such as faults.

We will select the maxspots that have a shape classification of "ridge":

```python
max_spots_ridge = max_spots[max_spots["ID"]=="ridge"]

fig, ax = plt.subplots()
ax.scatter(max_spots_ridge["X"], max_spots_ridge["Y"], s=0.1)
ax.set_xlabel("Easting (m)")
ax.set_ylabel("Northing (m)")
ax.set_aspect("equal")
```

![Max spots](figures/02_maxspots.png)

### Saving max spots to a shapefile

Now, we will convert the data frame object `max_spots` into a geospatial object using **geopandas**, and save it as a shapefile.  To do this, we need the coordinate system of the data, which we will get from the HGM file. 

```python
crs_from_hgm = hgm_umatilla_dataset.crs # get the coordinate system from the HGM file

max_points_gdf = gpd.GeoDataFrame(max_spots,
                                  geometry=gpd.points_from_xy(max_spots['X'],
                                  max_spots['Y'], crs=crs_from_hgm))

max_points_gdf.to_file("umatilla_aeromag_maxspots.shp", driver="ESRI Shapefile")
```
----------
### Other examples

[Calculating the horizontal gradient magnitude](./01_horizontal_gradient_magnitude.md)

[Connecting max spots points into lines](./03_maxspots_lineations.md)

----------
[Back to README](../README.md)