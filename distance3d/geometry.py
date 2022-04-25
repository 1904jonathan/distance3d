"""Tools for geometric computations."""
import math
import numpy as np


def convert_rectangle_to_segment(rectangle_center, rectangle_extents, i0, i1):
    """Extract line segment from rectangle.

    Parameters
    ----------
    rectangle_center : array, shape (3,)
        Center point of the rectangle.

    rectangle_extents : array, shape (3, 2)
        Extents along axes of the rectangles:
        0.5 * rectangle_sizes * rectangle_axes.

    i0 : int
        Either 0 or 1, selecting line segment.

    i1 : int
        Either 0 or 1, selecting line segment.

    Returns
    -------
    segment_start : array, shape (3,)
        Start point of segment.

    segment_end : array, shape (3,)
        End point of segment.
    """
    segment_middle = rectangle_center + (2 * i0 - 1) * rectangle_extents[i1]
    segment_start = segment_middle - rectangle_extents[1 - i1]
    segment_end = segment_middle + rectangle_extents[1 - i1]
    return segment_end, segment_start


def convert_rectangle_to_vertices(
        rectangle_center, rectangle_axes, rectangle_lengths):
    """Convert rectangle to vertices.

    Parameters
    ----------
    rectangle_center : array, shape (3,)
        Center point of the rectangle.

    rectangle_axes : array, shape (2, 3)
        Each row is a vector of unit length, indicating the direction of one
        axis of the rectangle. Both vectors are orthogonal.

    rectangle_lengths : array, shape (2,)
        Lengths of the two sides of the rectangle.

    Returns
    -------
    rectangle_points : array, shape (4, 3)
        Vertices of the rectangle.
    """
    return np.array([
        rectangle_center
        + 0.5 * a * rectangle_axes[0] * rectangle_lengths[0]
        + 0.5 * b * rectangle_axes[1] * rectangle_lengths[1]
        for a in [-1, 1] for b in [-1, 1]
    ])


def convert_box_to_face(box2origin, size, i, sign):
    """Convert box to face.

    Parameters
    ----------
    box2origin : array, shape (4, 4)
        Pose of the box.

    size : array, shape (3,)
        Size of the box along its axes.

    i : int
        Index of the axis along which we select the face.

    sign : int
        Indicate the direction along the axis.

    Returns
    -------
    face_center : array, shape (3,)
        Center point of the rectangle.

    face_axes : array, shape (2, 3)
        Each row is a vector of unit length, indicating the direction of one
        axis of the rectangle. Both vectors are orthogonal.

    face_lengths : array, shape (2,)
        Lengths of the two sides of the rectangle.
    """
    other_indices = [0, 1, 2]
    other_indices.remove(i)
    face_center = box2origin[:3, 3] + sign * 0.5 * size[i] * box2origin[:3, i]
    face_axes = np.array([box2origin[:3, j] for j in other_indices])
    face_lengths = np.array([size[j] for j in other_indices])
    return face_center, face_axes, face_lengths


def convert_segment_to_line(segment_start, segment_end):
    """Convert line segment to line.

    Parameters
    ----------
    segment_start : array, shape (3,)
        Start point of segment.

    segment_end : array, shape (3,)
        End point of segment.

    Returns
    -------
    segment_direction : array, shape (3,)
        Line direction with unit length (or 0).

    segment_length : float
        Length of the line segment.
    """
    segment_direction = segment_end - segment_start
    segment_length = np.linalg.norm(segment_direction)
    if segment_length > 0:
        segment_direction /= segment_length
    return segment_direction, segment_length


def convert_box_to_vertices(box2origin, size):
    """Convert box to vertices.

    Parameters
    ----------
    box2origin : array, shape (4, 4)
        Pose of the box.

    size : array, shape (3,)
        Size of the box along its axes.

    Returns
    -------
    box_points : array, shape (8, 3)
        Vertices of the box.
    """
    box_points = np.array([
        box2origin[:3, 3]
        + 0.5 * sign0 * box2origin[:3, 0] * size[0]
        + 0.5 * sign1 * box2origin[:3, 1] * size[1]
        + 0.5 * sign2 * box2origin[:3, 2] * size[2]
        for sign0 in [-1, 1] for sign1 in [-1, 1] for sign2 in [-1, 1]])
    return box_points


def cylinder_extreme_along_direction(
        search_direction, cylinder2origin, radius, length):
    """Compute extreme point of cylinder along a direction.

    You can find similar implementations here:

    * https://github.com/kevinmoran/GJK/blob/b38d923d268629f30b44c3cf6d4f9974bbcdb0d3/Collider.h#L42
      (Copyright (c) 2017 Kevin Moran, MIT License or Unlicense)
    * https://github.com/bulletphysics/bullet3/blob/e306b274f1885f32b7e9d65062aa942b398805c2/src/BulletCollision/CollisionShapes/btConvexShape.cpp#L167
      (Copyright (c) 2003-2009 Erwin Coumans, zlib license)

    Parameters
    ----------
    search_direction : array, shape (3,)
        Search direction.

    cylinder2origin : array, shape (4, 4)
        Pose of the cylinder.

    radius : float
        Radius of the cylinder.

    length : float
        Radius of the cylinder.

    Returns
    -------
    extreme_point : array, shape (3,)
        Extreme point along search direction.
    """
    local_dir = np.dot(cylinder2origin[:3, :3].T, search_direction)

    s = math.sqrt(local_dir[0] ** 2 + local_dir[1] ** 2)
    if local_dir[2] < 0.0:
        z = -0.5 * length
    else:
        z = 0.5 * length
    if s != 0.0:
        d = radius / s
        local_vertex = np.array([local_dir[0] * d, local_dir[1] * d, z])
    else:
        local_vertex = np.array([radius, 0.0, z])
    return np.dot(cylinder2origin[:3, :3], local_vertex) + cylinder2origin[:3, 3]


def capsule_extreme_along_direction(
        search_direction, capsule2origin, radius, height):
    """Compute extreme point of cylinder along a direction.

    You can find similar implementations here:

    * https://github.com/kevinmoran/GJK/blob/b38d923d268629f30b44c3cf6d4f9974bbcdb0d3/Collider.h#L42/kevinmoran/GJK/blob/master/Collider.h#L42
      (Copyright (c) 2017 Kevin Moran, MIT License or Unlicense)
    * https://github.com/bulletphysics/bullet3/blob/e306b274f1885f32b7e9d65062aa942b398805c2/src/BulletCollision/CollisionShapes/btConvexShape.cpp#L228
      (Copyright (c) 2003-2009 Erwin Coumans, zlib license)

    Parameters
    ----------
    search_direction : array, shape (3,)
        Search direction.

    capsule2origin : array, shape (4, 4)
        Pose of the capsule.

    radius : float
        Radius of the cylinder.

    height : float
        Height of the cylinder.

    Returns
    -------
    extreme_point : array, shape (3,)
        Extreme point along search direction.
    """
    # TODO error with axis-aligned capsules
    local_dir = np.dot(capsule2origin[:3, :3].T, search_direction)

    s = np.linalg.norm(local_dir)
    if s == 0.0:
        local_vertex = np.zeros(3)
    else:
        local_vertex = local_dir / s * radius
    if local_dir[2] > 0.0:
        local_vertex[2] += 0.5 * height
    else:
        local_vertex[2] -= 0.5 * height

    return np.dot(capsule2origin[:3, :3], local_vertex) + capsule2origin[:3, 3]


def hesse_normal_form(plane_point, plane_normal):
    """Computes Hesse normal form of a plane.

    In the Hesse normal form (x * n - d = 0), x is any point on the plane,
    n is the plane's normal, and d ist the distance from the origin to the
    plane along its normal.

    Parameters
    ----------
    plane_point : array, shape (3,)
        Point on the plane.

    plane_normal : array, shape (3,)
        Normal of the plane. We assume unit length.

    Returns
    -------
    plane_normal : array, shape (3,)
        Normal of the plane. We assume unit length.

    d : float, optional (default: None)
        Distance of the plane to origin in Hesse normal form.
    """
    return plane_normal, np.dot(plane_point, plane_normal)