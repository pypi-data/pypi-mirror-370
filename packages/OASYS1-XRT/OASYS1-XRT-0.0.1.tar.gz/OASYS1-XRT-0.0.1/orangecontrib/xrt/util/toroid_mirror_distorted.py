import os
import scipy
import numpy as np
from xrt.backends.raycing.oes import ToroidMirror


def get_m1_slope_error(x=[-5, 5],
                       nx=51,
                       distorsion_factor=1,
                       fname="/users/srio/OASYS1.2/modelling_team_scripts_and_workspaces/id09/xrt/ID9-toreSESO-D2-P2.slp"):
    # if fname == "2018.05.03_id09_slope_error.txt":
    if os.path.splitext(fname)[1] == ".txt":
        y_mm, dz_dy_mrad = np.loadtxt(fname, unpack=True)
        dz_dy_rad = dz_dy_mrad*1e-3
    # elif fname == "ID9-toreSESO-D2-P2.slp":
    elif os.path.splitext(fname)[1] == ".slp":
        y_mm, dz_dy_urad = np.loadtxt(fname, skiprows=6, unpack=True)
        poly = np.polyfit(y_mm, dz_dy_urad, 1)
        dz_dy_urad = dz_dy_urad - np.polyval(poly, y_mm)
        dz_dy_rad = dz_dy_urad*1e-6
    # elif fname == "dabam-030.dat":
    elif os.path.splitext(fname)[1] == ".dat":
        y_mm, dz_dy_urad = np.loadtxt(fname, unpack=True)
        dz_dy_rad = dz_dy_urad*1e-6
    else:
        raise ValueError(f"'fname' = {fname} not recognized")
    dz_dy_rad *= distorsion_factor
    y_mm -= np.mean(y_mm)
    dz_dy_rad -= np.mean(dz_dy_rad)
    z_mm = scipy.integrate.cumtrapz(dz_dy_rad, x=y_mm, initial=0)
    x_mm = np.linspace(x[0], x[1], nx)
    z_mm = z_mm[:, np.newaxis]
    z_mm = np.repeat(z_mm, nx, axis=1).T
    return x_mm, y_mm, z_mm


class ToroidMirrorDistorted(ToroidMirror):

    def __init__(self, distorsion_factor=1, *args, **kwargs):
        ToroidMirror.__init__(self, *args, **kwargs)
        x = self.limPhysX
        x_dist, y_dist, z_dist = get_m1_slope_error(
            x=x, distorsion_factor=distorsion_factor)
        self.n_x_dist = len(x_dist)
        self.n_y_dist = len(y_dist)
        self.limPhysX = np.min(x_dist), np.max(x_dist)
        self.limPhysY = np.min(y_dist), np.max(y_dist)
        self.get_surface_limits()
        self.x_grad, self.y_grad = np.gradient(z_dist, x_dist, y_dist)
        self.x_grad = np.arctan(self.x_grad)
        self.y_grad = np.arctan(self.y_grad)
        self.z_spline = scipy.ndimage.spline_filter(z_dist)
        self.x_grad_spline = scipy.ndimage.spline_filter(self.x_grad)
        self.y_grad_spline = scipy.ndimage.spline_filter(self.y_grad)

    def local_z_distorted(self, x, y):
        coords = np.array(
            [(x-self.limPhysX[0]) /
             (self.limPhysX[1]-self.limPhysX[0]) * (self.n_x_dist-1),
             (y-self.limPhysY[0]) /
             (self.limPhysY[1]-self.limPhysY[0]) * (self.n_y_dist-1)])
        z = scipy.ndimage.map_coordinates(self.z_spline, coords,
                                          prefilter=True)
        return z

    def local_n_distorted(self, x, y):
        coords = np.array(
            [(x-self.limPhysX[0]) /
             (self.limPhysX[1]-self.limPhysX[0]) * (self.n_x_dist-1),
             (y-self.limPhysY[0]) /
             (self.limPhysY[1]-self.limPhysY[0]) * (self.n_y_dist-1)])
        a = scipy.ndimage.map_coordinates(self.x_grad_spline, coords,
                                          prefilter=True)
        b = scipy.ndimage.map_coordinates(self.y_grad_spline, coords,
                                          prefilter=True)
        return b, -a