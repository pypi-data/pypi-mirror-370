## `maxspots_lineations(x, y, azimuth_tol=35, min_line_segments=3, dist_tol=None, order="none")`

Connects max spots points into lines

Connects points with coordinates x, y into a series of lines.  Points will
be connected into the same line only if subsequent pairs of points have a
maximum distance within a given distance tolerance, and if the angle
between subsequent pairs of points is within a given azimuth tolerance of
the previous pair.  A minimum number of points is required to form a line.

### Parameters
----------
**x : _numpy.ndarray_**

x-coordinates, must be one-dimensional.

**y : _numpy.ndarray_**

y-coordinates, must be one-dimensional, must have the same number of
points as x.

**azimuth_tol : _float, optional_**

Azimuth tolerance in degrees, must be between 0 and 180, inclusive.
Default is 35 degrees.

**min_line_segments :_integer, optional_**

Minimum number of points required to form a line.  Must be at least 1.
Default is 3.

**dist_tol : _float, optional_**

Maximum distance allowed to form a line segment between neighboring
points.  Must be greater than zero.  The default, `dist_tol=None`,
will result in the distance tolerance being assigned a value that is
1.75 times the mean nearest neighbor distance.

**order : _str or array-like, optional_**

If an array, should be a 1-D array of indices indicating the order
in which the algorithm should visit points.

If a string, should be 'fixed', 'random', or 'none'.  Default is 'none'.

If 'fixed', the algorithm starts at the point
closest to the upper-left coordinates and proceeds in order of
increasing distance from the starting point.

If 'random', algorithm visits the points in random order.

If 'none', algorithm visits the
points in the order in which they are passed.

### Returns
----------
**lines : _list_**

List of lines.  Each line is a list of integer indices of the
coordinates x, y, in the sequential order of the connected points.

### Notes
----------
If `order='random'`, due to the randomized visiting order of the points,
this function may return different results each time it is called.

### References
----------
Phillips, J.D., Hansen, R.O., and Blakely, R.J., 2007, The use of curvature in potential-field interpretation, Exploration Geophysics, 38, 111-119, <https://doi.org/10.1071/EG07014>.

Examples
----------

Consider a simple case of a parabolic surface defined by $f(x,y) = -(x-y)^2$.
In this case a single line will be returned.

```python
>>> import pymaxspots
>>> import numpy as np
>>> N = 13
>>> X, Y = np.meshgrid(np.arange(N), np.arange(N))
>>> Z = -(X-Y)**2
>>> maxspots = pymaxspots.maxspots(Z, 0, 0, 1, 1)
>>> maxspots
array([('ridge',  1.5,  -1.5, 0., 0., -45., 0., -4., 1),
    ('ridge',  2.5,  -2.5, 0., 0., -45., 0., -4., 1),
    ('ridge',  3.5,  -3.5, 0., 0., -45., 0., -4., 1),
    ('ridge',  4.5,  -4.5, 0., 0., -45., 0., -4., 1),
    ('ridge',  5.5,  -5.5, 0., 0., -45., 0., -4., 1),
    ('ridge',  6.5,  -6.5, 0., 0., -45., 0., -4., 1),
    ('ridge',  7.5,  -7.5, 0., 0., -45., 0., -4., 1),
    ('ridge',  8.5,  -8.5, 0., 0., -45., 0., -4., 1),
    ('ridge',  9.5,  -9.5, 0., 0., -45., 0., -4., 1),
    ('ridge', 10.5, -10.5, 0., 0., -45., 0., -4., 1),
    ('ridge', 11.5, -11.5, 0., 0., -45., 0., -4., 1)],
    dtype=[('ID', '<U10'), ('X', '<f8'), ('Y', '<f8'), ('HGM', '<f8'),
    ('elong', '<f8'), ('strike', '<f8'), ('e1', '<f8'), ('e2', '<f8'),
    ('type', '<i8')])
>>> lines = pymaxspots.maxspots_lineations(maxspots["X"], maxspots["Y"])
>>> lines
[[10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]]
```

To recover the x, y coordinates of the first line:

```python
>>> X = np.c_[maxspots["X"], maxspots["Y"]]
>>> coords = [X[i] for i in lines[0]]
>>> coords
[array([ 11.5, -11.5]),
array([ 10.5, -10.5]),
array([ 9.5, -9.5]),
array([ 8.5, -8.5]),
array([ 7.5, -7.5]),
array([ 6.5, -6.5]),
array([ 5.5, -5.5]),
array([ 4.5, -4.5]),
array([ 3.5, -3.5]),
array([ 2.5, -2.5]),
array([ 1.5, -1.5])]
```

To demonstrate the optional arguments, we must look at a more complicated
case.  Consider a surface defined by two ridges that intersect at a 90
degree angle.  This produces four lines at 90 degrees to each other.
The closest point of each line to another line is separated by a distance
of approximately 1.42 and an azimuth difference of 45 degrees.
Each line has 5 points or 4 line segments.

```python
>>> Z = np.max(np.dstack([-(X-int(N/2))**2, - (Y-int(N/2))**2]), axis=2)
>>> maxspots = pymaxspots.maxspots(Z, 0, 0, 1, 1)
>>> maxspots_ridge = maxspots[maxspots["ID"]=="ridge"]
>>> lines = pymaxspots.maxspots_lineations(maxspots_ridge["X"],
maxspots_ridge["Y"])
>>> lines
[[4, 3, 2, 1, 0],
[9, 8, 7, 6, 5],
[14, 13, 12, 11, 10],
[19, 18, 17, 16, 15]]
```

By default, `min_line_segments=3`, but changing this value can affect how
many lines are returned.  For example, in this case, no lines will be
returned if `min_line_segments=5`.

```python
>>> lines = pymaxspots.maxspots_lineations(maxspots["X"], maxspots["Y"],
min_line_segments=5)
>>> lines
[[4, 3, 2, 1, 0],
[9, 8, 7, 6, 5],
[14, 13, 12, 11, 10],
[19, 18, 17, 16, 15]]
```

By default, `azimuth_tol=35`, but changing this value can affect the number
and length of the lines returned.  For example, in this case, changing
`azimuth_tol=100` will result in two longer lines, since lines at 45 degrees
of each other can now be joined:

```python
>>> lines = pymaxspots.maxspots_lineations(maxspots_ridge["X"],
maxspots_ridge["Y"], azimuth_tol=100)
>>> lines
[[5, 6, 7, 8, 9, 4, 3, 2, 1, 0],
[19, 18, 17, 16, 15, 10, 11, 12, 13, 14]]
```

The `order` parameter can also change the lines returned.
For example, in this case, if `order='random'`, it will change which points
are assigned to which line, as well as the sequence of points in each line.

```python
>>> lines = pymaxspots.maxspots_lineations(maxspots_ridge["X"],
maxspots_ridge["Y"], azimuth_tol=100, order='random')
>>> lines
[[5, 6, 7, 8, 9, 15, 16, 17, 18, 19],
[14, 13, 12, 11, 10, 4, 3, 2, 1, 0]]
```

If `dist_tol` is modified, this will also change the number and length of
lines returned.  For example, in this case, changing `dist_tol=1` will
prevent the perpendicular lines, which are separated by a distance of 
approximately 1.42, from being connected:

```python
>>> lines = pymaxspots.maxspots_lineations(maxspots_ridge["X"],
maxspots_ridge["Y"], azimuth_tol=100, dist_tol=1)
>>> lines
[[4, 3, 2, 1, 0],
[9, 8, 7, 6, 5],
[14, 13, 12, 11, 10],
[19, 18, 17, 16, 15]]
```

----------
[Back to README](../README.md)