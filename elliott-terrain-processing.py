"""
Falklands Terrain Pipeline
Processes SRTM elevation data and exports a patch-level terrain map
for use in NetLogo.
"""

import os
import csv
import numpy as np
import rasterio
from rasterio.windows import from_bounds
from rasterio.enums import Resampling
from rasterio.merge import merge
from scipy.ndimage import gaussian_filter
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

import os
import glob

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

GEOTIFF_FOLDER = os.path.join(BASE_DIR, "GEOTiff Files")

SRTM_PATH = glob.glob(os.path.join(GEOTIFF_FOLDER, "*.tif"))

if len(SRTM_PATH) == 0:
    raise RuntimeError("No GeoTIFF files found in GEOTiff Files folder.")

print("Found DEM files:")
for f in SRTM_PATH:
    print("  ", f)

BBOX = {
    "south": -53,
    "north": -51,
    "west": -62,
    "east": -58
}

METERS_PER_PATCH = 1000
PATCH_COLS = 120
PATCH_ROWS = 100

OUTPUT_DIR = "output"


# --------------------------------------------------
# TERRAIN CLASSES
# --------------------------------------------------

TERRAIN_CLASSES = {
    "moorland": {"move_cost": 1.0},
    "ridge": {"move_cost": 1.2},
    "bog": {"move_cost": 1.7},
    "urban": {"move_cost": 1.1},
    "water": {"move_cost": 9999}
}


# --------------------------------------------------
# WIND EXPOSURE
# --------------------------------------------------

WIND_EFFECT = {
    "moorland": {"wind_exposure": 1.0},
    "ridge": {"wind_exposure": 1.5},
    "bog": {"wind_exposure": 0.8},
    "urban": {"wind_exposure": 0.7},
    "water": {"wind_exposure": 1.2}
}


# --------------------------------------------------
# TERRAIN COLORS
# --------------------------------------------------

TERRAIN_COLORS = {
    "moorland": "#4CAF50",
    "bog": "#1B5E20",
    "ridge": "#9E9E9E",
    "urban": "#D32F2F",
    "water": "#1976D2"
}


# --------------------------------------------------
# MERGE GEO TIFFS
# --------------------------------------------------

def merge_geotiffs(files):

    src_files = [rasterio.open(f) for f in files]

    mosaic, transform = merge(src_files)

    elev_grid = mosaic[0]

    for src in src_files:
        src.close()

    return elev_grid, transform


# --------------------------------------------------
# LOAD DEM
# --------------------------------------------------

def load_srtm(path):

    if isinstance(path, list):

        print("Merging GeoTIFF tiles...")

        elev, transform = merge_geotiffs(path)

        return elev

    with rasterio.open(path) as src:

        window = from_bounds(
            BBOX["west"],
            BBOX["south"],
            BBOX["east"],
            BBOX["north"],
            src.transform
        )

        data = src.read(
            1,
            window=window,
            out_shape=(PATCH_ROWS, PATCH_COLS),
            resampling=Resampling.bilinear
        )

        return data.astype(float)


# --------------------------------------------------
# TERRAIN FEATURE DERIVATION
# --------------------------------------------------

def slope_degrees(grid):

    gy, gx = np.gradient(grid, METERS_PER_PATCH, METERS_PER_PATCH)

    return np.degrees(np.arctan(np.sqrt(gx**2 + gy**2)))


def relative_elevation(grid):

    return grid - gaussian_filter(grid, sigma=16)


# --------------------------------------------------
# TERRAIN CLASSIFICATION
# --------------------------------------------------

def classify_terrain(elev, slope, rel_elev):

    terrain = np.full(elev.shape, "moorland", dtype=object)

    # Water detection
    terrain[elev <= 0] = "water"

    # Ridge detection
    ridge_mask = (slope > 12) & (rel_elev > 2)
    terrain[ridge_mask] = "ridge"

    # Bog detection
    bog_mask = (rel_elev < -2) & (slope < 5)
    terrain[bog_mask] = "bog"

    return terrain


# --------------------------------------------------
# EXPORT CSV
# --------------------------------------------------

def export_csv(elev, slope, rel_elev, terrain, path):

    rows, cols = elev.shape

    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", newline="") as f:

        writer = csv.writer(f)

        writer.writerow([
            "pxcor",
            "pycor",
            "elevation_m",
            "slope_deg",
            "rel_elevation_m",
            "terrain_type",
            "move_cost",
            "wind_exposure"
        ])

        for r in range(rows):

            for c in range(cols):

                terrain_type = terrain[r, c]

                writer.writerow([
                    c,
                    (rows - 1) - r,
                    round(float(elev[r, c]), 2),
                    round(float(slope[r, c]), 2),
                    round(float(rel_elev[r, c]), 2),
                    terrain_type,
                    TERRAIN_CLASSES[terrain_type]["move_cost"],
                    WIND_EFFECT[terrain_type]["wind_exposure"]
                ])


# --------------------------------------------------
# PREVIEW IMAGE
# --------------------------------------------------

def save_preview(elev, terrain, path):

    rows, cols = elev.shape

    color_img = np.zeros((rows, cols, 3))

    for ttype, hexcol in TERRAIN_COLORS.items():
        color_img[terrain == ttype] = mcolors.to_rgb(hexcol)

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.imshow(color_img, origin="upper", aspect="auto")

    ax.set_title("Falklands Terrain Classification")

    plt.savefig(path, dpi=150)

    plt.close()


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():

    elev = load_srtm(SRTM_PATH)

    slope = slope_degrees(elev)

    rel_elev = relative_elevation(elev)

    terrain = classify_terrain(elev, slope, rel_elev)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    csv_path = os.path.join(OUTPUT_DIR, "terrain_patch_map.csv")

    export_csv(elev, slope, rel_elev, terrain, csv_path)

    png_path = os.path.join(OUTPUT_DIR, "preview.png")

    save_preview(elev, terrain, png_path)

def main():

    print("Merging GeoTIFF tiles...")

    elev = load_srtm(SRTM_PATH)

    # calculate slope and relative elevation
    slope = slope_degrees(elev)
    rel_elev = relative_elevation(elev)

    # classify terrain
    terrain = classify_terrain(elev, slope, rel_elev)

    print("Resampling DEM to 1 km grid...")

    # convert terrain types to numeric codes
    terrain_codes = {
        "moorland": 1,
        "bog": 2,
        "ridge": 3,
        "urban": 4,
        "water": 5
    }

    terrain_numeric = np.vectorize(terrain_codes.get)(terrain)

    scale_factor = int(1000 / 30)

    rows = terrain_numeric.shape[0] // scale_factor * scale_factor
    cols = terrain_numeric.shape[1] // scale_factor * scale_factor

    terrain_trimmed = terrain_numeric[:rows, :cols]

    terrain_1km = terrain_trimmed.reshape(
        rows // scale_factor,
        scale_factor,
        cols // scale_factor,
        scale_factor
    ).mean(axis=(1,3))

    # ensure output folder exists
    OUTPUT_DIR = os.path.join(BASE_DIR, "output")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    csv_path = os.path.join(OUTPUT_DIR, "terrain_patch_map.csv")

    np.savetxt(csv_path, terrain_1km, delimiter=",")

    print("Saved terrain grid to:", csv_path)
    print("Falklands terrain pipeline complete.")


if __name__ == "__main__":
    main()