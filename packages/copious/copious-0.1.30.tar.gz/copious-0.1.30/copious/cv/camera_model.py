from functools import partial
from typing import Tuple

import cv2
import numpy as np
from scipy.optimize import curve_fit


EPS_FLOAT32 = float(np.finfo(np.float32).eps)


class FisheyeCameraModel:
    def __init__(
        self,
        pp: Tuple[float, float],
        focal: Tuple[float, float],
        inv_poly: Tuple[float, float, float, float],
        image_size: Tuple[int, int],
        fov: int,
    ):
        self.pp = pp
        self.focal = focal
        self.inv_poly = np.array(inv_poly, dtype=np.float32)
        self.image_size = image_size
        self.fov = fov
        self.intrinsic_mat = np.array(
            [
                [self.focal[0], 0, self.pp[0]],
                [0, self.focal[1], self.pp[1]],
                [0, 0, 1],
            ],
            dtype=np.float32,
        )

    @staticmethod
    def fit_unproj_func(p0, p1, p2, p3, fov=200):

        def proj_func(x, params):
            p0, p1, p2, p3 = params
            return x + p0 * x**3 + p1 * x**5 + p2 * x**7 + p3 * x**9

        def poly_odd6(x, k0, k1, k2, k3, k4, k5):
            """
            $$f(x) = x + k_0 x^3 + k_1 x^5 + k_2 x^7 + k_3 x^9 + k_4 x^{11} + k_5 x^{13}$$
            """
            return x + k0 * x**3 + k1 * x**5 + k2 * x**7 + k3 * x**9 + k4 * x**11 + k5 * x**13

        theta = np.linspace(-0.5 * fov * np.pi / 180, 0.5 * fov * np.pi / 180, num=fov * 500)
        theta_d = proj_func(theta, (p0, p1, p2, p3))
        params, pcov = curve_fit(poly_odd6, theta_d, theta)
        error = np.sqrt(np.diag(pcov)).mean()
        assert error < 3.1e-3, f"poly parameter curve fitting failed: {error}. ({params=})"
        k0, k1, k2, k3, k4, k5 = params
        return partial(poly_odd6, k0=k0, k1=k1, k2=k2, k3=k3, k4=k4, k5=k5)

    def unproject_points(self, points):
        unproj_func = self.fit_unproj_func(*self.inv_poly[:4], fov=self.fov)
        cx, cy = self.pp
        fx, fy = self.focal
        u = points[:, 0]
        v = points[:, 1]
        x_distorted = (u - cx) / fx
        y_distorted = (v - cy) / fy
        r_distorted = theta_distorted = np.sqrt(x_distorted**2 + y_distorted**2)
        r_distorted[r_distorted < 1e-5] = 1e-5
        theta = unproj_func(r_distorted)
        theta = np.clip(theta, -0.5 * self.fov * np.pi / 180, 0.5 * self.fov * np.pi / 180)
        vignette_mask = np.float32(np.abs(theta * 180 / np.pi) < self.fov / 2)
        # camera coords on a sphere x-y-z right-down-forward
        dd = np.sin(theta)
        xx = x_distorted * dd / r_distorted
        yy = y_distorted * dd / r_distorted
        zz = np.cos(theta)
        fisheye_cam_coords = np.stack([xx, yy, zz], axis=1)
        return fisheye_cam_coords

    def project_points(self, points: np.ndarray) -> np.ndarray:
        xc = points[:, 0]
        yc = points[:, 1]
        zc = points[:, 2]
        norm = np.sqrt(xc**2 + yc**2)
        theta = np.arctan2(norm, zc)
        fov_mask = theta > self.fov / 2 * np.pi / 180
        rho = (
            theta
            + self.inv_poly[0] * theta**3
            + self.inv_poly[1] * theta**5
            + self.inv_poly[2] * theta**7
            + self.inv_poly[3] * theta**9
        )
        width, height = self.image_size
        image_radius = np.sqrt((width / 2) ** 2 + (height) ** 2)
        rho[fov_mask] = 2 * image_radius / self.focal[0]
        xn = rho * xc / norm
        yn = rho * yc / norm
        xn[norm < EPS_FLOAT32] = 0
        yn[norm < EPS_FLOAT32] = 0
        norm_coords = np.stack([xn, yn, np.ones_like(xn)], axis=1)
        intrinsic_mat = np.array(
            [
                [self.focal[0], 0, self.pp[0]],
                [0, self.focal[1], self.pp[1]],
                [0, 0, 1],
            ],
            dtype=np.float32,
        )

        image_coords = norm_coords @ intrinsic_mat.T
        return image_coords[:, :2]

    def undistort_image(self, image: np.ndarray) -> np.ndarray:
        return cv2.fisheye.undistortImage(
            distorted=image, K=self.intrinsic_mat, D=self.inv_poly[:4], Knew=self.intrinsic_mat
        )

    def undistort_points(self, points: np.ndarray, out_as_homo=True) -> np.ndarray:
        """Undistort 2D points on distorted image to 2D points on undistorted image."""
        norm_coords_homo = self.unproject_points(points)
        undistorted_points_on_image = (
            norm_coords_homo @ self.intrinsic_mat.T
        )  # 用小孔相机（假设无畸变）的方式将相机系中的3D点投到图像上
        if not out_as_homo:
            undistorted_points_on_image = undistorted_points_on_image[:, :2] / undistorted_points_on_image[:, 2:]
        return undistorted_points_on_image
