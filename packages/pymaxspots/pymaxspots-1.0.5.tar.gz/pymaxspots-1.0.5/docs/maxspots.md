## `maxspots(hgm, ulx, uly, dx, dy)`

Finds the max spots of the horizontal gradient magnitude grid

Finds the max spots of the horizontal gradient magnitude grid using the
method of Phillips and others (2007).

### Parameters
----------
**hgm : array_like**

A two dimensional array representing the horizontal gradient magnitude
of a potential field.  Grid is assumed to be vertically oriented, i.e,
no row or column rotation.

**ulx : _scalar_**

x-coordinate of the upper-left corner of the upper-left pixel.

**uly : _scalar_**

y-coordinate of the upper-left corner of the upper-left pixel.

**dx : _scalar_**

Spacing between grid cells in the x direction.  Must be positive.

**dy : _scalar_**

Spacing between grid cells in the y direction.  Must be positive.

#### Returns
-------
**maxpts : _numpy.ndarray_**

A structured array where each row represents a max spot point.

The columns of the array are named as follows:
- 'ID' (str): string description of shape of curvature of max point.
- 'X' (float): x-coordinate.
- 'Y' (float): y-coordinate.
- 'HGM' (float): value of horizontal gradient magnitude at the max spot.
- 'elong' (float): elongation ratio (e1/e2).
- 'strike' (float): azimuth of principle direction of elongation.
- 'e1' (float): big eigenvalue.
- 'e2' (float): small eigenvalue.
- 'type' (float): integer number denoting curvature shape.

#### References
----------
Phillips, J.D., Hansen, R.O., and Blakely, R.J., 2007, The use of curvature in potential-field interpretation, Exploration Geophysics, 38, 111-119, <https://doi.org/10.1071/EG07014>.

#### Examples
----------

Consider a simple case of a parabolic surface defined by $f(x,y) = -(x-y)$.
In this case, the points along the top of the parabola will be classified
as having a 'ridge' shape.

```python
>>> import pymaxspots
>>> import numpy as np
>>> N = 5
>>> X, Y = np.meshgrid(np.arange(N), np.arange(N))
>>> Z = -(X-Y)**2
>>> maxspots = pymaxspots.maxspots(Z, 0, 0, 1, 1)
>>> maxspots
array([('ridge', 1.5, -1.5, 0., 0., -45., 0., -4., 1),
    ('ridge', 2.5, -2.5, 0., 0., -45., 0., -4., 1),
    ('ridge', 3.5, -3.5, 0., 0., -45., 0., -4., 1)],
    dtype=[('ID', '<U10'), ('X', '<f8'), ('Y', '<f8'), ('HGM', '<f8'),
    ('elong', '<f8'), ('strike', '<f8'), ('e1', '<f8'), ('e2', '<f8'),
    ('type', '<i8')])
```

----------
[Back to README](../README.md)
