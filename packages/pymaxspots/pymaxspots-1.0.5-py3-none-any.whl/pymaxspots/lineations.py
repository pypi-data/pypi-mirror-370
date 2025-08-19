import numpy as np
from scipy.spatial import KDTree
from numba import jit

@jit(nopython=True)
def _azimuth_difference(azimuth1, azimuth2):
    """ Returns difference of two azimuths in degrees """
    azimuth_diff = np.absolute(azimuth1 - azimuth2)
    while azimuth_diff > 180:
        azimuth_diff = 360 - azimuth_diff
    return azimuth_diff

@jit(nopython=True)
def _get_azimuth(point1, point2):
    """ Returns heading in degrees clockwise from north """
    dx = float(point2[0] - point1[0])
    dy = float(point2[1] - point1[1])
    return np.degrees(np.arctan2(dx, dy))

@jit(nopython=True)
def _evaluate_point_score(dist, deviation, dist_tol, azimuth_tol):
    """ Neighbor nodes are scored by their distance and azimuth deviation
    to choose the best neighbor to add to path """
    return (dist/dist_tol)**2 + (deviation/azimuth_tol)**2

def _grow_path(tree, path, data, visited, dist_tol, azimuth_tol):
    """ Adds points to path """
    while True:
        azimuth = _get_azimuth(data[path[-2]], data[path[-1]])
        curr = path[-1]
        neighbors = [item for item in tree.query_ball_point(data[curr], r=dist_tol) if not visited[item] and item not in path]
        best_next = []
        for next in neighbors:
            azimuth_next = _get_azimuth(data[path[-1]], data[next])
            dist_next = np.linalg.norm(data[curr] - data[next], axis = 0)
            deviation = _azimuth_difference(azimuth, azimuth_next)
            if deviation < azimuth_tol:
                score = _evaluate_point_score(dist_next, deviation, dist_tol, azimuth_tol)
                best_next.append((score, next))
        if not best_next:
            break
        else:
            scores = np.array(best_next)[:,0]
            best_score_ix = np.argmin(scores)
            best_next_point = best_next[best_score_ix][1]
            path.append(best_next_point)

    return path

def _find_best_path(tree, curr, data, visited, dist_tol, azimuth_tol, min_line_segments):
    """ Returns the path with the most segments """
    neighbors = [item for item in tree.query_ball_point(data[curr], r=dist_tol) if not visited[item] and item != curr]
    possible_paths = []
    for next in neighbors:
        path = [curr, next]
        path = _grow_path(tree, path, data, visited, dist_tol, azimuth_tol)
        path.reverse() # Grow path in opposite direction
        path = _grow_path(tree, path, data, visited, dist_tol, azimuth_tol)
        if len(path) > min_line_segments: # Check number of segments in path
            possible_paths.append(path)
    if possible_paths:
        return possible_paths[np.argmax([len(ppath) for ppath in possible_paths])]
    else:
        return []

def _mean_nearest_neighbor_distance_from_tree(tree, X):
    """Mean distance between nearest neighbor pairs given K-d tree"""
    dist, nearest_ix = tree.query(X, k=2)
    least_dist = dist[:, 1]
    return np.mean(least_dist)

def mean_nearest_neighbor_distance(x, y):
    """Mean distance between nearest neighbor pairs with coordinates x, y

    Calculates the mean distance between nearest neighbor pairs defined by
    coordinates x, y.

    Parameters
    ----------
    x : numpy.ndarray
        x-coordinates, must be one-dimensional.

    y : numpy.ndarray
        y-coordinates, must be one-dimensional, must have the same number of
        points as x.

    Returns
    ----------
    result : float
        Mean distance between all nearest neighbor pairs.

    Examples
    ----------

    Given points with coordinates `x` and `y`, find the mean distance between
    each point and its nearest neighbor.

    >>> import numpy as np
    >>> import pymaxspots
    >>> x = np.array([-3, -2, 0, 3, 6])
    >>> y = np.zeros(x.size)
    >>> dist = pymaxspots.mean_nearest_neighbor_distance(x, y)
    >>> dist
    2.0
    
    """
    if (x.ndim != 1):
        raise ValueError("x must have dimension of 1, got {}".format(x.ndim))
    if (y.ndim != 1):
        raise ValueError("x must have dimension of 1, got {}".format(y.ndim))
    if (x.size != y.size):
        raise ValueError("x and y must have equal size")
    if not np.all(np.isfinite(x)):
        raise ValueError("x cannot contain any nan or inf values")
    if not np.all(np.isfinite(y)):
        raise ValueError("x cannot contain any nan or inf values")
    
    X = np.c_[x, y]
    tree = KDTree(X)
    return _mean_nearest_neighbor_distance_from_tree(tree, X)

def maxspots_lineations(x, y, azimuth_tol=35, min_line_segments=3,
                        dist_tol=None, order="none"):
    """Connects max spots points into lines

    Connects points with coordinates x, y into a series of lines.  Points will
    be connected into the same line only if subsequent pairs of points have a
    maximum distance within a given distance tolerance, and if the angle
    between subsequent pairs of points is within a given azimuth tolerance of
    the previous pair.  A minimum number of points is required to form a line.

    Parameters
    ----------
    x : numpy.ndarray
        x-coordinates, must be one-dimensional.

    y : numpy.ndarray
        y-coordinates, must be one-dimensional, must have the same number of
        points as x.

    azimuth_tol : float, optional
        Azimuth tolerance in degrees, must be between 0 and 180, inclusive.
        Default is 35 degrees.

    min_line_segments : integer, optional
        Minimum number of points required to form a line.  Must be at least 1.
        Default is 3.

    dist_tol : float, optional
        Maximum distance allowed to form a line segment between neighboring
        points.  Must be greater than zero.  The default, `dist_tol=None`,
        will result in the distance tolerance being assigned a value that is
        1.75 times the mean nearest neighbor distance.

    order : str or array-like, optional
        If an array, should be a 1-D array of indices indicating the order
        in which the algorithm should visit points.
        If a string, should be 'fixed', 'random', or 'none'.
        Default is 'none'.  If 'fixed', the algorithm starts at the point
        closest to the upper-left coordinates and proceeds in order of
        increasing distance from the starting point.  If 'random', algorithm
        visits the points in random order.  If 'none', algorithm visits the
        points in the order in which they are passed.

    Returns
    ----------
    lines : list
        List of lines.  Each line is a list of integer indices of the
        coordinates x, y, in the sequential order of the connected points.

    Notes
    ----------
        If `order='random'`, due to the randomized visiting order of the points,
        this function may return different results each time it is called.

    References
    ----------
    Phillips, J.D., Hansen, R.O., and Blakely, R.J., 2007, The use of curvature
    in potential-field interpretation, Exploration Geophysics, 38, 111-119,
    <https://doi.org/10.1071/EG07014>.

    Examples
    ----------

    Consider a simple case of a parabolic surface defined by `f(x,y) = -(x-y)`.
    In this case a single line will be returned.

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

    To recover the x, y coordinates of the first line:

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

    To demonstrate the optional arguments, we must look at a more complicated
    case.  Consider a surface defined by two ridges that intersect at a 90
    degree angle.  This produces four lines at 90 degrees to each other.
    The closest point of each line to another line is separated by a distance
    of approximately 1.42 and an azimuth difference of 45 degrees.
    Each line has 5 points or 4 line segments.

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

    By default, `min_line_segments=3`, but changing this value can affect how
    many lines are returned.  For example, in this case, no lines will be
    returned if `min_line_segments=5`.

    >>> lines = pymaxspots.maxspots_lineations(maxspots["X"], maxspots["Y"],
    min_line_segments=5)
    >>> lines
    [[4, 3, 2, 1, 0],
    [9, 8, 7, 6, 5],
    [14, 13, 12, 11, 10],
    [19, 18, 17, 16, 15]]

    By default, `azimuth_tol=35`, but changing this value can affect the number
    and length of the lines returned.  For example, in this case, changing
    `azimuth_tol=100` will result in two longer lines, since lines at 45 degrees
    of each other can now be joined:

    >>> lines = pymaxspots.maxspots_lineations(maxspots_ridge["X"],
    maxspots_ridge["Y"], azimuth_tol=100)
    >>> lines
    [[5, 6, 7, 8, 9, 4, 3, 2, 1, 0],
    [19, 18, 17, 16, 15, 10, 11, 12, 13, 14]]

    The `order` parameter can also change the lines returned.
    For example, in this case, if `order='random'`, it will change which points
    are assigned to which line, as well as the sequence of points in each line.

    >>> lines = pymaxspots.maxspots_lineations(maxspots_ridge["X"],
    maxspots_ridge["Y"], azimuth_tol=100, order='random')
    >>> lines
    [[5, 6, 7, 8, 9, 15, 16, 17, 18, 19],
    [14, 13, 12, 11, 10, 4, 3, 2, 1, 0]]

    If `dist_tol` is modified, this will also change the number and length of
    lines returned.  For example, in this case, changing `dist_tol=1` will
    prevent the perpendicular lines, which are separated by a distance of 
    approximately 1.42, from being connected:

    >>> lines = pymaxspots.maxspots_lineations(maxspots_ridge["X"],
    maxspots_ridge["Y"], azimuth_tol=100, dist_tol=1)
    >>> lines
    [[4, 3, 2, 1, 0],
    [9, 8, 7, 6, 5],
    [14, 13, 12, 11, 10],
    [19, 18, 17, 16, 15]]

    """
    if (x.ndim != 1):
        raise ValueError("x must have dimension of 1, got {}".format(x.ndim))
    if (y.ndim != 1):
        raise ValueError("x must have dimension of 1, got {}".format(y.ndim))
    if (x.size != y.size):
        raise ValueError("x and y must have equal size")
    if not np.all(np.isfinite(x)):
        raise ValueError("x cannot contain any nan or inf values")
    if not np.all(np.isfinite(y)):
        raise ValueError("x cannot contain any nan or inf values")
    if azimuth_tol < 0 or azimuth_tol > 180:
        raise ValueError("azimuth_tol must be between 0 and 180 inclusive")
    if min_line_segments < 1:
        raise ValueError("min_line_segments must be at least 1")
    if (dist_tol and dist_tol <= 0):
        raise ValueError("dist_tol must be greater than zero")
    if isinstance(order, str):
        if order != "fixed" and order != "random" and order != "none":
            raise ValueError("""order can only take str values of
                             'fixed', 'random', or 'none'""")
    else:
        order = np.asanyarray(order)
        if order.ndim != 1:
            raise ValueError("order must have dimension of 1, got {}".format(order.ndim))
        if order.size != x.size:
            raise ValueError("order must have same size as x and y")
        if np.unique(order).size != order.size:
            raise ValueError("order must have unique values")
        if order.dtype is not np.dtype(int):
            raise ValueError("order.dtype must be int")
        if not np.all(np.isfinite(order)):
            raise ValueError("order cannot contain any nan or inf values")

    X = np.c_[x, y]
    num_points = X.shape[0]
    tree = KDTree(X)

    if not dist_tol:
        tolerance = _mean_nearest_neighbor_distance_from_tree(tree, X)
        dist_tol = tolerance * 1.75

    lines = [] # Keep track of line paths
    visited = np.zeros(num_points, dtype=bool)

    if isinstance(order, str):
        if order == 'random':
            ix_order = np.arange(num_points)
            np.random.shuffle(ix_order)
        elif order == 'fixed':
            xy_start = [x.min(), y.max()]
            dist_order, ix_order = tree.query(xy_start, k=num_points)
        else: # order = 'none'
            ix_order = np.arange(num_points)
    else:
        ix_order = order

    for curr in ix_order:
        if not visited[curr]:
            path = _find_best_path(tree, curr, X, visited, dist_tol, azimuth_tol, min_line_segments)
            if path:
                lines.append(path)
                for idx in path:
                    visited[idx] = True
            else:
                visited[curr] = True

    return lines
