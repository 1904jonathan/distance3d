import math
import numpy as np
from ..geometry import hesse_normal_form
from ._line import point_to_line


def point_to_disk(point, center, radius, normal):
    """Compute the shortest distance between point and disk.

    Implementation adapted from 3D Game Engine Design by David H. Eberly.

    Geometric Tools, Inc.
    http://www.geometrictools.com
    Copyright (c) 1998-2006.  All Rights Reserved

    The Wild Magic Version 4 Foundation Library source code is supplied
    under the terms of the license agreement
    (http://www.geometrictools.com/License/Wm4FoundationLicense.pdf)
    and may not be copied or disclosed except in accordance with the terms
    of that agreement.

    Parameters
    ----------
    point : array, shape (3,)
        3D point.

    center : array, shape (3,)
        Center of the disk.

    radius : float
        Radius of the disk.

    normal : array, shape (3,)
        Normal to the plane in which the disk lies.

    Returns
    -------
    dist : float
        The shortest distance between point and disk.

    closest_point_disk : array, shape (3,)
        Closest point on the disk.
    """
    # signed distance from point to plane of disk
    diff = point - center
    dist_to_plane = diff.dot(normal)

    # projection of P - C onto plane is Q - C = P - C - dist_to_plane * normal
    diff_in_plane = diff - dist_to_plane * normal
    sqr_len = diff_in_plane.dot(diff_in_plane)

    length = math.sqrt(sqr_len)
    t = radius
    if length != 0.0:
        t /= length
    closest_point_disk = center + min(1.0, t) * diff_in_plane

    return np.linalg.norm(point - closest_point_disk), closest_point_disk


def disk_to_disk(center1, radius1, normal1, center2, radius2, normal2, epsilon=1e-8):
    """Compute the shortest distance between two disks.

    Parameters
    ----------
    center1 : array, shape (3,)
        Center of the disk.

    radius1 : float
        Radius of the disk.

    normal1 : array, shape (3,)
        Normal to the plane in which the disk lies.

    center2 : array, shape (3,)
        Center of the disk.

    radius2 : float
        Radius of the disk.

    normal2 : array, shape (3,)
        Normal to the plane in which the disk lies.

    epsilon : float, optional (default: 1e-8)
        Values smaller than epsilon are considered to be 0.

    Returns
    -------
    dist : float
        The shortest distance between two disks.

    closest_point_disk1 : array, shape (3,)
        Closest point on the disk 1.

    closest_point_disk2 : array, shape (3,)
        Closest point on the disk 2.
    """
    # (1) test intersection first (source: https://stackoverflow.com/a/67116330/915743)
    # Plücker coordinates of intersection line
    line_direction, line_moment = plane_intersects_plane(center1, normal1, center2, normal2)
    line_point = np.cross(line_direction, line_moment) / np.dot(line_direction, line_direction)
    h1, p1 = point_to_line(center1, line_point, line_direction)
    h2, p2 = point_to_line(center2, line_point, line_direction)
    ell = np.linalg.norm(p2 - p1)
    h = h1 + h2
    if abs(h) > epsilon:
        t1 = h1 * ell / h
        closest_to_both_disks = p1 - line_direction * t1
        if np.linalg.norm(closest_to_both_disks - center1) < radius1 and np.linalg.norm(closest_to_both_disks - center2) < radius2:
            return 0.0, closest_to_both_disks, closest_to_both_disks
    elif ell <= radius1 + radius2:  # both centers are on the common line
        contact = 0.5 * (center1 + center2)
        return 0.0, contact, contact

    # (2) no contact: simple iterative procedure
    # better solution: https://www.sciencedirect.com/science/article/pii/S0307904X0200080X
    _, contact_point_disk2 = point_to_disk(center1, center2, radius2, normal2)
    prev_dist = np.linalg.norm(center2 - center1)
    for i in range(20):
        _, contact_point_disk1 = point_to_disk(
            contact_point_disk2, center1, radius1, normal1)
        _, contact_point_disk2 = point_to_disk(
            contact_point_disk1, center2, radius2, normal2)
        dist = np.linalg.norm(contact_point_disk2 - contact_point_disk1)
        if prev_dist - dist < epsilon:
            break
        prev_dist = dist
    return np.linalg.norm(contact_point_disk2 - contact_point_disk1), contact_point_disk1, contact_point_disk2


# TODO find a better place
def plane_intersects_plane(
        plane_point1, plane_normal1, plane_point2, plane_normal2):
    _, d1 = hesse_normal_form(plane_point1, plane_normal1)
    _, d2 = hesse_normal_form(plane_point2, plane_normal2)
    line_direction = np.cross(plane_normal1, plane_normal2)
    line_moment = plane_normal1 * d2 - plane_normal2 * d1
    return line_direction, line_moment
