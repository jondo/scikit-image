# coding: utf-8
import numpy as np

from ._draw import _coords_inside_image

from .._shared._geometry import polygon_clip
from ._draw import line

from skimage._shared.version_requirements import is_installed
from warnings import warn
matplotlib_installed = is_installed('matplotlib')
if not matplotlib_installed:
    warn('Polygon perimeter drawing requires matplotlib')


def _ellipse_in_shape(shape, center, radiuses):
    """Generate coordinates of points within ellipse bounded by shape."""
    r_lim, c_lim = np.ogrid[0:float(shape[0]), 0:float(shape[1])]
    r, c = center
    ry, rx = radiuses
    distances = ((r_lim - r) / ry) ** 2 + ((c_lim - c) / rx) ** 2
    return np.nonzero(distances < 1)


def ellipse(r, c, yradius, xradius, shape=None):
    """Generate coordinates of pixels within ellipse.

    Parameters
    ----------
    r, c : double
        Centre coordinate of ellipse.
    yradius, xradius : double
        Minor and major semi-axes. ``(x/xradius)**2 + (y/yradius)**2 = 1``.
    shape : tuple, optional
        Image shape which is used to determine the maximum extent of output pixel
        coordinates. This is useful for ellipses which exceed the image size.
        By default the full extent of the ellipse are used.

    Returns
    -------
    rr, cc : ndarray of int
        Pixel coordinates of ellipse.
        May be used to directly index into an array, e.g.
        ``img[rr, cc] = 1``.

    Examples
    --------
    >>> from skimage.draw import ellipse
    >>> img = np.zeros((10, 10), dtype=np.uint8)
    >>> rr, cc = ellipse(5, 5, 3, 4)
    >>> img[rr, cc] = 1
    >>> img
    array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 1, 1, 1, 1, 1, 0, 0],
           [0, 0, 1, 1, 1, 1, 1, 1, 1, 0],
           [0, 0, 1, 1, 1, 1, 1, 1, 1, 0],
           [0, 0, 1, 1, 1, 1, 1, 1, 1, 0],
           [0, 0, 0, 1, 1, 1, 1, 1, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], dtype=uint8)

    """

    center = np.array([r, c])
    radiuses = np.array([yradius, xradius])

    # The upper_left and lower_right corners of the
    # smallest rectangle containing the ellipse.
    upper_left = np.ceil(center - radiuses).astype(int)
    lower_right = np.floor(center + radiuses).astype(int)

    if shape is not None:
        # Constrain upper_left and lower_right by shape boundary.
        upper_left = np.maximum(upper_left, np.array([0, 0]))
        lower_right = np.minimum(lower_right, np.array(shape[:2]) - 1)

    shifted_center = center - upper_left
    bounding_shape = lower_right - upper_left + 1

    rr, cc = _ellipse_in_shape(bounding_shape, shifted_center, radiuses)
    rr.flags.writeable = True
    cc.flags.writeable = True
    rr += upper_left[0]
    cc += upper_left[1]
    return rr, cc


def circle(r, c, radius, shape=None):
    """Generate coordinates of pixels within circle.

    Parameters
    ----------
    r, c : double
        Centre coordinate of circle.
    radius: double
        Radius of circle.
    shape : tuple, optional
        Image shape which is used to determine the maximum extent of output pixel
        coordinates. This is useful for circles which exceed the image size.
        By default the full extent of the circle are used.

    Returns
    -------
    rr, cc : ndarray of int
        Pixel coordinates of circle.
        May be used to directly index into an array, e.g.
        ``img[rr, cc] = 1``.

    Notes
    -----
        This function is a wrapper for skimage.draw.ellipse()

    Examples
    --------
    >>> from skimage.draw import circle
    >>> img = np.zeros((10, 10), dtype=np.uint8)
    >>> rr, cc = circle(4, 4, 5)
    >>> img[rr, cc] = 1
    >>> img
    array([[0, 0, 1, 1, 1, 1, 1, 0, 0, 0],
           [0, 1, 1, 1, 1, 1, 1, 1, 0, 0],
           [1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
           [1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
           [1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
           [1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
           [1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
           [0, 1, 1, 1, 1, 1, 1, 1, 0, 0],
           [0, 0, 1, 1, 1, 1, 1, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], dtype=uint8)

    """

    return ellipse(r, c, radius, radius, shape)


def polygon_perimeter(cy, cx, shape=None, clip=False):
    """Generate polygon perimeter coordinates.

    Parameters
    ----------
    cy : (N,) ndarray
        Y-coordinates of vertices of polygon.
    cx : (N,) ndarray
        X-coordinates of vertices of polygon.
    shape : tuple, optional
        Image shape which is used to determine maximum extents of output pixel
        coordinates. This is useful for polygons which exceed the image size.
        By default the full extents of the polygon are used.
    clip : bool, optional
        Whether to clip the polygon to the provided shape.  If this is set
        to True, the drawn figure will always be a closed polygon with all
        edges visible.

    Returns
    -------
    rr, cc : ndarray of int
        Pixel coordinates of polygon.
        May be used to directly index into an array, e.g.
        ``img[rr, cc] = 1``.

    Examples
    --------
    >>> from skimage.draw import polygon_perimeter
    >>> img = np.zeros((10, 10), dtype=np.uint8)
    >>> rr, cc = polygon_perimeter([5, -1, 5, 10],
    ...                            [-1, 5, 11, 5],
    ...                            shape=img.shape, clip=True)
    >>> img[rr, cc] = 1
    >>> img
    array([[0, 0, 0, 0, 1, 1, 1, 0, 0, 0],
           [0, 0, 0, 1, 0, 0, 0, 1, 0, 0],
           [0, 0, 1, 0, 0, 0, 0, 0, 1, 0],
           [0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
           [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
           [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
           [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
           [0, 1, 1, 0, 0, 0, 0, 0, 0, 1],
           [0, 0, 0, 1, 0, 0, 0, 1, 1, 0],
           [0, 0, 0, 0, 1, 1, 1, 0, 0, 0]], dtype=uint8)

    """
    if clip:
        if shape is None:
            raise ValueError("Must specify clipping shape")
        clip_box = np.array([0, 0, shape[0] - 1, shape[1] - 1])
    else:
        clip_box = np.array([np.min(cy), np.min(cx),
                             np.max(cy), np.max(cx)])

    # Do the clipping irrespective of whether clip is set.  This
    # ensures that the returned polygon is closed and is an array.
    cy, cx = polygon_clip(cy, cx, *clip_box)

    cy = np.round(cy).astype(int)
    cx = np.round(cx).astype(int)

    # Construct line segments
    rr, cc = [], []
    for i in range(len(cy) - 1):
        line_r, line_c = line(cy[i], cx[i], cy[i + 1], cx[i + 1])
        rr.extend(line_r)
        cc.extend(line_c)

    rr = np.asarray(rr)
    cc = np.asarray(cc)

    if shape is None:
        return rr, cc
    else:
        return _coords_inside_image(rr, cc, shape)


def set_color(img, coords, color, alpha=1):
    """Set pixel color in the image at the given coordinates.

    Coordinates that exceed the shape of the image will be ignored.

    Parameters
    ----------
    img : (M, N, D) ndarray
        Image
    coords : tuple of ((P,) ndarray, (P,) ndarray)
        Row and column coordinates of pixels to be colored.
    color : (D,) ndarray
        Color to be assigned to coordinates in the image.
    alpha : scalar or (N,) ndarray
        Alpha values used to blend color with image.  0 is transparent,
        1 is opaque.

    Returns
    -------
    img : (M, N, D) ndarray
        The updated image.

    Examples
    --------
    >>> from skimage.draw import line, set_color
    >>> img = np.zeros((10, 10), dtype=np.uint8)
    >>> rr, cc = line(1, 1, 20, 20)
    >>> set_color(img, (rr, cc), 1)
    >>> img
    array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 1]], dtype=uint8)

    """
    rr, cc = coords

    if img.ndim == 2:
        img = img[..., np.newaxis]

    color = np.array(color, ndmin=1, copy=False)

    if img.shape[-1] != color.shape[-1]:
        raise ValueError('Color shape ({}) must match last '
                         'image dimension ({}).'.format(color.shape[0],
                                                        img.shape[-1]))

    if np.isscalar(alpha):
        # Can be replaced by ``full_like`` when numpy 1.8 becomes
        # minimum dependency
        alpha = np.ones_like(rr) * alpha

    rr, cc, alpha = _coords_inside_image(rr, cc, img.shape, val=alpha)

    alpha = alpha[..., np.newaxis]

    color = color * alpha
    vals = img[rr, cc] * (1 - alpha)

    img[rr, cc] = vals + color
