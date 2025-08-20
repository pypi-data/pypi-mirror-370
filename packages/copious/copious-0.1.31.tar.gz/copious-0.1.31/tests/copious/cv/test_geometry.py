import math

import pytest
import numpy as np
from scipy.spatial.transform import Rotation

from copious.cv.geometry import points3d_to_homo, Box3d, xyzq2mat, euler2mat, rt2mat


def test_to_homo():
    np.testing.assert_almost_equal(
        points3d_to_homo(
            np.array([[0, 2, 3], [0.1, -0.2, 0.3]])
        ),
        np.array([[0, 2, 3, 1], [0.1, -0.2, 0.3, 1]])
    )


@pytest.fixture
def box3d_psr_1():
    return [0, 0, 0, 5, 2, 1.8, 0, 0, math.pi / 2]


@pytest.fixture
def box3d_psr_2():
    return [6, 8, -0.05, 5, 2, 1.8, 0, 0, -math.pi / 2]


@pytest.fixture
def box3d_psr_3a():
    return [0, 0, 0, 6, 2, 1.6, -0.5236, 0, 0]  # rotate along x-axis by -30 degrees


@pytest.fixture
def box3d_psr_3b():
    return [0, 0, 0, 2, 6, 1.6, -0.5236, 0, 1.5707963268]  # rotate along x-axis by -30 degrees, then z-axis by 90 degrees (seq: "xyz")


@pytest.fixture
def box3d_psr_4a():
    return [0.4797, -1.9767,  0.0239, 0.4303, 3.3381, 0.0359, -0.0076, 0.0099, 1.8197]


@pytest.fixture
def box3d_psr_4b():
    return [0.4797, -1.9767,  0.0239, 3.3381, 0.4303, 0.0359, -0.0076,  0.0099, -2.892689]


def test_box3d_get_corners1(box3d_psr_1):
    box = Box3d.from_pos_scale_euler(*box3d_psr_1, degrees=False)
    np.testing.assert_almost_equal(box.corners, np.array([
        [1.0,  2.5, -0.9],
        [-1.0, 2.5, -0.9],
        [-1.0, 2.5, 0.9],
        [1.0,  2.5, 0.9],
        [1.0,  -2.5, -0.9],
        [-1.0, -2.5, -0.9],
        [-1.0, -2.5, 0.9],
        [1.0,  -2.5, 0.9],
    ]))


def test_box3d_get_corners2(box3d_psr_2):
    box = Box3d.from_pos_scale_euler(*box3d_psr_2, degrees=False)
    np.testing.assert_almost_equal(box.corners, np.array([
        [5.0,  5.5, -0.95],
        [7.0,  5.5, -0.95],
        [7.0,  5.5, 0.85],
        [5.0,  5.5, 0.85],
        [5.0, 10.5, -0.95],
        [7.0, 10.5, -0.95],
        [7.0, 10.5, 0.85],
        [5.0, 10.5, 0.85],
    ]))


def test_box3d_get_corners3(box3d_psr_3a):
    box = Box3d.from_pos_scale_euler(*box3d_psr_3a, degrees=False)
    np.testing.assert_almost_equal(box.corners, np.array([
        [ 3.0, -1.2660254, -0.19282032],
        [ 3.0,  0.4660254, -1.19282032],
        [ 3.0,  1.2660254,  0.19282032],
        [ 3.0, -0.4660254,  1.19282032],
        [-3.0, -1.2660254, -0.19282032],
        [-3.0,  0.4660254, -1.19282032],
        [-3.0,  1.2660254,  0.19282032],
        [-3.0, -0.4660254,  1.19282032],
    ]), decimal=4)


def test_box3d_get_corners_4(box3d_psr_3a, box3d_psr_3b):
    box1 = Box3d.from_pos_scale_euler(*box3d_psr_3a, degrees=False)
    box2 = Box3d.from_pos_scale_euler(*box3d_psr_3b, degrees=False, seq="XYZ")
    np.testing.assert_almost_equal(box1.corners[[1, 5, 4, 0]], box2.corners[[0, 1, 5, 4]])


def test_box3d_get_corners_5(box3d_psr_4a, box3d_psr_4b):
    box1 = Box3d.from_pos_scale_euler(*box3d_psr_4a, degrees=False)
    box2 = Box3d.from_pos_scale_euler(*box3d_psr_4b, degrees=False)
    np.testing.assert_almost_equal(box1.corners[[1, 5, 4, 0]], box2.corners[[0, 1, 5, 4]])


def test_xyzq2mat_homogeneous_matrix_shape():
    # Test when as_homo is True
    homo_matrix = xyzq2mat(1, 2, 3, 0, 0, 0, 1, True)
    assert homo_matrix.shape == (4, 4), "Homogeneous matrix should be 4x4"

def test_xyzq2mat_non_homogeneous_matrix_shape():
    # Test when as_homo is False
    non_homo_matrix = xyzq2mat(1, 2, 3, 0, 0, 0, 1, False)
    assert non_homo_matrix.shape == (3, 4), "Non-homogeneous matrix should be 3x4"

def test_xyzq2mat_default_as_homo():
    # Test when as_homo is not provided (should default to False)
    default_matrix = xyzq2mat(1, 2, 3, 0, 0, 0, 1)
    assert default_matrix.shape == (3, 4), "Default matrix should be 3x4 when as_homo is not provided"

def test_xyzq2mat_translation_components():
    # Check if the translation components are set correctly for both cases
    homo_matrix = xyzq2mat(1, 2, 3, 0, 0, 0, 1, True)
    non_homo_matrix = xyzq2mat(1, 2, 3, 0, 0, 0, 1, False)
    np.testing.assert_array_equal(homo_matrix[:3, 3], [1, 2, 3])
    np.testing.assert_array_equal(non_homo_matrix[:, 3], [1, 2, 3])

def test_xyzq2mat_rotation_matrix_validity():
    # Identity quaternion should produce an identity rotation matrix for both cases
    homo_matrix = xyzq2mat(0, 0, 0, 0, 0, 0, 1, True)
    non_homo_matrix = xyzq2mat(0, 0, 0, 0, 0, 0, 1, False)
    expected_rotation = np.eye(3)
    np.testing.assert_array_almost_equal(homo_matrix[:3, :3], expected_rotation)
    np.testing.assert_array_almost_equal(non_homo_matrix[:3, :3], expected_rotation)



def test_xyzq2mat_matrix_shape():
    # Test both homogeneous and non-homogeneous output shapes
    homo_matrix = xyzq2mat(1, 2, 3, 0, 0, 0, 1, True)
    non_homo_matrix = xyzq2mat(1, 2, 3, 0, 0, 0, 1, False)
    assert homo_matrix.shape == (4, 4), "Homogeneous matrix should be 4x4"
    assert non_homo_matrix.shape == (3, 4), "Non-homogeneous matrix should be 3x4"


def test_xyzq2mat_identity_quaternion():
    # Identity quaternion with zero translation
    matrix = xyzq2mat(0, 0, 0, 0, 0, 0, 1, True)
    expected_matrix = np.eye(4)
    np.testing.assert_array_almost_equal(matrix, expected_matrix)

def test_xyzq2mat_non_identity_quaternion():
    # Non-identity quaternion (90 degrees rotation around z-axis)
    matrix = xyzq2mat(0, 0, 0, 0, 0, np.sqrt(0.5), np.sqrt(0.5), False)
    expected_rotation = np.array([[0, -1, 0], [1, 0, 0], [0, 0, 1]])
    np.testing.assert_array_almost_equal(matrix[:3, :3], expected_rotation)

def test_xyzq2mat_zero_translation():
    # Zero translation with an identity quaternion
    matrix = xyzq2mat(0, 0, 0, 0, 0, 0, 1, False)
    expected_matrix = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0]])
    np.testing.assert_array_almost_equal(matrix, expected_matrix)


def test_euler2mat_default():
    x, y, z = 45, 30, 60
    result = euler2mat(x, y, z)
    expected_rot = Rotation.from_euler('XYZ', [x, y, z], degrees=True).as_matrix()
    np.testing.assert_almost_equal(result, expected_rot, decimal=6)

def test_euler2mat_homogeneous():
    x, y, z = 45, 30, 60
    result = euler2mat(x, y, z, as_homo=True)
    expected_rot = np.eye(4)
    expected_rot[:3, :3] = Rotation.from_euler('XYZ', [x, y, z], degrees=True).as_matrix()
    np.testing.assert_almost_equal(result, expected_rot, decimal=6)

def test_euler2mat_axis_order():
    x, y, z = 45, 30, 60
    result = euler2mat(x, y, z, axis_order='ZYX')
    expected_rot = Rotation.from_euler('ZYX', [x, y, z], degrees=True).as_matrix()
    np.testing.assert_almost_equal(result, expected_rot, decimal=6)

def test_euler2mat_radians():
    x, y, z = np.pi/4, np.pi/6, np.pi/3
    result = euler2mat(x, y, z, degrees=False)
    expected_rot = Rotation.from_euler('XYZ', [x, y, z], degrees=False).as_matrix()
    np.testing.assert_almost_equal(result, expected_rot, decimal=6)

def test_euler2mat_homogeneous_radians():
    x, y, z = np.pi/4, np.pi/6, np.pi/3
    result = euler2mat(x, y, z, as_homo=True, degrees=False)
    expected_rot = np.eye(4)
    expected_rot[:3, :3] = Rotation.from_euler('XYZ', [x, y, z], degrees=False).as_matrix()
    np.testing.assert_almost_equal(result, expected_rot, decimal=6)

def test_euler2mat_custom_order_homogeneous():
    x, y, z = 45, 30, 60
    result = euler2mat(x, y, z, as_homo=True, axis_order='YXZ')
    expected_rot = np.eye(4)
    expected_rot[:3, :3] = Rotation.from_euler('YXZ', [x, y, z], degrees=True).as_matrix()
    np.testing.assert_almost_equal(result, expected_rot, decimal=6)

def test_euler2mat_zero_angles():
    x, y, z = 0, 0, 0
    result = euler2mat(x, y, z)
    expected_rot = np.eye(3)
    np.testing.assert_almost_equal(result, expected_rot, decimal=6)

def test_euler2mat_zero_angles_homogeneous():
    x, y, z = 0, 0, 0
    result = euler2mat(x, y, z, as_homo=True)
    expected_rot = np.eye(4)
    np.testing.assert_almost_equal(result, expected_rot, decimal=6)


def test_non_identity_rotation():
    rotation = np.array([[0, -1, 0],
                         [1, 0, 0],
                         [0, 0, 1]])
    translation = np.array([1, 2, 3])
    expected = np.hstack([rotation, translation.reshape(-1, 1)])
    result = rt2mat(rotation, translation, as_homo=False)
    np.testing.assert_array_equal(result, expected)


def test_homogeneous_conversion():
    rotation = np.array([[0, -1, 0],
                         [1, 0, 0],
                         [0, 0, 1]])
    translation = np.array([1, 2, 3])
    expected = np.eye(4)
    expected[:3, :3] = rotation
    expected[:3, 3] = translation
    result = rt2mat(rotation, translation, as_homo=True)
    np.testing.assert_array_equal(result, expected)


def test_translation_column_vector():
    rotation = np.eye(3)
    translation = np.array([[1], [2], [3]])  # Shape (3, 1)
    expected = np.hstack([rotation, np.array([1, 2, 3]).reshape(-1, 1)])
    result = rt2mat(rotation, translation, as_homo=False)
    np.testing.assert_array_equal(result, expected)


def test_output_shapes():
    rotation = np.eye(3)
    translation = np.zeros(3)
    assert rt2mat(rotation, translation).shape == (3, 4)
    assert rt2mat(rotation, translation, as_homo=True).shape == (4, 4)
