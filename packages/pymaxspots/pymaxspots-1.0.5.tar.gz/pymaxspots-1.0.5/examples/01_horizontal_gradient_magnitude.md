## Example: Calculating the horizontal gradient magnitude

In this example, we show how to use **pymaxspots** to calculate the horizontal gradient magnitude (HGM) of a gridded potential-field dataset.  We will use the aeromagnetic data from northeastern Oregon (Earney and others, 2022).

If you already have the HGM, see [Calculating max spots from the horizontal gradient magnitude](./02_maxspots.md) for an example of how to calculate max spots from the HGM data.

First we import the necessary packages, load the pseudogravity data, and read the values that define the coordinates and spacing of the grid.

```python
import numpy as np
import rasterio
import pymaxspots
import pathlib
import matplotlib.pyplot as plt

# loading the pseudogravity transform of the aeromagnetic data
pseudograv_raster_path = pathlib.Path("../data/Umatilla_final_220308/Magnetics/Umatilla_aeromag_Pseudogravity.tif")
pseudograv_dataset = rasterio.open(pseudograv_raster_path)

masked_img = pseudograv_dataset.read(1, masked=True) # get the first band from the file
pseudograv = masked_img.filled(np.nan) # replace all instances of the nodata value with np.nan

# get the geotransform which defines the coordinates and spacing of the grid
ulx, dx, rr, uly, cr, dy = pseudograv_dataset.get_transform()
dy_abs = np.abs(dy) # ensuring that dy is represented as a positive value
```

We can visualize the pseudogravity data:

```python
fig, ax = plt.subplots()
ax.imshow(pseudograv)
ax.set_aspect("equal")
```

![Pseudogravity](figures/01_pseudograv.png)

Next, we use `pymaxspots.horizontal_gradient_magnitude()` to calculate the horizontal gradient magnitude (HGM) of the pseudogravity data.

```python
hgm = pymaxspots.horizontal_gradient_magnitude(pseudograv, dx, dy_abs)
fig, ax = plt.subplots()
ax.imshow(hgm)
ax.set_aspect("equal")
```

![Calculated HGM](figures/01_hgm.png)

----------
### Other examples

[Calculating max spots from the horizontal gradient magnitude](./02_maxspots.md)

[Connecting max spots points into lines](./03_maxspots_lineations.md)

----------
[Back to README](../README.md)