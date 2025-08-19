import itertools
import math

import numpy as np

EPS = np.finfo(float).eps * 4.0
"""
Utility functions of matrix and vector transformations.

NOTE: convention for quaternions is (x, y, z, w)
"""

# For testing whether a number is close to zero
_FLOAT_EPS = np.finfo(np.float64).eps
_EPS4 = _FLOAT_EPS * 4.0


def euler2mat(euler):
    """Convert Euler Angles to Rotation Matrix.

    See rotation.py for notes
    """
    euler = np.asarray(euler, dtype=np.float64)
    assert euler.shape[-1] == 3, f"Invalid shaped euler {euler}"

    ai, aj, ak = -euler[..., 2], -euler[..., 1], -euler[..., 0]
    si, sj, sk = np.sin(ai), np.sin(aj), np.sin(ak)
    ci, cj, ck = np.cos(ai), np.cos(aj), np.cos(ak)
    cc, cs = ci * ck, ci * sk
    sc, ss = si * ck, si * sk

    mat = np.empty(euler.shape[:-1] + (3, 3), dtype=np.float64)
    mat[..., 2, 2] = cj * ck
    mat[..., 2, 1] = sj * sc - cs
    mat[..., 2, 0] = sj * cc + ss
    mat[..., 1, 2] = cj * sk
    mat[..., 1, 1] = sj * ss + cc
    mat[..., 1, 0] = sj * cs - sc
    mat[..., 0, 2] = -sj
    mat[..., 0, 1] = cj * si
    mat[..., 0, 0] = cj * ci
    return mat


def euler2quat(euler):
    """Convert Euler Angles to Quaternions.

    See rotation.py for notes
    """
    euler = np.asarray(euler, dtype=np.float64)
    assert euler.shape[-1] == 3, f"Invalid shape euler {euler}"

    ai, aj, ak = euler[..., 2] / 2, -euler[..., 1] / 2, euler[..., 0] / 2
    si, sj, sk = np.sin(ai), np.sin(aj), np.sin(ak)
    ci, cj, ck = np.cos(ai), np.cos(aj), np.cos(ak)
    cc, cs = ci * ck, ci * sk
    sc, ss = si * ck, si * sk

    quat = np.empty(euler.shape[:-1] + (4,), dtype=np.float64)
    quat[..., 0] = cj * cc + sj * ss
    quat[..., 3] = cj * sc - sj * cs
    quat[..., 2] = -(cj * ss + sj * cc)
    quat[..., 1] = cj * cs - sj * sc
    return quat


def mat2euler(mat):
    """Convert Rotation Matrix to Euler Angles.

    See rotation.py for notes
    """
    mat = np.asarray(mat, dtype=np.float64)
    assert mat.shape[-2:] == (3, 3), f"Invalid shape matrix {mat}"

    cy = np.sqrt(mat[..., 2, 2] * mat[..., 2, 2] + mat[..., 1, 2] * mat[..., 1, 2])
    condition = cy > _EPS4
    euler = np.empty(mat.shape[:-1], dtype=np.float64)
    euler[..., 2] = np.where(
        condition,
        -np.arctan2(mat[..., 0, 1], mat[..., 0, 0]),
        -np.arctan2(-mat[..., 1, 0], mat[..., 1, 1]),
    )
    euler[..., 1] = np.where(
        condition, -np.arctan2(-mat[..., 0, 2], cy), -np.arctan2(-mat[..., 0, 2], cy)
    )
    euler[..., 0] = np.where(
        condition, -np.arctan2(mat[..., 1, 2], mat[..., 2, 2]), 0.0
    )
    return euler


def mat2quat(rmat):
    """
    Converts given rotation matrix to quaternion.

    Args:
        rmat (np.array): 3x3 rotation matrix

    Returns:
        np.array: (x,y,z,w) float quaternion angles
    """
    M = np.asarray(rmat).astype(np.float32)[:3, :3]

    m00 = M[0, 0]
    m01 = M[0, 1]
    m02 = M[0, 2]
    m10 = M[1, 0]
    m11 = M[1, 1]
    m12 = M[1, 2]
    m20 = M[2, 0]
    m21 = M[2, 1]
    m22 = M[2, 2]
    # symmetric matrix K
    K = np.array(
        [
            [m00 - m11 - m22, np.float32(0.0), np.float32(0.0), np.float32(0.0)],
            [m01 + m10, m11 - m00 - m22, np.float32(0.0), np.float32(0.0)],
            [m02 + m20, m12 + m21, m22 - m00 - m11, np.float32(0.0)],
            [m21 - m12, m02 - m20, m10 - m01, m00 + m11 + m22],
        ]
    )
    K /= 3.0
    # quaternion is Eigen vector of K that corresponds to largest eigenvalue
    w, V = np.linalg.eigh(K)
    inds = np.array([3, 0, 1, 2])
    q1 = V[inds, np.argmax(w)]
    if q1[0] < 0.0:
        np.negative(q1, q1)
    inds = np.array([1, 2, 3, 0])
    return q1[inds]


def quat2euler(quat):
    """Convert Quaternion to Euler Angles.

    See rotation.py for notes
    """
    return mat2euler(quat2mat(quat))


def subtract_euler(e1, e2):
    assert e1.shape == e2.shape
    assert e1.shape[-1] == 3
    q1 = euler2quat(e1)
    q2 = euler2quat(e2)
    q_diff = quat_mul(q1, quat_conjugate(q2))
    return quat2euler(q_diff)


def quat2mat(quaternion):
    """
    Converts given quaternion to matrix.

    Args:
        quaternion (np.array): (x,y,z,w) vec4 float angles

    Returns:
        np.array: 3x3 rotation matrix
    """
    # awkward semantics for use with numba
    inds = np.array([3, 0, 1, 2])
    q = np.asarray(quaternion).copy().astype(np.float32)[inds]

    n = np.dot(q, q)
    if n < EPS:
        return np.identity(3)
    q *= math.sqrt(2.0 / n)
    q2 = np.outer(q, q)
    return np.array(
        [
            [1.0 - q2[2, 2] - q2[3, 3], q2[1, 2] - q2[3, 0], q2[1, 3] + q2[2, 0]],
            [q2[1, 2] + q2[3, 0], 1.0 - q2[1, 1] - q2[3, 3], q2[2, 3] - q2[1, 0]],
            [q2[1, 3] - q2[2, 0], q2[2, 3] + q2[1, 0], 1.0 - q2[1, 1] - q2[2, 2]],
        ]
    )


def quat_conjugate(q):
    inv_q = -q
    inv_q[..., 0] *= -1
    return inv_q


def quat_mul(q0, q1):
    assert q0.shape == q1.shape
    assert q0.shape[-1] == 4
    assert q1.shape[-1] == 4

    w0 = q0[..., 0]
    x0 = q0[..., 1]
    y0 = q0[..., 2]
    z0 = q0[..., 3]

    w1 = q1[..., 0]
    x1 = q1[..., 1]
    y1 = q1[..., 2]
    z1 = q1[..., 3]

    w = w0 * w1 - x0 * x1 - y0 * y1 - z0 * z1
    x = w0 * x1 + x0 * w1 + y0 * z1 - z0 * y1
    y = w0 * y1 + y0 * w1 + z0 * x1 - x0 * z1
    z = w0 * z1 + z0 * w1 + x0 * y1 - y0 * x1
    q = np.array([w, x, y, z])
    if q.ndim == 2:
        q = q.swapaxes(0, 1)
    assert q.shape == q0.shape
    return q


def quat_rot_vec(q, v0):
    q_v0 = np.array([0, v0[0], v0[1], v0[2]])
    q_v = quat_mul(q, quat_mul(q_v0, quat_conjugate(q)))
    v = q_v[1:]
    return v


def quat_identity():
    return np.array([1, 0, 0, 0])


def quat2axisangle(quat):
    theta = 0
    axis = np.array([0, 0, 1])
    sin_theta = np.linalg.norm(quat[1:])

    if sin_theta > 0.0001:
        theta = 2 * np.arcsin(sin_theta)
        theta *= 1 if quat[0] >= 0 else -1
        axis = quat[1:] / sin_theta

    return axis, theta


def euler2point_euler(euler):
    _euler = euler.copy()
    if len(_euler.shape) < 2:
        _euler = np.expand_dims(_euler, 0)
    assert _euler.shape[1] == 3
    _euler_sin = np.sin(_euler)
    _euler_cos = np.cos(_euler)
    return np.concatenate([_euler_sin, _euler_cos], axis=-1)


def point_euler2euler(euler):
    _euler = euler.copy()
    if len(_euler.shape) < 2:
        _euler = np.expand_dims(_euler, 0)
    assert _euler.shape[1] == 6
    angle = np.arctan(_euler[..., :3] / _euler[..., 3:])
    angle[_euler[..., 3:] < 0] += np.pi
    return angle


def quat2point_quat(quat):
    # Should be in qw, qx, qy, qz
    _quat = quat.copy()
    if len(_quat.shape) < 2:
        _quat = np.expand_dims(_quat, 0)
    assert _quat.shape[1] == 4
    angle = np.arccos(_quat[:, [0]]) * 2
    xyz = _quat[:, 1:]
    xyz[np.squeeze(np.abs(np.sin(angle / 2))) >= 1e-5] = (xyz / np.sin(angle / 2))[
        np.squeeze(np.abs(np.sin(angle / 2))) >= 1e-5
    ]
    return np.concatenate([np.sin(angle), np.cos(angle), xyz], axis=-1)


def point_quat2quat(quat):
    _quat = quat.copy()
    if len(_quat.shape) < 2:
        _quat = np.expand_dims(_quat, 0)
    assert _quat.shape[1] == 5
    angle = np.arctan(_quat[:, [0]] / _quat[:, [1]])
    qw = np.cos(angle / 2)

    qxyz = _quat[:, 2:]
    qxyz[np.squeeze(np.abs(np.sin(angle / 2))) >= 1e-5] = (qxyz * np.sin(angle / 2))[
        np.squeeze(np.abs(np.sin(angle / 2))) >= 1e-5
    ]
    return np.concatenate([qw, qxyz], axis=-1)


def normalize_angles(angles):
    """Puts angles in [-pi, pi] range."""
    angles = angles.copy()
    if angles.size > 0:
        angles = (angles + np.pi) % (2 * np.pi) - np.pi
        assert -np.pi - 1e-6 <= angles.min() and angles.max() <= np.pi + 1e-6
    return angles


def round_to_straight_angles(angles):
    """Returns closest angle modulo 90 degrees."""
    angles = np.round(angles / (np.pi / 2)) * (np.pi / 2)
    return normalize_angles(angles)


def get_parallel_rotations():
    mult90 = [0, np.pi / 2, -np.pi / 2, np.pi]
    parallel_rotations = []
    for euler in itertools.product(mult90, repeat=3):
        canonical = mat2euler(euler2mat(euler))
        canonical = np.round(canonical / (np.pi / 2))
        if canonical[0] == -2:
            canonical[0] = 2
        if canonical[2] == -2:
            canonical[2] = 2
        canonical *= np.pi / 2
        if all([(canonical != rot).any() for rot in parallel_rotations]):
            parallel_rotations += [canonical]
    assert len(parallel_rotations) == 24
    return parallel_rotations


def unit_vector(data, axis=None, out=None):
    """
    Returns ndarray normalized by length, i.e. eucledian norm, along axis.
    E.g.:
        >>> v0 = numpy.random.random(3)
        >>> v1 = unit_vector(v0)
        >>> numpy.allclose(v1, v0 / numpy.linalg.norm(v0))
        True
        >>> v0 = numpy.random.rand(5, 4, 3)
        >>> v1 = unit_vector(v0, axis=-1)
        >>> v2 = v0 / numpy.expand_dims(numpy.sqrt(numpy.sum(v0*v0, axis=2)), 2)
        >>> numpy.allclose(v1, v2)
        True
        >>> v1 = unit_vector(v0, axis=1)
        >>> v2 = v0 / numpy.expand_dims(numpy.sqrt(numpy.sum(v0*v0, axis=1)), 1)
        >>> numpy.allclose(v1, v2)
        True
        >>> v1 = numpy.empty((5, 4, 3), dtype=numpy.float32)
        >>> unit_vector(v0, axis=1, out=v1)
        >>> numpy.allclose(v1, v2)
        True
        >>> list(unit_vector([]))
        []
        >>> list(unit_vector([1.0]))
        [1.0]
    Args:
        data (np.array): data to normalize
        axis (None or int): If specified, determines specific axis along data to normalize
        out (None or np.array): If specified, will store computation in this variable
    Returns:
        None or np.array: If @out is not specified, will return normalized vector. Otherwise, stores the output in @out
    """
    if out is None:
        data = np.array(data, dtype=np.float32, copy=True)
        if data.ndim == 1:
            data /= math.sqrt(np.dot(data, data))
            return data
    else:
        if out is not data:
            out[:] = np.array(data, copy=False)
        data = out
    length = np.atleast_1d(np.sum(data * data, axis))
    np.sqrt(length, length)
    if axis is not None:
        length = np.expand_dims(length, axis)
    data /= length
    if out is None:
        return data


def quat_slerp(quat0, quat1, fraction, shortestpath=True):
    """
    Return spherical linear interpolation between two quaternions.
    E.g.:
    >>> q0 = random_quat()
    >>> q1 = random_quat()
    >>> q = quat_slerp(q0, q1, 0.0)
    >>> np.allclose(q, q0)
    True
    >>> q = quat_slerp(q0, q1, 1.0)
    >>> np.allclose(q, q1)
    True
    >>> q = quat_slerp(q0, q1, 0.5)
    >>> angle = math.acos(np.dot(q0, q))
    >>> np.allclose(2.0, math.acos(np.dot(q0, q1)) / angle) or \
        np.allclose(2.0, math.acos(-np.dot(q0, q1)) / angle)
    True
    Args:
        quat0 (np.array): (x,y,z,w) quaternion startpoint
        quat1 (np.array): (x,y,z,w) quaternion endpoint
        fraction (float): fraction of interpolation to calculate
        shortestpath (bool): If True, will calculate the shortest path
    Returns:
        np.array: (x,y,z,w) quaternion distance
    """
    q0 = unit_vector(quat0[:4])
    q1 = unit_vector(quat1[:4])
    if fraction == 0.0:
        return q0
    elif fraction == 1.0:
        return q1
    d = np.dot(q0, q1)
    if abs(abs(d) - 1.0) < _EPS4:
        return q0
    if shortestpath and d < 0.0:
        # invert rotation
        d = -d
        q1 *= -1.0
    angle = math.acos(np.clip(d, -1, 1))
    if abs(angle) < _EPS4:
        return q0
    isin = 1.0 / math.sin(angle)
    q0 *= math.sin((1.0 - fraction) * angle) * isin
    q1 *= math.sin(fraction * angle) * isin
    q0 += q1
    return q0


def make_pose(translation, rotation):
    """
    Makes a homogeneous pose matrix from a translation vector and a rotation matrix.

    Args:
        translation (np.array): (x,y,z) translation value
        rotation (np.array): a 3x3 matrix representing rotation

    Returns:
        pose (np.array): a 4x4 homogeneous matrix
    """
    pose = np.zeros((4, 4))
    pose[:3, :3] = rotation
    pose[:3, 3] = translation
    pose[3, 3] = 1.0
    return pose


def axisangle2quat(vec):
    """
    Converts scaled axis-angle to quat.

    Args:
        vec (np.array): (ax,ay,az) axis-angle exponential coordinates

    Returns:
        np.array: (x,y,z,w) vec4 float angles
    """
    # Grab angle
    angle = np.linalg.norm(vec)

    # handle zero-rotation case
    if math.isclose(angle, 0.0):
        return np.array([0.0, 0.0, 0.0, 1.0])

    # make sure that axis is a unit vector
    axis = vec / angle

    q = np.zeros(4)
    q[3] = np.cos(angle / 2.0)
    q[:3] = axis * np.sin(angle / 2.0)
    return q


def pose_inv(pose):
    """
    Computes the inverse of a homogeneous matrix corresponding to the pose of some
    frame B in frame A. The inverse is the pose of frame A in frame B.

    Args:
        pose (np.array): 4x4 matrix for the pose to inverse

    Returns:
        np.array: 4x4 matrix for the inverse pose
    """

    # Note, the inverse of a pose matrix is the following
    # [R t; 0 1]^-1 = [R.T -R.T*t; 0 1]

    # Intuitively, this makes sense.
    # The original pose matrix translates by t, then rotates by R.
    # We just invert the rotation by applying R-1 = R.T, and also translate back.
    # Since we apply translation first before rotation, we need to translate by
    # -t in the original frame, which is -R-1*t in the new frame, and then rotate back by
    # R-1 to align the axis again.

    pose_inv = np.zeros((4, 4))
    pose_inv[:3, :3] = pose[:3, :3].T
    pose_inv[:3, 3] = -pose_inv[:3, :3].dot(pose[:3, 3])
    pose_inv[3, 3] = 1.0
    return pose_inv


def pose_in_A_to_pose_in_B(pose_A, pose_A_in_B):
    """
    Converts a homogenous matrix corresponding to a point C in frame A
    to a homogenous matrix corresponding to the same point C in frame B.

    Args:
        pose_A (np.array): 4x4 matrix corresponding to the pose of C in frame A
        pose_A_in_B (np.array): 4x4 matrix corresponding to the pose of A in frame B

    Returns:
        np.array: 4x4 matrix corresponding to the pose of C in frame B
    """

    # pose of A in B takes a point in A and transforms it to a point in C.

    # pose of C in B = pose of A in B * pose of C in A
    # take a point in C, transform it to A, then to B
    # T_B^C = T_A^C * T_B^A
    return pose_A_in_B.dot(pose_A)


def mat2pose(hmat):
    """
    Converts a homogeneous 4x4 matrix into pose.

    Args:
        hmat (np.array): a 4x4 homogeneous matrix

    Returns:
        2-tuple:

            - (np.array) (x,y,z) position array in cartesian coordinates
            - (np.array) (x,y,z,w) orientation array in quaternion form
    """
    pos = hmat[:3, 3]
    orn = mat2quat(hmat[:3, :3])
    return pos, orn
