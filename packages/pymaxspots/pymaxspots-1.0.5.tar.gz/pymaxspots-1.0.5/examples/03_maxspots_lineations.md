## Example: Connecting max spots points into lines

In this example, we show how to use **pymaxspots** to connect max spots points into lines by using the `pymaxspots.maxspots_lineations()` function.

This function connects the points together into lines if they are within a maximum distance of each other (set by the `dist_tol` parameter), and if each subsequent line segment is within a maximum azimuth angle (set by the `azimuth_tol` parameter) of the previous segment.  Lines must have a minimum number of points (set by the `min_line_segments` parameter).

For this example, we will use the aeromagnetic data from northeastern Oregon (Earney and others, 2022).  We will use the published max spots points from this dataset.

For a demonstration of how to use **pymaxspots** to calculate the max spots, see the example for [Calculating the max spots from the horizontal gradient magnitude](./02_maxspots.md).

First we import the necessary packages and load the max spots data.

```python
import numpy as np
import pymaxspots
import pathlib
import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString

# loading the max spots data from the Umatilla dataset
max_spots_csv_path = pathlib.Path("../data/Umatilla_final_220308/Magnetics/Umatilla_aeromag_max_spots.csv")
max_spots = pd.read_csv(max_spots_csv_path)
crs = "epsg:26911" # UTM Zone 11N NAD83
max_spots_gdf = gpd.GeoDataFrame(max_spots,
                                 geometry=gpd.points_from_xy(max_spots['X'],
                                 max_spots['Y']), crs=crs)

# selecting the points where the curvature shape is classified as a "ridge"
max_spots_ridge = max_spots[max_spots["ID"]=="ridge"]

fig, ax = plt.subplots()
ax.scatter(max_spots_ridge["X"], max_spots_ridge["Y"], s=0.1)
ax.set_xlabel("Easting (m)")
ax.set_ylabel("Northing (m)")
ax.set_xlim(351150, 415650)
ax.set_ylim(5102650, 5023850)
ax.set_aspect("equal")
```

![Max spots](figures/03_maxspots_umatilla.png)

### Using mean_nearest_neighbor_distance()

`pymaxspots.maxspots_lineations()` automatically calculates a value for `dist_tol` which is equal to 1.75 times the mean distance between each point and its nearest neighbor.  We can use `pymaxspots.mean_nearest_neighbor_distance()` to find out what this value is.

```python
mean_nn_dist = pymaxspots.mean_nearest_neighbor_distance(max_spots_ridge["X"], max_spots_ridge["Y"])
dist_tol = 1.75 * mean_nn_dist
print("dist_tol = {}".format(dist_tol))
```

```
dist_tol = 149.78767814833844
```

### Connecting points with maxspots_lineations()

Now we use `pymaxspots.maxspots_lineations()` to connect the max spots points into lines.  We will set an azimuth tolerance of 40 degrees instead of the default 35 degrees.

```python
# find the lineations
lines = pymaxspots.maxspots_lineations(max_spots_ridge["X"], max_spots_ridge["Y"], azimuth_tol=40, order="fixed")
```

Note that `pymaxspots.maxspots_lineations()` returns a list of "lines".  Each "line" is a list of the indices of the `x, y` coordinates, ordered in the sequence in which they are connected.

We can obtain the connected sequence of coordinates by using these indices.  By using the **shapely** library, we can convert each line into a vector line feature.

```python
X = np.c_[max_spots_ridge["X"], max_spots_ridge["Y"]]
lines_xy = [LineString([X[i] for i in line]) for line in lines]
```

### Saving line features to a shapefile

```python
# save these line features as a shapefile
lines_xy_gdf = gpd.GeoDataFrame(geometry=lines_xy, crs=crs)
lines_xy_gdf.to_file("umatilla_aeromag_lineations.shp", driver="ESRI Shapefile")
```

### Visualizing the line features

We can also display the line features in map view:

```python
fig, ax = plt.subplots()
lines_xy_gdf.plot(ax=ax)
ax.set_xlabel("Easting (m)")
ax.set_ylabel("Northing (m)")
ax.set_xlim(351150, 415650)
ax.set_ylim(5102650, 5023850)
ax.set_aspect("equal")
```

![Max spots lines](figures/03_lines.png)

----------
### Other examples

[Calculating the horizontal gradient magnitude](./01_horizontal_gradient_magnitude.md)

[Calculating max spots from the horizontal gradient magnitude](./02_maxspots.md)

----------
[Back to README](../README.md)