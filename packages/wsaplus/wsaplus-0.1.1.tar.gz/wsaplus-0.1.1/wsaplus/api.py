"""Public API for generating WSA+ solar wind speed maps.

This module refactors the core logic from the raw wsaplus.py
script into a reusable library.
"""

from __future__ import annotations

import os
import warnings
from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np
import torch
import astropy.units as u
import sunpy.map
from astropy.constants import R_sun
from astropy.coordinates import SkyCoord
from astropy.io import fits
from sunpy.coordinates.sun import carrington_rotation_time
from pfsspy.tracing import FortranTracer
import pfsspy
from pfsspy.utils import fix_hmi_meta
from sklearn.neighbors import BallTree
from scipy.interpolate import griddata
from numba import njit
from joblib import Parallel, delayed

from .model import WSASurrogateModel

# Reduce noisy warnings from dependencies
warnings.filterwarnings(
    "ignore", message="At least one field line ran out of steps during tracing."
)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
CPU_COUNT = int(os.getenv("WSAPLUS_CPU", "6"))


@dataclass
class WsaPlusResult:
    speed_kms: np.ndarray  # [360, 180]
    phi_grid_deg: np.ndarray  # [360, 180]
    theta_grid_deg: np.ndarray  # [360, 180]
    features: dict  # optional extra artifacts


# --------------------------- Magnetogram I/O ---------------------------

def load_magnetogram(path: str, mag_type: str = "GONG"):
    mag_type = mag_type.upper()
    if mag_type == "GONG":
        amap = sunpy.map.Map(path)
        # sanitize meta
        amap.meta.update(
            {
                "bunit": "G",
                "cunit1": "degree",
                "rsun_ref": 696000000.0,
                "rsun_obs": 696000000.0,
            }
        )
        input_map = sunpy.map.Map(amap.data - np.mean(amap.data), amap.meta)
        return input_map
    elif mag_type == "HMI":
        amap = sunpy.map.Map(path)
        fix_hmi_meta(amap)
        input_map = amap.resample([360, 180] * u.pix)
        return input_map
    else:
        raise ValueError("mag_type must be 'GONG' or 'HMI'")


# --------------------------- PFSS + features ---------------------------

def _pfss(input_map):
    nrho = 100
    rss = 2.50
    pfss_input = pfsspy.Input(input_map, nrho, rss)
    output = pfsspy.pfss(pfss_input)

    source_surface_radius = rss * R_sun
    solar_surface_radius = 1.0 * R_sun

    n_points = 180
    phi = np.linspace(0.0, 2.0 * np.pi, 2 * n_points + 1)[:-1]
    sin_theta = np.linspace(-1.0, 1.0, n_points)
    theta = np.arcsin(sin_theta)

    Theta, Phi = np.meshgrid(theta, phi, indexing="ij")
    Theta, Phi = Theta * u.rad, Phi * u.rad

    open_footpoints = SkyCoord(
        radius=source_surface_radius, lat=Theta.ravel(), lon=Phi.ravel(), frame=output.coordinate_frame
    )
    closed_footpoints = SkyCoord(
        radius=solar_surface_radius, lat=Theta.ravel(), lon=Phi.ravel(), frame=output.coordinate_frame
    )

    tracer = FortranTracer(step_size=0.5)
    backward_fieldlines = tracer.trace(open_footpoints, output)
    forward_fieldlines = tracer.trace(closed_footpoints, output)
    open_mask = forward_fieldlines.connectivities
    open_grid = open_mask.reshape(180, 360)

    Br_sun = input_map.data.T

    return output, backward_fieldlines, forward_fieldlines, Br_sun, open_grid


# Numba-accelerated expansion factor
@njit
def _calculate_expansion_factors(r_solar, r_ss, Br_solar, Br_ss):
    return r_solar * r_solar * Br_solar / (r_ss * r_ss * Br_ss)


def _extract_closed_coords(forward_fieldlines):
    def process_field_line(field_line):
        latitudes, longitudes = [], []
        if not field_line.is_open:
            coordinates = field_line.coords
            if len(coordinates) > 0:
                latitudes.extend([coordinates[0].lat.value, coordinates[-1].lat.value])
                longitudes.extend([coordinates[0].lon.value, coordinates[-1].lon.value])
        return latitudes, longitudes

    results = Parallel(n_jobs=CPU_COUNT, backend="loky")(
        delayed(process_field_line)(fl) for fl in forward_fieldlines
    )

    clats, clons = [], []
    for lats, lons in results:
        clats.extend(lats)
        clons.extend(lons)

    return np.array(clats) * u.deg, np.array(clons) * u.deg


def _fieldlines_data(output, backward_fieldlines, forward_fieldlines):
    closed_lat, closed_lon = _extract_closed_coords(forward_fieldlines)

    phi_solar = backward_fieldlines.open_field_lines.solar_feet.lon
    theta_solar = backward_fieldlines.open_field_lines.solar_feet.lat
    r_solar = backward_fieldlines.open_field_lines.solar_feet.radius
    Br_solar = output.get_bvec(backward_fieldlines.open_field_lines.solar_feet)[:, 0]

    phi_ss = backward_fieldlines.open_field_lines.source_surface_feet.lon
    theta_ss = backward_fieldlines.open_field_lines.source_surface_feet.lat
    r_ss = backward_fieldlines.open_field_lines.source_surface_feet.radius
    Br_ss = output.get_bvec(backward_fieldlines.open_field_lines.source_surface_feet)[:, 0]

    exp_factors = _calculate_expansion_factors(
        r_solar.value, r_ss.value, Br_solar.value, Br_ss.value
    )

    open_points = np.vstack(
        (np.radians(theta_solar.value), np.radians(phi_solar.value))
    ).T
    closed_points = np.vstack(
        (np.radians(closed_lat.value), np.radians(closed_lon.value))
    ).T

    tree = BallTree(closed_points, metric="haversine")

    if len(open_points) > 10000:
        chunk_size = len(open_points) // CPU_COUNT
        chunks = [open_points[i : i + chunk_size] for i in range(0, len(open_points), chunk_size)]

        def process_chunk(chunk):
            return tree.query(chunk, k=1)

        results = Parallel(n_jobs=CPU_COUNT, backend="loky")(
            delayed(process_chunk)(chunk) for chunk in chunks
        )
        distances = np.concatenate([r[0] for r in results])
    else:
        distances, _ = tree.query(open_points, k=1)

    min_dist_deg = np.degrees(distances).flatten()
    return min_dist_deg, exp_factors, theta_ss, phi_ss, Br_ss


# --------------------------- Gridding ---------------------------

def _interpolate_to_grid(phi_ss, theta_ss, min_distances, exp_factors, Br_ss):
    n_points = 180
    phi_grid = np.linspace(0.0, 2.0 * np.pi, 2 * n_points + 1)[:-1] * 180 / np.pi
    sin_theta = np.linspace(-1.0, 1.0, n_points)
    theta_grid = np.arcsin(sin_theta) * 180 / np.pi

    Phi_grid, Theta_grid = np.meshgrid(phi_grid, theta_grid, indexing="ij")

    theta_ss_deg = theta_ss.value
    phi_ss_deg = phi_ss.value

    def interp(values):
        lin = griddata((phi_ss_deg, theta_ss_deg), values, (Phi_grid, Theta_grid), method="linear")
        near = griddata((phi_ss_deg, theta_ss_deg), values, (Phi_grid, Theta_grid), method="nearest")
        mask = np.isnan(lin)
        out = lin.copy()
        out[mask] = near[mask]
        return out

    min_dist_grid = interp(min_distances)

    exp_safe = np.copy(exp_factors)
    exp_safe[exp_safe <= 0] = 1.0
    log_exp = np.log10(exp_safe)
    exp_grid = interp(log_exp)

    Br_grid = interp(Br_ss.value)

    return Phi_grid, Theta_grid, min_dist_grid, exp_grid, Br_grid


# --------------------------- Inference ---------------------------

def _compute_wsaplus_speed(min_distances_grid, exp_factors_grid, checkpoint_path: str, device=None):
    device = device or DEVICE

    f_min, f_max = -4.0, 6.0
    d_min, d_max = 0.0, 25.0

    f_norm = np.clip((exp_factors_grid - f_min) / (f_max - f_min), 0, 1)
    d_norm = np.clip((min_distances_grid - d_min) / (d_max - d_min), 0, 1)

    f_norm = torch.tensor(f_norm, dtype=torch.float32, device=device)
    d_norm = torch.tensor(d_norm, dtype=torch.float32, device=device)

    input_maps = torch.stack([f_norm, d_norm], dim=0).unsqueeze(0)

    model = WSASurrogateModel().to(device)
    if not os.path.exists(checkpoint_path):
        raise FileNotFoundError(
            f"WSA+ checkpoint not found: {checkpoint_path}. Provide --checkpoint or set WSAPLUS_CHECKPOINT."
        )
    ckpt = torch.load(checkpoint_path, map_location=device)
    state_key = 'model_state' if 'model_state' in ckpt else 'state_dict'
    model.load_state_dict(ckpt[state_key])
    model.eval()

    with torch.no_grad():
        wsaplus_speed = model(input_maps)[0, 0].detach().cpu().numpy()

    return wsaplus_speed


# --------------------------- Public API ---------------------------

def generate_wsaplus_map(
    magnetogram_path: str,
    mag_type: str = "GONG",
    checkpoint_path: Optional[str] = None,
    device: Optional[torch.device] = None,
    n_cpu: Optional[int] = None,
) -> WsaPlusResult:
    """
    Generate a WSA+ solar wind speed map at 0.1 AU from a synoptic magnetogram.

    Returns a WsaPlusResult with speed map and lat/lon grids (degrees).
    """
    device = device or DEVICE

    if n_cpu is not None:
        global CPU_COUNT
        CPU_COUNT = int(n_cpu)
    
    checkpoint_path = (
        checkpoint_path
        or os.getenv("WSAPLUS_CHECKPOINT")
        or os.path.join(os.path.expanduser("~/.cache/wsaplus"), "wsaplus.pt")
    )

    input_map = load_magnetogram(magnetogram_path, mag_type)
    output, back_fl, fwd_fl, Br_sun, open_grid = _pfss(input_map)
    min_d, exp_f, theta_ss, phi_ss, Br_ss = _fieldlines_data(output, back_fl, fwd_fl)
    Phi_grid, Theta_grid, min_d_grid, exp_grid, Br_grid = _interpolate_to_grid(
        phi_ss, theta_ss, min_d, exp_f, Br_ss
    )

    wsaplus_speed = _compute_wsaplus_speed(min_d_grid, exp_grid, checkpoint_path, device=device)

    features = {
        "min_distance_deg": min_d_grid,
        "log10_expansion": exp_grid,
        "Br_source_surface": Br_grid,
    }
    return WsaPlusResult(
        speed_kms=wsaplus_speed,
        phi_grid_deg=Phi_grid,
        theta_grid_deg=Theta_grid,
        features=features,
    )
