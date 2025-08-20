# histomap

**Napari dock widget to overlay tile polygons and table annotations from `SpatialData` onto an H&E image, and to interactively select cells in a 2D embedding (e.g., UMAP in `AnnData.obsm`) and visualize the selected regions on the H&E.**

- **Overlay mode**: color polygons on the H&E by an `AnnData.obs` column (categorical or numeric) from `SpatialData.tables[<name>]`.
- **UMAP-lasso mode**: open a 2D embedding from `AnnData.obsm` (e.g., `X_umap`), lasso points, and preview the corresponding tile polygons on the H&E; optionally save the selection back to `obs`.

---

## Installation

```bash
# Recommended: use a fresh environment
conda create --name histomap python=3.11 -y
conda activate histomap

# If published on PyPI:
pip install histomap

# If installing from source in this repo:
# pip install -e .
```

### Runtime dependencies (installed automatically if from PyPI)
- napari, PyQt5, magicgui
- geopandas, shapely
- anndata, matplotlib, spatialdata  
- (Optional, for robust SVS reading) `openslide-python`, `napari-openslide`

> **Windows notes**  
> - If `geopandas`/`shapely` wheels fail, upgrade pip (`pip install -U pip`) and try again.  
> - For OpenSlide, install the prebuilt binaries or use `conda install -c conda-forge openslide openslide-python` in the same environment.

---

## Quick start

```python
import histomap as hm
```

### Method 1 — Use a `SpatialData` object

```python
import spatialdata as sd
import histomap as hm

sda = sd.read_zarr("/path/to/spatialdata.zarr")

# Preferred: pass the H&E path explicitly (best on Windows)
viewer = hm.histomap(
    sda,
    wsi_path="/path/to/HE_image.svs",   # alias: imagePath="/path/to/HE_image.svs"
    # mpp=0.263049,                     # µm/px (optional; if tiles are in microns, scale=1/mpp is auto-applied)
)

# If you omit wsi_path, histomap will try to parse a path from str(sda).
# If no path is found, you’ll see a dialog asking you to pass wsi_path explicitly.
```

**Typical workflow in the UI**
1. Click **Open WSI in Viewer** (if not already opened).
2. Choose a **Table** (from `sda.tables`), **Data axis** (`obs` or `obsm`), and a column/key.
3. - For `obs`: click **Render Overlay** to color polygons on the H&E.  
   - For `obsm` (e.g., `X_umap`): click **Open UMAP + Lasso**, lasso points, and inspect the green **Lasso preview** on the H&E.
4. Optionally enter a **Layer name** and **obs column**, then click **Save selection** to write labels into `AnnData.obs` and add a persistent overlay layer.

### Method 2 — Use with **lazyslide/wsidata**

```python
import lazyslide as zs
from wsidata import open_wsi
import histomap as hm

wsi = open_wsi("/path/to/HE_image.svs")

# Assuming tiling & feature extraction are already done, e.g.:
# zs.pp.tile_tissues(wsi, tile_px=256, mpp=0.5)
# zs.tl.feature_extraction(wsi, model='chief')

# Launch viewer and overlay tiles/annotations stored in wsi.tables / wsi.shapes
viewer = hm.histomap(wsi)
```

---

## Parameters (entry point)

```python
viewer = hm.histomap(
    sda_or_wsi,                        # SpatialData or compatible WSIData
    *,
    wsi_path=None,                     # str | Path | None; preferred image to open (alias: imagePath)
    mpp=None,                          # float | None; µm/px. If provided and no explicit scale, applies scale=(1/mpp, 1/mpp)
    global_to_pixel_scale=None,        # (sx, sy) override for polygon transform
    global_to_pixel_translate=None,    # (tx, ty) override
    theme="dark",
    canvas_bg="white",
)
```

**Precedence**  
- If `global_to_pixel_scale` is provided, it overrides `mpp`.  
- If `wsi_path` is provided, it overrides any path parsed from `SpatialData`.  
- If neither `wsi_path` nor a parsable path exists, histomap shows a dialog explaining how to pass `wsi_path`.

---

## Data assumptions

- `sda.shapes["tiles"]` is a `GeoDataFrame` with polygons; its **index** contains tile IDs.  
- `sda.tables[<name>]` is an `AnnData` where `obs_names` match the tile IDs (string-matched; dtype mismatches are handled).  
- For UMAP-lasso, `AnnData.obsm[<key>]` contains an `(n_cells, 2+)` embedding (e.g., `X_umap`).

---

## Tips & alignment

- **Tiles already in pixels?** Don’t pass `mpp`. Use **Calibrate (fit tiles)** if needed.  
- **Tiles in microns?** Pass `mpp=<µm/px>` and click **Auto-align (use MPP)** (or rely on the automatic scale if you didn’t override with `global_to_pixel_scale`).  
- The overlay layers inherit the image layer’s **affine**, so they remain aligned across pyramid levels.

---

## Saving lasso selections (what gets written)

When you click **Save selection**:
- The chosen `obs` column is created/normalized as **plain Python strings (`dtype=object`) with no missing values**.  
- Only **selected rows** receive the provided label (string). Non-selected rows remain unchanged (empty string by default).  
- A persistent overlay layer is added with the saved selection (the transient **Lasso preview** is removed).

> **Why object strings?**  
> Writing pandas’ nullable string dtype (`dtype="string"`) to Zarr requires opting in (`anndata.settings.allow_write_nullable_strings=True`). Using plain object strings avoids that requirement and is maximally portable.

---

## Troubleshooting

### ❗️“boolean value of NA is ambiguous” during `wsi.write()` / `SpatialData.write()`
You likely have `pd.NA` or mixed types in `AnnData.obs`. Ensure **no NA** in string-like columns and that they are **object strings**.

### ❗️“allow_write_nullable_strings is False”
Either set:
```python
import anndata as ad
ad.settings.allow_write_nullable_strings = True
```
or convert to **object strings**.

### ❗️Cannot overwrite/move files on Windows after closing the viewer
Clear layers before saving: `viewer.layers.clear()` and run garbage collection.

### ❗️No H&E appears and you see “H&E Image Missing”
Pass the image explicitly:
```python
viewer = hm.histomap(sda, wsi_path="/absolute/path/to/HnE.svs")
```

---

## FAQ

**Q: Do I need `openslide`?**  
A: Only if you’re opening `.svs`/WSI formats through Napari.

**Q: Can I use a custom image and MPP without modifying the dock UI?**  
A: Yes—pass `wsi_path=...` and `mpp=...` to `hm.histomap(...)`.

---
