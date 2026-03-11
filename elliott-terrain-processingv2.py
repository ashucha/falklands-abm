import os
import numpy as np
import rasterio

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DEM_PATH = os.path.join(BASE_DIR, "GEOTiff Files", "merged_output.tif")


def load_srtm(path):
    with rasterio.open(path) as src:
        elev = src.read(1)
    return elev


def slope_degrees(elev):

    dzdx = np.gradient(elev, axis=1)
    dzdy = np.gradient(elev, axis=0)

    slope = np.sqrt(dzdx**2 + dzdy**2)

    return slope


def relative_elevation(elev):

    kernel_size = 25

    pad = kernel_size // 2

    padded = np.pad(elev, pad, mode="edge")

    rel = np.zeros_like(elev)

    for i in range(rel.shape[0]):
        for j in range(rel.shape[1]):
            window = padded[i:i+kernel_size, j:j+kernel_size]
            rel[i, j] = elev[i, j] - np.mean(window)

    return rel


def classify_terrain(elev, slope, rel):

    terrain = np.empty(elev.shape, dtype=int)

    terrain[(slope < 2) & (rel < -2)] = 2   # bog
    terrain[(slope > 6)] = 3               # ridge
    terrain[(elev < 1)] = 5                # water
    terrain[(terrain == 0)] = 1            # moorland

    return terrain


def main():

    print("Loading merged DEM...")

    elev = load_srtm(DEM_PATH)

    print("Computing slope...")

    slope = slope_degrees(elev)

    print("Computing relative elevation...")

    rel_elev = relative_elevation(elev)

    print("Classifying terrain...")

    terrain = classify_terrain(elev, slope, rel_elev)

    print("Resampling DEM to 1 km grid...")

    scale_factor = int(1000 / 30)

    rows = terrain.shape[0] // scale_factor * scale_factor
    cols = terrain.shape[1] // scale_factor * scale_factor

    terrain_trimmed = terrain[:rows, :cols]

    terrain_1km = terrain_trimmed.reshape(
        rows // scale_factor,
        scale_factor,
        cols // scale_factor,
        scale_factor
    ).mean(axis=(1, 3))

    OUTPUT_DIR = os.path.join(BASE_DIR, "output")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    csv_path = os.path.join(OUTPUT_DIR, "terrain_patch_map_v2.csv")

    np.savetxt(csv_path, terrain_1km, delimiter=",", fmt="%d")

    print("Saved terrain grid to:", csv_path)
    print("Falklands terrain pipeline complete.")


if __name__ == "__main__":
    main()