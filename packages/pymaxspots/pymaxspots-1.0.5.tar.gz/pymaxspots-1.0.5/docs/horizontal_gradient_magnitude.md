## `horizontal_gradient_magnitude(grid, dx, dy)`

Calculates the horizontal gradient magnitude of a potential field grid

Compute the horizontal gradient magnitude of a regular gridded potential
field M with grid spacing defined by dx and dy.

#### Parameters
----------
**grid : _array_like_**

A two dimensional array representing a gridded potential field.

**dx : _scalar_**

Spacing between grid cells in the x direction.

**dy : _scalar_**

Spacing between grid cells in the y direction.

#### Returns
-------
**horizontal_gradient_magnitude_grid** : **_numpy.ndarray_**

A two dimensional array representing the horizontal
gradient magnitude of the passed ``grid``.

#### Notes
-----
The horizontal gradient magnitude is calculated as:

$$
    h(x, y) = \sqrt{
        \left( \frac{\partial M}{\partial x} \right)^2
        + \left( \frac{\partial M}{\partial y} \right)^2
    }
$$

where $M$ is the regularly gridded potential field.

#### References
----------
Blakely, R.J., 1995, Potential Theory in Gravity and Magnetic Applications, Cambridge University Press, <https://doi.org/10.1017/CBO9780511549816>.

#### Examples
----------

Given a potential field grid, find the horizontal gradient.  In this case,
consider a potential field grid defined as a 2D parabola.  We can find the
horizontal gradient magnitude of this parabolic surface:

```python
>>> import numpy as np
>>> import pymaxspots
>>> ncol = nrow = 5
>>> X, Y = np.meshgrid(np.arange(ncol), np.arange(nrow))
>>> Z = -(X-2)**2 - (Y-2)**2
>>> hgm = pymaxspots.horizontal_gradient_magnitude(Z, 1, 1)
>>> hgm
array([[4.24264069, 3.60555128, 3.        , 3.60555128, 4.24264069],
    [3.60555128, 2.82842712, 2.        , 2.82842712, 3.60555128],
    [3.        , 2.        , 0.        , 2.        , 3.        ],
    [3.60555128, 2.82842712, 2.        , 2.82842712, 3.60555128],
    [4.24264069, 3.60555128, 3.        , 3.60555128, 4.24264069]])
```

----------
[Back to README](../README.md)
