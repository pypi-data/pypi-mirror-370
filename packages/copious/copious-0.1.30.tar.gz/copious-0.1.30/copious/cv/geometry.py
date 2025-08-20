from typing import List, Union, Tuple

import numpy as np
from scipy.spatial.transform import Rotation


def xyzq2mat(
    x: float, y: float, z: float, qx: float, qy: float, qz: float, qw: float, as_homo: bool = False
) -> np.ndarray:
    """A helper function that convert xyzq (7 values) representation to transformation matrix representation.

    Parameters
    ----------
    x : float
        x coordinate of the translation
    y : float
        y coordinate of the translation
    z : float
        z coordinate of the translation
    qx : float
        x component of the rotation Quaternion
    qy : float
        y component of the rotation Quaternion
    qz : float
        z component of the rotation Quaternion
    qw : float
        w component of the rotation Quaternion
    as_homo: bool
        if true, the matrix will be saved as homogeneous (4x4), otherwise, it will be saved as 3x4

    Returns
    -------
    np.ndarray
        of shape (3, 4) if as_homo == False, otherwise, (4, 4)
    """
    rot = Rotation.from_quat([qx, qy, qz, qw]).as_matrix()
    T = np.eye(4)
    T[:3, 3] = [x, y, z]
    T[:3, :3] = rot
    if as_homo:
        return T
    return T[:3, :]


def rt2mat(
    rotation: np.ndarray, translation: np.ndarray, as_homo: bool = False
) -> np.ndarray:
    """A helper function that convert rotation matrix (3x3) and translation (3,) to transformation matrix representation.

    Parameters
    ----------
    rotation : np.ndarray
        rotation matrix of shape (3, 3)
    translation : np.ndarray
        translation of shape (3,)
    as_homo: bool
        if true, the matrix will be saved as homogeneous (4x4), otherwise, it will be saved as 3x4

    Returns
    -------
    np.ndarray
        of shape (3, 4) if as_homo == False, otherwise, (4, 4)
    """
    T = np.eye(4)
    T[:3, :3] = rotation
    T[:3, 3] = translation.flatten()
    if as_homo:
        return T
    return T[:3, :]


def euler2mat(x: float, y: float, z: float, as_homo: bool = False, axis_order: str = "XYZ", degrees: bool = True) -> np.ndarray:
    """A helper function that convert euler angles (3 values) representation to transformation matrix representation.

    Parameters
    ----------
    x : float
        x coordinate of the translation
    y : float
        y coordinate of the translation
    z : float
        z coordinate of the translation
    as_homo: bool
        if true, the matrix will be saved as homogeneous (4x4), otherwise, it will be saved as 3x4

    Returns
    -------
    np.ndarray
        of shape (3, 4) if as_homo == False, otherwise, (4, 4)
    """
    rot = np.eye(4)
    rot[:3, :3] = Rotation.from_euler(axis_order, [x, y, z], degrees=degrees).as_matrix()
    if as_homo:
        return rot
    return rot[:3, :3]


def points3d_to_homo(points3d: np.ndarray) -> np.ndarray:
    return np.concatenate((points3d, np.ones(len(points3d))[:, None]), axis=1)


def homo_to_points3d(points_homo: np.ndarray) -> np.ndarray:
    return points_homo[:, :3]


class Box3d:
    def __init__(self, position: np.ndarray, scale: np.ndarray, rotation: Rotation, corners_template: np.ndarray = None) -> None:
        """_summary_

        Parameters
        ----------
        position : np.ndarray
            of shape (3, )
        scale : np.ndarray
            of shape (3, )
        rotation : scipy.spatial.transform.Rotation
            rotation
        corners_template: 
            default template looks as follows

                (2) +---------+. (3)
                    | ` .   fr|  ` .
                    | (6) +---+-----+ (7)
                    |     |   |   bk|
                (1) +-----+---+. (0)|
                    ` .   |     ` . |
                    (5) ` +---------+ (4)
            
        Returns
        -------
        _type_
            _description_
        """
        self.position = position
        self.scale = scale
        self.rotation = rotation
        self._corners = None
        self.corners_template = corners_template
        if self.corners_template is None:
            self.corners_template = np.array([
                [0.5, -0.5, -0.5],
                [0.5, 0.5, -0.5],
                [0.5, 0.5, 0.5],
                [0.5, -0.5, 0.5],
                [-0.5, -0.5, -0.5],
                [-0.5, 0.5, -0.5],
                [-0.5, 0.5, 0.5],
                [-0.5, -0.5, 0.5],
            ])
    
    @property
    def corners(self) -> np.ndarray:
        """
        Returns
        -------
        np.ndarray
            of shape (8, 3)
        """
        if self._corners is None:
            self._corners = self.calc_box_corners()
        return self._corners
    
    def calc_box_corners(self) -> np.ndarray:
        """
        Parameters
        -------
        np.ndarray
            of shape (8, 3)
        """
        corners = self.corners_template.copy()
        corners = corners * self.scale[None]
        corners = corners @ self.rotation.as_matrix().T
        corners = corners + self.position
        return corners

    @classmethod
    def from_pos_scale_euler(cls, pos_x: float, pos_y: float, pos_z: float, scale_x: float, scale_y: float, scale_z: float, rot_euler_x: float, rot_euler_y: float, rot_euler_z: float, seq: str = "XYZ", degrees: bool = False,):
        pos = np.array([pos_x, pos_y, pos_z], dtype=np.float32)
        scale = np.array([scale_x, scale_y, scale_z], dtype=np.float32)
        rot = Rotation.from_euler(seq, [rot_euler_x, rot_euler_y, rot_euler_z], degrees=degrees)
        return cls(pos, scale, rot)


__all__ = ["xyzq2mat", "rt2mat", "euler2mat", "points3d_to_homo", "homo_to_points3d", "Box3d"]
