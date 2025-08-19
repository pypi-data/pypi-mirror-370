import numpy as np
from scipy import constants
from numba import jit

@jit(nopython=True)
def _usgs_curv4_phillips(hgm, ulx, uly, dx, dy):
    r"""Finds the max spots of the horizontal gradient magnitude grid

    Finds the max spots of the horizontal gradient magnitude grid using the
    method of Phillips and others (2007).

    Parameters
    ----------
    hgm : :class:`numpy.ndarray`
        A two dimensional array representing the horizontal gradient magnitude
        of a potential field.  Grid is assumed to be vertically oriented, i.e,
        no row or column rotation.

    ulx : scalar
        x-coordinate of the upper-left corner of the upper-left pixel.

    uly : scalar
        y-coordinate of the upper-left corner of the upper-left pixel.

    dx : scalar
        Spacing between grid cells in the x direction.  Must be positive.

    dy : scalar
        Spacing between grid cells in the y direction.  Must be positive.

    Returns
    -------
    maxpts : :class:`numpy.ndarray`
        A structured array where each row represents a max spot point.
        The columns of the array are as follows:
        - 'X' (float): x-coordinate.
        - 'Y' (float): y-coordinate.
        - 'HGM' (float): value of horizontal gradient magnitude at the max spot.
        - 'elong' (float): elongation ratio (e1/e2).
        - 'strike' (float): azimuth of principle direction of elongation.
        - 'e1' (float): big eigenvalue.
        - 'e2' (float): small eigenvalue.
        - 'type' (float): integer number denoting curvature shape.

    References
    ----------
    Phillips, J.D., Hansen, R.O., and Blakely, R.J., 2007, The use of curvature
    in potential-field interpretation, Exploration Geophysics, 38, 111-119,
    <https://doi.org/10.1071/EG07014>.
    """

    DEGREES_PER_RADIAN = 1 / constants.degree

    # stores grid values used to fit the quadratic surface
    g = np.zeros(10)

    max_points = []

    # j is row index
    # i is col index
    for j in range(1, hgm.shape[0]-1):
        # y-coordinate of pixel center
        yc = uly - j * dy - dy/2
        for i in range(1, hgm.shape[1]-1):
            # x-coordinate of pixel center
            xc = ulx + i * dx + dx/2
            
            g[1] = hgm[j+1, i-1]
            g[2] = hgm[j+1, i]
            g[3] = hgm[j+1, i+1] 
            g[4] = hgm[j, i-1]
            g[5] = hgm[j, i]
            g[6] = hgm[j, i+1]
            g[7] = hgm[j-1, i-1]
            g[8] = hgm[j-1, i]
            g[9] = hgm[j-1, i+1]

            if not np.all(np.isfinite(g)): continue

            A = (5.*g[5] + 2.*(g[2] + g[4] + g[6] + g[8]) - (g[1] + g[3] + g[7] + g[9]))/9.
            B = (g[3] + g[6] + g[9] - (g[1] + g[4] + g[7] ))/(6.*dx)
            C = (g[7] + g[8] + g[9] - (g[1] + g[2] + g[3]))/(6.*dy)
            D = (g[1] + g[3] + g[4] + g[6] + g[7] + g[9] - 2.*(g[2] + g[5] + g[8]))/(6.*dx*dx)
            E = (g[1] - g[3] - g[7] + g[9])/(4.*dx*dy)
            F = (g[1] + g[2] + g[3] + g[7] + g[8] + g[9] - 2.*(g[4] + g[5] + g[6]))/(6.*dy*dy)

            # Get the eigenvalues of the curvature matrix
            D_plus_F = D + F
            sqrt_term = np.sqrt((D - F)**2 + E**2)
            e1 = D_plus_F + sqrt_term
            e2 = D_plus_F - sqrt_term

            # Get the corresponding eigenvectors
            xx1 = 1.0
            if E != 0:
                yy1 = (e1 - 2.*D)/E
            elif e1 != 2.*F:
                yy1 = E/(e1 - 2.*F)
            else:
                xx1 = 0.0
                yy1 = 1.0
            
            xx2 = 1.0
            if E != 0:
                yy2 = (e2 - 2.*D)/E
            elif e2 != 2.*F:
                yy2 = E/(e2 - 2.*F)
            else:
                xx2 = 0.0
                yy2 = 1.0

            # Get the strike
            if e1 == e2:
                strike = np.inf
            else: 
                if np.abs(e1) > np.abs(e2):
                    strike = DEGREES_PER_RADIAN * np.arctan2(xx2, yy2)
                else:
                    strike = DEGREES_PER_RADIAN * np.arctan2(xx1, yy1)
                
                if strike > 90.: strike -= 180.
                if strike < -90.: strike += 180.

            # Find the critical points with ridge or trough shape
            # x-coordinate of the critical point relative to the pixel center
            x0 = 0
            # y-coordinate of the critical point relative to the pixel center
            y0 = 0
            # value of horizontal gradient magnitude
            g0 = 0
            # integer classification of curvature shape
            out_shape_type = 0
            if np.abs(e1) > np.abs(e2):
                den = D*(xx1**2) + E*xx1*yy1 + F*(yy1**2)
                if den != 0:
                    t0 = -0.5*(B*xx1 + C*yy1)/den
                    x0 = xx1*t0
                    y0 = yy1*t0
            elif np.abs(e1) < np.abs(e2):
                den = D*(xx2**2) + E*xx2*yy2 + F*(yy2**2)
                if den != 0:
                    t0 = -0.5*(B*xx2 + C*yy2)/den
                    x0 = xx2*t0
                    y0 = yy2*t0

            if x0 > -dx/2. and x0 < dx/2. and y0 > -dy/2. and y0 < dy/2.:
                g0 = A + B*x0 + C*y0 + D*(x0**2) + E*x0*y0 + F*(y0**2)
                out_shape_type = 0
                if e1 > 0.0 and e1 > np.abs(e2):
                    out_shape_type = 2
                elif e2 > 0.0 and e2 > np.abs(e1):
                    out_shape_type = 2
                elif e1 < 0.0 and np.abs(e1) > np.abs(e2):
                    out_shape_type = 1
                elif e2 < 0.0 and np.abs(e2) > np.abs(e1):
                    out_shape_type = 1
                out_x = x0 + xc
                out_y = y0 + yc
                out_hgm = g0
                out_strike = strike
                out_e1 = e1
                out_e2 = e2
                if out_e2 == 0:
                    out_elong = np.inf
                else:
                    out_elong = np.abs(out_e1/out_e2)
                if out_shape_type != 0:
                    max_points.append((out_x, out_y, out_hgm, out_elong, out_strike, out_e1, out_e2, out_shape_type))

            # Find the critical points with minimum, maximum, or saddle shape
            # x-coordinate of the critical point relative to the pixel center
            xe = 0
            # y-coordinate of the critical point relative to the pixel center
            ye = 0
            # value of horizontal gradient magnitude
            ge = 0
            # integer classification of curvature shape
            out_shape_type = 0
            den = E**2 - 4.*D*F
            if den != 0:
                xe = (2.*F*B - C*E)/den
                ye = (2.*D*C - E*B)/den
                if xe > -dx/2. and xe < dx/2. and ye > -dy/2. and ye < dy/2.:
                    ge = A + B*xe + C*ye + D*(xe**2) + E*xe*ye + F*(ye**2)
                    if e1 < 0.0 and e2 < 0.0:
                        out_shape_type = 3
                    elif e1 > 0.0 and e2 > 0.0:
                        out_shape_type = 4
                    elif e1*e2 < 0.0:
                        out_shape_type = 5
                    out_x = xe + xc
                    out_y = ye + yc
                    out_hgm = ge
                    out_strike = strike
                    out_e1 = e1
                    if out_e2 == 0:
                        out_elong = np.inf
                    else:
                        out_elong = np.abs(out_e1/out_e2)
                    if out_shape_type != 0:
                        max_points.append((out_x, out_y, out_hgm, out_elong, out_strike, out_e1, out_e2, out_shape_type))

    maxpts = np.array(max_points)

    return maxpts

def maxspots(hgm, ulx, uly, dx, dy):
    r"""Finds the max spots of the horizontal gradient magnitude grid

    Finds the max spots of the horizontal gradient magnitude grid using the
    method of Phillips and others (2007).

    Parameters
    ----------
    hgm : array_like
        A two dimensional array representing the horizontal gradient magnitude
        of a potential field.  Grid is assumed to be vertically oriented, i.e,
        no row or column rotation.

    ulx : scalar
        x-coordinate of the upper-left corner of the upper-left pixel.

    uly : scalar
        y-coordinate of the upper-left corner of the upper-left pixel.

    dx : scalar
        Spacing between grid cells in the x direction.  Must be positive.

    dy : scalar
        Spacing between grid cells in the y direction.  Must be positive.

    Returns
    -------
    maxpts : :class:`numpy.ndarray`
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

    References
    ----------
    Phillips, J.D., Hansen, R.O., and Blakely, R.J., 2007, The use of curvature
    in potential-field interpretation, Exploration Geophysics, 38, 111-119,
    <https://doi.org/10.1071/EG07014>.

    Examples
    ----------

    Consider a simple case of a parabolic surface defined by `f(x,y) = -(x-y)`.
    In this case, the points along the top of the parabola will be classified
    as having a 'ridge' shape.

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
    """
    g = np.asanyarray(hgm)
    if (g.ndim != 2):
        raise ValueError("hgm must be two-dimensional")
    if dx <= 0:
        raise ValueError("dx must be greater than zero")
    if dy <= 0:
        raise ValueError("dy must be greater than zero")

    maxpts = _usgs_curv4_phillips(g, ulx, uly, dx, dy)

    maxpts_dtypes = [
        ('ID', 'U10'),
        ('X', '<f8'),
        ('Y', '<f8'),
        ('HGM', '<f8'),
        ('elong', '<f8'),
        ('strike', '<f8'),
        ('e1', '<f8'),
        ('e2', '<f8'),
        ('type', '<i8')
    ]

    # write curvature shape type as string and append as first column
    # of returned array
    shape = maxpts[:,-1]
    out_maxpts = []
    for _shape, _maxpts_row in zip(shape, maxpts):
        if _shape == 1:
            _shape_str = 'ridge'
        elif _shape == 2:
            _shape_str = 'trough'
        elif _shape == 3:
            _shape_str = 'high'
        elif _shape == 4:
            _shape_str = 'low'
        elif _shape == 5:
            _shape_str = 'saddle'
        else:
            _shape_str = ''

        out_maxpts.append(tuple([_shape_str] + [item for item in _maxpts_row]))
    
    return np.array(out_maxpts, dtype=maxpts_dtypes)

def horizontal_gradient_magnitude(grid, dx, dy):
    r"""Calculates the horizontal gradient magnitude of a potential field grid

    Compute the horizontal gradient magnitude of a regular gridded potential
    field M with grid spacing defined by dx and dy.

    Parameters
    ----------
    grid : array_like
        A two dimensional array representing a gridded potential field.

    dx : scalar
        Spacing between grid cells in the x direction.

    dy : scalar
        Spacing between grid cells in the y direction.

    Returns
    -------
    horizontal_gradient_magnitude_grid : :class:`numpy.ndarray`
        A two dimensional :class:`numpy.ndarray` representing the horizontal
        gradient magnitude of the passed ``grid``.

    Notes
    -----
    The horizontal gradient magnitude is calculated as:

    .. math::

        h(x, y) = \sqrt{
            \left( \frac{\partial M}{\partial x} \right)^2
            + \left( \frac{\partial M}{\partial y} \right)^2
        }

    where :math:`M` is the regularly gridded potential field.

    References
    ----------
    Blakely, R.J., 1995, Potential Theory in Gravity and Magnetic Applications,
    Cambridge University Press, <https://doi.org/10.1017/CBO9780511549816>.

    Examples
    ----------

    Given a potential field grid, find the horizontal gradient.  In this case,
    consider a potential field grid defined as a 2D parabola.  We can find the
    horizontal gradient magnitude of this parabolic surface:

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
    
    """
    g = np.asanyarray(grid)
    if (g.ndim != 2):
        raise ValueError("grid must be two-dimensional")

    hgm_x, hgm_y = np.gradient(g, dx, dy)
    hgm = np.sqrt( hgm_x**2 + hgm_y**2 )

    return hgm
