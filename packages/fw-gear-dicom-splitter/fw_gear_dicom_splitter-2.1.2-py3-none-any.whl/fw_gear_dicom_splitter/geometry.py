import logging
import math

import numpy
import numpy as np

# This is used for type hints only
from numpy import ndarray

log = logging.getLogger(__name__)


def compute_normal(orientation: ndarray) -> ndarray:
    """
    Computes the normal (cross product) of an image orientation vector

    Args:
        orientation (ndarray): Vector from image orientation patient (n=6)

    Returns:
        ndarray : 3D vector normal to the input orientation
    """
    rv = np.array(orientation[0:3])
    cv = np.array(orientation[3:6])
    return np.cross(rv, cv)


def compute_axis_from_pair(p1: ndarray, p2: ndarray) -> ndarray:
    """
    Computes the unit vector connecting p1 to p2

    Args:
        p1 (ndarray) : First point
        p2 (ndarray) : 2nd point

    Returns:
        ndarray: 3D normalized vector that connects p1 to p2
    """
    if p1 is None or p2 is None:
        return None
    assert len(p1) == len(p2)
    axis = np.subtract(p2, p1)
    # Compute magnitude of the vector connecting the origins
    mag = math.fabs(np.linalg.norm(axis))
    # if mag is valid, normalize to return unit vector
    if mag > 0.001:
        axis /= mag
    else:
        # This means the points are nearly degenerate and we should
        # not use them
        axis = None
    return axis


def compute_axis_from_origins(position_list: ndarray) -> ndarray:
    """
    Compute the axis that connects the first pair of non-degenerate slice locations

    Args:
        position_list (ndarray) : List of image position patient per frame

    Returns:
        ndarray: 3D normalized vector that connects the first non-degenerate pair of points
    """
    if len(position_list) < 2:
        return None
    p0 = position_list[0]
    next_index = 1
    # Check first pair
    axis: object = compute_axis_from_pair(p0, position_list[next_index])
    # While the two origins are degenerate...
    while axis is None:
        # Sample the pair of the next origin and the first one
        next_index = next_index + 1
        if next_index >= len(position_list):
            # Need to break if we reach end of list
            log.debug("End of list reached before axis could be successfully computed.")
            break
        axis = compute_axis_from_pair(p0, position_list[next_index])
    return axis


def compute_slice_locations_from_origins(
    origin_list: ndarray, ortho_axis: ndarray = None
) -> ndarray:
    """
    Computes slice positions along an axis connecting a sequence of origins

    Args:
        origin_list (ndarray) : List of image position patient per frame
        ortho_axis (ndarray) : Unit vector along which locations are computed (may be None)

    Returns:
        ndarray: Array of scalar slice positions as dot product of ortho_axis against origin_list
    """
    n = len(origin_list)
    axis = ortho_axis
    if axis is None:
        # Compute axis connecting the origins of the positions
        # This is done versus using a normal to handle condition of gantry tilt
        axis = compute_axis_from_origins(origin_list)
        if axis is None:
            # Various conditions lead to no axis. One of them is if all slices are degenerate
            log.debug("No axis identified.")
            return None
    # Convert slice positions to numpy array
    if not isinstance(origin_list, ndarray):
        origin_list = np.asarray(origin_list)
    # Reshape array as n 3D coordinates
    origin_list = origin_list.reshape((n, 3))
    # Compute dot product of axis against each 3D coordinate
    return np.dot(origin_list, axis)


def compute_slice_spacing_from_locations(slice_locations: ndarray) -> float:
    """
    Compute scalar slice spacing from the vector of slice locations.

    If the slice spacing is not uniform, None is returned

    Args:
        slice_locations (ndarray) : Vector of scalar slice locations (position along slice axis)

    Returns:
        float: Uniform spacing between locations (None if the spacing is not uniform)
    """
    vdiff = np.diff(slice_locations).round(decimals=2)
    slice_spacing = None
    if len(vdiff) < 1:
        return slice_spacing
    min, max = vdiff.min(), vdiff.max()
    if np.isclose(min, max, atol=0.01):
        slice_spacing = min
    else:
        # Return None to indicate non uniform slice spacing
        log.debug("Slice spacing is not uniform.")
        slice_spacing = None
    return slice_spacing


def is_uniform(v: ndarray, decimals=2) -> bool:
    """
    Returns whether the input array has uniform values within a tolerance

    Args:
        v (ndarray) : A vector of dimensionality 1-2
        decimals (int) : Rounding precision of values within the vector

    Returns:
        bool: Whether the vector has uniform values within the specified rounding precision
    """
    if not isinstance(v, ndarray):
        v = numpy.asarray(v)
    v = v.round(decimals=decimals)
    n_dims = len(v.shape)
    if n_dims == 1:
        vdiff = np.diff(v)
        return numpy.isclose(vdiff.min(), vdiff.max())
    else:
        v0 = v[0]
        for index in range(1, len(v)):
            v1 = v[index]
            if not numpy.array_equal(v0, v1):
                return False
        return True


def split_by_geometry(
    orientations: ndarray, origins: ndarray, max_split=-1
) -> tuple[int, list]:
    """
    Computes a split by the number of "phases" from geometry defined by an array of slice
    orientations and origins.

    Args:
        orientations (ndarray): Vector from image orientation patient of size n
        origins (ndarray): Vector from image position patient of size n
        max_split (int) : Maximum number of allowed splits (ignored if < 0)

    Returns:
        tuple[int,list[int]] : Count of phases and corresponding array mapping
            position in orientations,origins with the phase index
    """
    if not isinstance(orientations, ndarray):
        orientations = numpy.asarray(orientations)
    phase_count, indexes = split_by_orientation(orientations, max_split)
    log.info(f"Geometric split by orientation phase count: {phase_count}")
    if phase_count > 1:
        return phase_count, indexes
    if len(origins) > 1 and is_uniform(orientations):
        locations = compute_slice_locations_from_origins(origins)
        if locations is not None:
            phase_count, indexes = split_by_location(locations, max_split)
            log.info(f"Geometric split by location phase count: {phase_count}")
    return phase_count, indexes


def split_by_orientation(
    orientations: ndarray, max_split: int = -1
) -> tuple[int, ndarray]:
    """
    Splits by a change in consecutive orientations

    Args:
        orientations (ndarray): Vector from image orientation patient
        max_split (int) : Maximum number of allowed splits (ignored if < 0)

    Returns:
        tuple[int, ndarray]: A tuple consisting of two elements:
            - An integer representing the number of phases detected.
            - An ndarray indicating the phase assignment for each orientation value.
    """
    n = len(orientations)
    if n == 0:
        return 1, []

    # Start by incrementing phase at each change in orientation
    normal_list = []
    phases_by_index = []
    phase_index = 0
    last_normal = None
    for index in range(n):
        v = orientations[index]
        normal = compute_normal(v).round(decimals=4)
        normal_list.append(normal)
        if last_normal is not None:
            if not numpy.allclose(normal, last_normal):
                log.debug(f"Orientation change detected. Normal: {normal}")
                phase_index += 1  # Increment phase, orientation changed detected
        phases_by_index.append(phase_index)
        last_normal = normal
    phase_count = phase_index + 1

    if 1 < max_split < phase_count:
        log.info(f"Max split exceeded, calculated phase count = {phase_count}")
        return 1, numpy.zeros(shape=n)

    # Return split assignments for non radial condition
    return phase_count, numpy.asarray(phases_by_index)


def split_by_location(locations: ndarray, max_split: int = -1) -> tuple[int, ndarray]:
    """
    Splits by the number of "phases" from an array of slice locations and
    returns a vector with the phase index for each location. A phase in this context
    refers to a sequence of monotonic slice locations.

    Args:
        locations (ndarray): Vector of computed slice locations
        max_split (int) : Maximum number of allowed splits (ignored if < 0)

    Returns:
        tuple[int, ndarray]: A tuple consisting of two elements:
            - An integer representing the number of phases detected.
            - An ndarray indicating the phase assignment for each orientation value.
    """
    n = len(locations)
    if n < 2:
        return 1, numpy.zeros(shape=n)

    # Ensure that locations is an ndarray
    if not isinstance(locations, ndarray):
        location = numpy.asarray(locations)  # noqa
    # Round all slice locations to nearest 0.01 mm
    locations = np.round(locations, decimals=2)

    # Lines from Anchor A-B below are computing the number of sign changes in the direction of locations
    # Example: Computations below upon a locations vector with 2 direction changes and thus 3 phases
    # locations =   [1,3,5,7,9, 5,7,9,11,13,15,  1, 3, 5, 7, 9,11]
    # indexes =     [  1,2,3,4, 5,6,7, 8, 9,10, 11,12,13,14,15,15]
    # vdiff1 =      [  2,2,2, 2,-4,2,2,2,2,  2,-14, 2, 2, 2, 2, 2]
    # shift_vdiff1= [  2,2,2,-4, 2,2,2,2,2,-14,  2, 2, 2, 2, 2, 2]
    # c =           [  4,4,4,-8,-8,4,4,4,4,-28,-28, 4, 4, 4, 4, 4]
    # phase_pos   [0,0,0,0,0, 1, 1,1,1,1,1,  2,  2, 2, 2, 2, 2, 2]

    # Compute vector of slice spacings (i.e. difference in slice positions)
    # Anchor A
    vdiff1 = np.diff(locations)
    length = len(vdiff1)

    # Construct indexes array
    indexes = np.arange(1, length + 1).astype(int)
    indexes[length - 1] = length - 1

    # Prepare array that is vdiff shifted one index to the right
    shift_vdiff1 = np.take(vdiff1, indexes)
    # Multiply vdiff against shift such that +/- reflects sign change
    c = vdiff1 * shift_vdiff1
    # Anchor B

    # Accumulate array where each position encodes the phase index
    phase_index = 0
    phase_pos_list = [0]
    for k in range(n - 1):
        # Assign phase_index to position k
        phase_pos_list.append(phase_index)
        # Condition for a new phase. Increment the phase shift on a negative
        # number occurring
        if (k < (n - 1)) and (c[k] < 0) and (k > 0) and (c[k - 1] >= 0):
            # Next k will have the incremented phase index
            phase_index += 1

    # Phase count is just the last phase index plus 1
    phase_count = phase_index + 1

    # Detect special condition to look for degenerate slice locations
    # This is tested in test_geometry.py with test_compute_phases_with_deg_slice_locations
    non_zero_count = np.count_nonzero(vdiff1)
    degen_count = length - non_zero_count
    if degen_count > 0 and (non_zero_count > 0):
        group_size = int(n / non_zero_count)
        number_of_groups = int(n / group_size)
        # Test for condition of groups of degenerate slice locations
        # For n groups of 3, for example, this pattern is [(0,1,2)xn]
        # Clear out phase_pos_list and reassign from this pattern
        if group_size * number_of_groups == n:
            phase_pos_list = []
            for k in range(n):
                m = k % group_size
                phase_pos_list.append(m)
            phase_count = group_size

    if 1 < max_split < phase_count:
        log.info(f"Max split exceeded, calculated phase count = {phase_count}")
        return 1, numpy.zeros(shape=n)

    return phase_count, np.asarray(phase_pos_list, dtype=int)
