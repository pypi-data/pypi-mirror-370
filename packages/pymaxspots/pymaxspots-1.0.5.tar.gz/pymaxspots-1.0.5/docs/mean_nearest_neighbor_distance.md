## `mean_nearest_neighbor_distance(x, y)`

Mean distance between nearest neighbor pairs with coordinates x, y

Calculates the mean distance between nearest neighbor pairs defined by
coordinates x, y.

### Parameters
----------
**x : _numpy.ndarray_**

x-coordinates, must be one-dimensional.

**y : _numpy.ndarray_**

y-coordinates, must be one-dimensional, must have the same number of
points as x.

### Returns
----------
**result** : **_float_**

Mean distance between all nearest neighbor pairs.

### Examples
----------

Given points with coordinates `x` and `y`, find the mean distance between
each point and its nearest neighbor.

```python
>>> import numpy as np
>>> import pymaxspots
>>> x = np.array([-3, -2, 0, 3, 6])
>>> y = np.zeros(x.size)
>>> dist = pymaxspots.mean_nearest_neighbor_distance(x, y)
>>> dist
2.0
```

----------
[Back to README](../README.md)
