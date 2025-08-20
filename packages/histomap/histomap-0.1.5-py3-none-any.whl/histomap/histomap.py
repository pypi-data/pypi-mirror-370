"""
Napari dock widget for overlaying SpatialData tile polygons on H&E and for UMAP‑lasso selection.

Requirements (install as needed):
    pip install napari PyQt5 magicgui geopandas shapely anndata matplotlib spatialdata
Optional (for robust SVS loading):
    pip install openslide-python napari-openslide

Usage:
    from napari_spatialdata_overlay import histomap
    viewer = histomap(
        spatialdata_obj,
        # If shapes are in microns but image is in pixels, scale by 1/MPP
        # (Do NOT pass this if your tiles are already in base pixels.)
        # global_to_pixel_scale=(1/0.263049, 1/0.263049),
        # global_to_pixel_translate=(0.0, 0.0),
        # UI theme is fixed to 'dark'; canvas background is forced to white.
    )

Notes:
        spatialdata_obj,
        # If shapes are in microns but image is in pixels, scale by 1/MPP
        # (Do NOT pass this if your tiles are already in base pixels.)
        # global_to_pixel_scale=(1/0.263049, 1/0.263049),
        # global_to_pixel_translate=(0.0, 0.0),
    )

Notes:
- Assumes `AnnData.obs_names` correspond to the index of `sda.shapes['tiles']` (no column join).
- Robust ID matching: we coerce both sides (obs_names and tiles.index) to strings before intersecting.
- Full-resolution WSI is opened via napari’s reader stack (e.g., napari-openslide).
- Overlays are pyramid-aware by copying the image layer's affine transform.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List, Dict, Tuple

import numpy as np
import pandas as pd
from qtpy import QtWidgets
from qtpy.QtCore import Qt

# Matplotlib embedded in Qt
import matplotlib
matplotlib.use("Qt5Agg")  # ensure Qt5 backend for embedded canvas
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.widgets import LassoSelector
from matplotlib.path import Path as MplPath
import colorsys

import napari
from napari.layers import Image as NapariImage

try:
    import geopandas as gpd
except Exception:
    gpd = None

try:
    from spatialdata import SpatialData
except Exception:
    SpatialData = object  # type: ignore

try:
    import anndata as ad
except Exception:
    ad = None  # type: ignore


# -------------------------- helpers -------------------------- #

def get_wsi_path(obj) -> Optional[str]:
    """Parse the WSI path from SpatialData.__str__ without regex (robust to escaping)."""
    s = str(obj)
    for line in s.splitlines():
        line = line.strip()
        if line.startswith("WSI:"):
            return line.split("WSI:", 1)[1].strip()
    return None


def parse_mpp_from_str(obj) -> Optional[float]:
    """Try to extract MPP using a simple regex-like parse; returns None if absent."""
    s = str(obj)
    for line in s.splitlines():
        line = line.strip()
        if line.startswith("Pixel physical size:"):
            rest = line.split("Pixel physical size:", 1)[1].strip()
            token = rest.split()[0] if rest else None
            try:
                return float(token)
            except Exception:
                return None
    return None


def is_categorical(series: pd.Series) -> bool:
    if pd.api.types.is_categorical_dtype(series) or series.dtype == object:
        # treat low-cardinality object as categorical
        return series.nunique(dropna=True) <= max(32, int(len(series) * 0.05))
    return pd.api.types.is_bool_dtype(series)


# ---------- color helpers ---------- #

def _relative_luminance(rgb):
    r, g, b = rgb
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _ensure_contrast_on_white(rgb):
    # If too light on white, darken slightly
    try:
        r, g, b = rgb
    except Exception:
        r, g, b, *_ = rgb
    if _relative_luminance((r, g, b)) > 0.82:
        factor = 0.85
        return (r * factor, g * factor, b * factor)
    return (r, g, b)


def _hex_to_rgb01(hex_str: str):
    hex_str = hex_str.lstrip('#')
    return tuple(int(hex_str[i:i+2], 16) / 255.0 for i in (0, 2, 4))


def _okabe_ito_no_black_no_white():
    # Okabe–Ito palette (colorblind-friendly) minus black/white
    hexes = [
        "#E69F00",  # orange
        "#56B4E9",  # sky blue
        "#009E73",  # bluish green
        "#F0E442",  # yellow (will be slightly darkened)
        "#0072B2",  # blue
        "#D55E00",  # vermillion
        "#CC79A7",  # reddish purple
    ]
    cols = [_hex_to_rgb01(hx) for hx in hexes]
    cols = [_ensure_contrast_on_white(c) for c in cols]
    return cols

@dataclass
class SelectionState:
    points: Optional[np.ndarray] = None  # (n_sel,) indices in table order
    name: str = ""
    obs_column: str = ""


# -------------------------- UMAP Lasso Dock -------------------------- #
class UmapLassoDock(QtWidgets.QWidget):
    """A Qt dock embedding a matplotlib scatter with a lasso selector."""

    def __init__(self, embedding: np.ndarray, index: pd.Index, on_selection):
        super().__init__()
        self.embedding = embedding
        self.index = index
        self.on_selection = on_selection
        self._init_ui()

    def _init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        self.fig = Figure(figsize=(5, 4), tight_layout=True)
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)

        ax = self.fig.add_subplot(111)
        self.ax = ax
        self.scatter = ax.scatter(self.embedding[:, 0], self.embedding[:, 1], s=6, linewidths=0)
        ax.set_xlabel("UMAP1")
        ax.set_ylabel("UMAP2")
        ax.set_title("Lasso to select; click outside to clear")

        self.lasso = LassoSelector(self.ax, onselect=self._on_lasso)
        self.canvas.mpl_connect("button_press_event", self._on_click)

    def _on_click(self, event):
        # Clicking outside axes clears selection
        if event.inaxes != self.ax:
            self._highlight([])
            self.on_selection([])

    def _on_lasso(self, verts: List[Tuple[float, float]]):
        path = MplPath(verts)
        inds = np.nonzero(path.contains_points(self.embedding))[0]
        self._highlight(inds)
        self.on_selection(list(inds))

    def _highlight(self, inds: List[int]):
        c = np.zeros((len(self.embedding),), dtype=float)
        c[:] = 0.25
        if len(inds):
            c[np.asarray(inds)] = 1.0
        self.scatter.set_array(c)
        self.scatter.set_cmap("Greys")
        self.scatter.set_clim(0, 1)
        self.canvas.draw_idle()


# -------------------------- Main Dock -------------------------- #
class SpatialOverlayDock(QtWidgets.QWidget):
    """Dock widget controlling overlays from SpatialData on a WSI in napari."""

    def __init__(self, viewer: napari.Viewer, sda: SpatialData,
                 global_to_pixel_scale: Tuple[float, float] | None = None,
                 global_to_pixel_translate: Tuple[float, float] | None = None):
        super().__init__()
        if gpd is None:
            raise ImportError("geopandas is required for polygon overlays. pip install geopandas")
        self.viewer = viewer
        self.sda = sda
        self.global_to_pixel_scale = global_to_pixel_scale
        self.global_to_pixel_translate = global_to_pixel_translate

        # State
        self.current_table_key: Optional[str] = None
        self.current_table: Optional[ad.AnnData] = None
        self.tiles: gpd.GeoDataFrame = self.sda.shapes["tiles"]  # expects index matching obs_names
        self.selection_state = SelectionState()

        # Parse MPP from SpatialData string for optional auto-scaling
        self._mpp = parse_mpp_from_str(self.sda)

        # Build UI
        self._build_ui()

    # ---------------- UI ---------------- #
    def _build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        # Header: WSI path and Open button
        wsi_path = get_wsi_path(self.sda)
        header = QtWidgets.QHBoxLayout()
        self.wsi_label = QtWidgets.QLabel(f"WSI: {wsi_path if wsi_path else 'N/A'}")
        self.wsi_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.open_btn = QtWidgets.QPushButton("Open WSI in Viewer")
        self.open_btn.clicked.connect(lambda: self._open_wsi(wsi_path))
        header.addWidget(self.wsi_label)
        header.addStretch(1)
        header.addWidget(self.open_btn)
        layout.addLayout(header)

        # Alignment helpers
        align_row = QtWidgets.QHBoxLayout()
        self.auto_align_btn = QtWidgets.QPushButton("Auto-align (use MPP)")
        self.auto_align_btn.setToolTip("If MPP is missing, you'll be prompted.")
        self.auto_align_btn.clicked.connect(self._auto_align_from_mpp)
        self.calibrate_btn = QtWidgets.QPushButton("Calibrate (fit tiles)")
        self.calibrate_btn.setToolTip("Estimate scale/translation from image & tile bounds")
        self.calibrate_btn.clicked.connect(self._calibrate_fit_to_image)
        self.clear_align_btn = QtWidgets.QPushButton("Clear align")
        self.clear_align_btn.clicked.connect(self._clear_alignment)
        align_row.addWidget(self.auto_align_btn)
        align_row.addWidget(self.calibrate_btn)
        align_row.addWidget(self.clear_align_btn)
        layout.addLayout(align_row)

        layout.addSpacing(6)

        # Table chooser
        self.table_combo = QtWidgets.QComboBox()
        table_keys = list(self.sda.tables.keys())
        self.table_combo.addItems(table_keys)
        self.table_combo.currentTextChanged.connect(self._on_table_changed)
        layout.addWidget(QtWidgets.QLabel("Table:"))
        layout.addWidget(self.table_combo)

        # obs/obsm chooser
        self.axis_combo = QtWidgets.QComboBox()
        self.axis_combo.addItems(["obs", "obsm"]) 
        self.axis_combo.currentTextChanged.connect(self._on_axis_changed)
        layout.addWidget(QtWidgets.QLabel("Data axis:"))
        layout.addWidget(self.axis_combo)

        # Column / key chooser (populated dynamically)
        self.column_combo = QtWidgets.QComboBox()
        layout.addWidget(QtWidgets.QLabel("Column / embedding key:"))
        layout.addWidget(self.column_combo)

        # Buttons for rendering / lasso
        btn_row = QtWidgets.QHBoxLayout()
        self.render_btn = QtWidgets.QPushButton("Render Overlay")
        self.render_btn.clicked.connect(self._on_render)
        self.lasso_btn = QtWidgets.QPushButton("Open UMAP + Lasso")
        self.lasso_btn.clicked.connect(self._on_open_lasso)
        btn_row.addWidget(self.render_btn)
        btn_row.addWidget(self.lasso_btn)
        layout.addLayout(btn_row)

        # Save selection controls
        save_group = QtWidgets.QGroupBox("Save current lasso selection to obs")
        save_layout = QtWidgets.QFormLayout()
        self.sel_name_edit = QtWidgets.QLineEdit()
        self.obs_col_edit = QtWidgets.QLineEdit()
        self.save_btn = QtWidgets.QPushButton("Save selection")
        self.save_btn.clicked.connect(self._on_save_selection)
        save_layout.addRow("Layer name:", self.sel_name_edit)
        save_layout.addRow("obs column:", self.obs_col_edit)
        save_layout.addRow(self.save_btn)
        save_group.setLayout(save_layout)
        layout.addWidget(save_group)

        layout.addStretch(1)

        # Initialize
        if self.table_combo.count():
            self._on_table_changed(self.table_combo.currentText())

    # ---------------- Actions ---------------- #
    def _open_wsi(self, wsi_path: Optional[str]):
        import os
        if not wsi_path:
            QtWidgets.QMessageBox.warning(self, "No Path", "WSI path not found in SpatialData text.")
            return
        if not os.path.exists(wsi_path):
            QtWidgets.QMessageBox.critical(self, "Path missing", f"WSI not found:{wsi_path}")
            return
        try:
            self.viewer.open(wsi_path)  # relies on available napari reader (e.g., openslide)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Open failed", f"Could not open WSI:{e}")

    def _on_table_changed(self, key: str):
        self.current_table_key = key
        self.current_table = self.sda.tables[key]
        self._populate_columns()

    def _on_axis_changed(self, axis: str):
        self._populate_columns()

    def _on_theme_changed(self, theme_name: str):
        """Switch napari UI theme (light=white background, dark=black)."""
        try:
            self.viewer.theme = theme_name
        except Exception:
            # older napari versions may not support theme assignment; ignore
            pass

    def _on_bg_changed(self, color_name: str):
        """Set only the canvas/view area background, not the whole UI."""
        self._set_canvas_background(color_name)

    def _set_canvas_background(self, color: str):
        # Try multiple access paths for robustness across napari versions
        try:
            qtv = getattr(self.viewer.window, 'qt_viewer', None) or getattr(self.viewer.window, '_qt_viewer', None)
            if qtv is not None and hasattr(qtv, 'canvas') and qtv.canvas is not None:
                try:
                    qtv.canvas.bgcolor = color
                    return
                except Exception:
                    try:
                        qtv.canvas.set_background_color(color)
                        return
                    except Exception:
                        pass
        except Exception:
            pass

    def _populate_columns(self):
        self.column_combo.clear()
        if self.current_table is None:
            return
        axis = self.axis_combo.currentText()
        if axis == "obs":
            cols = list(self.current_table.obs.columns)
        else:
            cols = list(self.current_table.obsm.keys())
        self.column_combo.addItems(cols)

    def _on_render(self):
        if self.current_table is None:
            QtWidgets.QMessageBox.warning(self, "No table", "Select a table first.")
            return
        axis = self.axis_combo.currentText()
        key = (self.column_combo.currentText() or "").strip()
        if not key:
            QtWidgets.QMessageBox.warning(self, "No column/key", f"Select a column in {axis}.")
            return
        if axis == "obs":
            if key not in self.current_table.obs:
                QtWidgets.QMessageBox.warning(self, "Missing column", f"obs['{key}'] not found in the selected table.")
                return
            self._render_obs_column(key)
        else:
            QtWidgets.QMessageBox.information(
                self, "Embedding", "Rendering from obsm is handled via the UMAP + Lasso panel."
            )

    def _on_open_lasso(self):
        if self.current_table is None:
            return
        if self.axis_combo.currentText() != "obsm":
            QtWidgets.QMessageBox.information(self, "Select obsm", "Switch Data axis to 'obsm' and choose an embedding key (e.g., X_umap).")
            return
        key = self.column_combo.currentText()
        if key == "":
            QtWidgets.QMessageBox.warning(self, "No key", "Choose an obsm key (e.g., X_umap) first.")
            return
        if key not in self.current_table.obsm:
            QtWidgets.QMessageBox.warning(self, "Missing", f"obsm['{key}'] not found.")
            return
        emb = np.asarray(self.current_table.obsm[key])
        if emb.ndim != 2 or emb.shape[1] < 2:
            QtWidgets.QMessageBox.warning(self, "Invalid", f"obsm['{key}'] must be (n,2+) for lasso.")
            return
        emb2 = emb[:, :2]

        # Create/raise a docked window with the lasso scatter
        self._lasso_dialog = QtWidgets.QDialog(self)
        self._lasso_dialog.setWindowTitle(f"Lasso selection: {self.current_table_key}:{key}")
        layout = QtWidgets.QVBoxLayout(self._lasso_dialog)
        dock = UmapLassoDock(emb2, self.current_table.obs_names, self._apply_lasso_selection)
        layout.addWidget(dock)
        note = QtWidgets.QLabel("After lasso, a green 'Lasso preview' overlay should appear on the WSI. If you don't see it, try 'Auto-align (use MPP)' or 'Calibrate (fit tiles)'.")
        note.setWordWrap(True)
        layout.addWidget(note)
        self._lasso_dialog.resize(680, 560)
        self._lasso_dialog.show()

    def _apply_lasso_selection(self, sel_inds: List[int]):
        # Record selection in state and immediately overlay as a layer
        if self.current_table is None:
            return
        self.selection_state.points = np.asarray(sel_inds, dtype=int) if len(sel_inds) else None
        self._overlay_selection_preview()

    # ---------------- Matching & overlay logic ---------------- #
    def _match_obs_names_to_tiles(self, names: pd.Index) -> pd.Index:
        """Coerce obs_names and tiles.index to strings and return the matching tile labels."""
        tiles_idx = pd.Index(self.tiles.index)
        tiles_str = tiles_idx.astype(str)
        names_str = pd.Index(names).astype(str)
        common = names_str.intersection(tiles_str)
        if len(common) == 0:
            return pd.Index([], dtype=tiles_idx.dtype)
        mask = tiles_str.isin(common)
        return tiles_idx[mask]

    def _tiles_to_napari(self, idx_like: pd.Index) -> Tuple[List[np.ndarray], Dict]:
        """Convert selected tile polygons to napari Shapes data after safe matching."""
        avail = self._match_obs_names_to_tiles(pd.Index(idx_like))
        if len(avail) == 0:
            return [], {}
        sub = self.tiles.loc[avail]
        polys: List[np.ndarray] = []
        for geom in sub.geometry:
            if geom is None or geom.is_empty:
                continue
            geoms = [geom] if geom.geom_type == "Polygon" else list(geom.geoms)
            for g in geoms:
                coords = np.asarray(g.exterior.coords, float)  # (x, y)
                # Optional global->pixel transform
                if self.global_to_pixel_scale is not None:
                    sx, sy = self.global_to_pixel_scale
                    coords = coords * np.array([sx, sy], float)
                if self.global_to_pixel_translate is not None:
                    tx, ty = self.global_to_pixel_translate
                    coords = coords + np.array([tx, ty], float)
                polys.append(coords[:, [1, 0]])  # (row, col)
        return polys, {}

    def _get_categorical_palette(self, n: int):
        """Return n high-contrast colors suitable for a white canvas.
        Strategy:
          - n <= 8: Okabe–Ito (colorblind-friendly) minus black; yellow darkened
          - 9 <= n <= 12: matplotlib 'tab10' then a few from 'Dark2'
          - 13 <= n <= 20: 'tab20' with even-then-odd index ordering for separation
          - n > 20: evenly spaced HSV around the color wheel, tuned for white background
        """
        out = []
        if n <= 8:
            base = _okabe_ito_no_black_no_white()
            out = base[:n]
        elif n <= 12:
            tab10 = matplotlib.colormaps.get("tab10")
            out = [tuple(tab10(i)[:3]) for i in range(min(10, n))]
            if n > 10:
                dark2 = matplotlib.colormaps.get("Dark2")
                out += [tuple(dark2(i)[:3]) for i in range(n - 10)]
        elif n <= 20:
            tab20 = matplotlib.colormaps.get("tab20")
            order = list(range(0, 20, 2)) + list(range(1, 20, 2))
            out = [tuple(tab20(i)[:3]) for i in order[:n]]
        else:
            hs = np.linspace(0.0, 1.0, n, endpoint=False)
            for k, h in enumerate(hs):
                s = 0.85 if (k % 2 == 0) else 0.95
                v = 0.90
                r, g, b = colorsys.hsv_to_rgb(h, s, v)
                out.append((r, g, b))
        # improve contrast on white
        out = [_ensure_contrast_on_white(c) for c in out]
        return out

    def _overlay_selection_preview(self):
        # Remove previous preview layer if any
        for lyr in [lyr for lyr in self.viewer.layers if lyr.name == "Lasso preview"]:
            self.viewer.layers.remove(lyr)
        if self.selection_state.points is None or self.current_table is None:
            return
        selected_names = self.current_table.obs_names[self.selection_state.points]
        polys, _ = self._tiles_to_napari(selected_names)
        if not polys:
            tiles_idx = self.tiles.index
            msg = (
                "No polygons for current selection."
                f"Examples:first selected → {list(map(str, selected_names[:5]))}"
                f"first tiles.index → {list(map(str, tiles_idx[:5]))}"
                "Tips:• Ensure obs_names and tiles.index refer to the same IDs."
                " • If coordinates look off, try Auto-align (use MPP) or Calibrate (fit tiles)."
            )
            QtWidgets.QMessageBox.warning(self, "No overlay", msg)
            return
        img_layer = self._get_image_layer()
        layer = self.viewer.add_shapes(
            polys,
            shape_type="polygon",
            edge_width=0.6,
            edge_color="black",
            face_color="green",
            name="Lasso preview",
            affine=(img_layer.affine if img_layer is not None else None),
            blending="translucent",
            opacity=0.4,
        )
        self.viewer.layers.selection.active = layer

    def _render_obs_column(self, col: str):
        tbl = self.current_table
        if tbl is None:
            return
        s = tbl.obs[col]

        # --- Robust alignment: match by stringified IDs, ignore non-overlapping tiles ---
        tiles_idx = pd.Index(self.tiles.index)
        tiles_str = tiles_idx.astype(str)
        obs_names_str = pd.Index(tbl.obs_names).astype(str)

        # map obs name (string) -> value
        obs_map = pd.Series(s.values, index=obs_names_str)
        matched_mask = tiles_str.isin(obs_map.index)
        if not matched_mask.any():
            QtWidgets.QMessageBox.information(
                self,
                "No overlap",
                "No obs_names matched tiles.index. Ensure they refer to the same tile IDs.",
            )
            return

        matched_tiles = tiles_idx[matched_mask]
        vals = obs_map.reindex(tiles_str[matched_mask])  # string index in tiles order
        vals.index = matched_tiles  # restore real tile index labels

        img_layer = self._get_image_layer()

        # If everything is NA after matching, nothing to draw
        if vals.dropna().empty:
            QtWidgets.QMessageBox.information(
                self,
                "No data",
                f"obs['{col}'] has no non-null values on matched tiles.",
            )
            return

        # ---- Categorical (strings/low-cardinality) ----
        if is_categorical(vals):
            cats = pd.Categorical(vals.astype("category")).categories
            if len(cats) == 0:
                QtWidgets.QMessageBox.information(self, "No classes", f"No non-null classes in obs['{col}'].")
                return
            palette = self._get_categorical_palette(len(cats))
            any_drawn = False
            for i, cat in enumerate(cats):
                idx = vals.index[(vals == cat).fillna(False)]
                if len(idx) == 0:
                    continue
                polys, _ = self._tiles_to_napari(idx)
                if not polys:
                    continue
                color = np.array(palette[i % len(palette)])
                face_color = np.tile(color, (len(polys), 1))
                layer = self.viewer.add_shapes(
                    polys,
                    shape_type="polygon",
                    edge_width=0.5,
                    edge_color="white",
                    face_color=face_color,
                    name=self._unique_layer_name(str(cat)),
                    affine=(img_layer.affine if img_layer is not None else None),
                    blending="translucent",
                    opacity=0.4,
                )
                self.viewer.layers.selection.active = layer
                any_drawn = True
            if not any_drawn:
                QtWidgets.QMessageBox.information(self, "Nothing to draw", "No matching polygons for the chosen column.")
            return

        # ---- Numeric ----
        numeric_vals = pd.to_numeric(vals, errors="coerce")
        if numeric_vals.dropna().empty:
            QtWidgets.QMessageBox.warning(self, "No data", f"All values in obs['{col}'] are NaN after matching.")
            return
        vmin = np.nanpercentile(numeric_vals, 2)
        vmax = np.nanpercentile(numeric_vals, 98)
        if not np.isfinite(vmin) or not np.isfinite(vmax) or vmin == vmax:
            vmin, vmax = np.nanmin(numeric_vals.values), np.nanmax(numeric_vals.values)
        norm = matplotlib.colors.Normalize(vmin=vmin, vmax=vmax)
        cmap = matplotlib.colormaps.get("viridis")

        idx_all = numeric_vals.index
        poly_data, _ = self._tiles_to_napari(idx_all)
        if not poly_data:
            QtWidgets.QMessageBox.warning(self, "No polygons", "Tiles not found or alignment issue.")
            return
        colors = []
        for v in numeric_vals.reindex(idx_all).values:
            if np.isnan(v):
                colors.append((0, 0, 0, 0))
            else:
                colors.append(cmap(norm(v)))
        colors = np.array(colors)
        if len(colors) != len(poly_data):
            colors = np.tile(np.array(cmap(0.5))[:3], (len(poly_data), 1))
        layer = self.viewer.add_shapes(
            poly_data,
            shape_type="polygon",
            edge_width=0.2,
            edge_color="white",
            face_color=colors,
            name=self._unique_layer_name(str(col)),
            affine=(img_layer.affine if img_layer is not None else None),
            blending="translucent",
            opacity=0.4,
        )
        self.viewer.layers.selection.active = layer
    
    def _on_save_selection(self):
        """Save current lasso as STRING labels in an obs column."""
        if self.selection_state.points is None or self.current_table is None:
            QtWidgets.QMessageBox.information(self, "Nothing to save", "No active lasso selection.")
            return
    
        name = self.sel_name_edit.text().strip() or "selection"
        obs_col = self.obs_col_edit.text().strip() or name
        adata = self.current_table
    
        # Ensure target column exists as PLAIN-STRING (object) dtype, with no NA
        if obs_col not in adata.obs:
            adata.obs[obs_col] = pd.Series("", index=adata.obs_names, dtype=object)
        else:
            s = adata.obs[obs_col]
            # nullable string or categorical → object; other non-object → object
            if pd.api.types.is_categorical_dtype(s) or getattr(s.dtype, "name", "") == "string" or s.dtype != object:
                s = s.astype(object)
            # replace missing with empty string
            s = s.where(~pd.isna(s), "")
            adata.obs[obs_col] = s
    
        # Indices to update (selected tiles)
        sel_names = adata.obs_names[self.selection_state.points]
        # Write the provided name to selected rows only
        adata.obs.loc[sel_names, obs_col] = str(name)
    
        # Add a permanent layer with this selection and clear preview
        polys, _ = self._tiles_to_napari(sel_names)
        if polys:
            img_layer = self._get_image_layer()
            layer = self.viewer.add_shapes(
                polys,
                shape_type="polygon",
                edge_width=0.6,
                edge_color="black",
                face_color="orange",
                name=name,
                affine=(img_layer.affine if img_layer is not None else None),
                blending="translucent",
                opacity=0.4,
            )
            self.viewer.layers.selection.active = layer
    
        # Clear preview layer
        for lyr in [lyr for lyr in self.viewer.layers if lyr.name == "Lasso preview"]:
            self.viewer.layers.remove(lyr)
    
        # Refresh UI to include/select the saved column
        self.axis_combo.setCurrentText("obs")
        self._populate_columns()
        i = self.column_combo.findText(obs_col)
        if i >= 0:
            self.column_combo.setCurrentIndex(i)
    
        QtWidgets.QMessageBox.information(
            self,
            "Saved",
            f"Saved {len(sel_names)} tiles to obs['{obs_col}'] as '{name}'. Existing values outside the selection were left unchanged.",
        )


    # ---- alignment helpers ----
    def _get_image_layer(self) -> Optional[NapariImage]:
        # Return the first Image layer (assumed to be the WSI)
        for lyr in self.viewer.layers:
            if isinstance(lyr, NapariImage):
                return lyr
        return None

    def _unique_layer_name(self, base: str) -> str:
        """Return a name not already used in the viewer by appending (2), (3), ..."""
        existing = {lyr.name for lyr in self.viewer.layers}
        if base not in existing:
            return base
        k = 2
        while f"{base} ({k})" in existing:
            k += 1
        return f"{base} ({k})"

    def _calibrate_fit_to_image(self):
        """Estimate scale and translation so tile bounds fit the current image layer."""
        img = self._get_image_layer()
        if img is None:
            QtWidgets.QMessageBox.warning(self, "No image", "Open a WSI image layer first.")
            return
        # image base dimensions (pixels)
        if isinstance(img.data, list):
            H, W = img.data[0].shape[-2:]
        else:
            H, W = img.data.shape[-2:]
        minx, miny, maxx, maxy = self.tiles.geometry.total_bounds
        span_x = maxx - minx
        span_y = maxy - miny
        if span_x <= 0 or span_y <= 0:
            QtWidgets.QMessageBox.warning(self, "Invalid tiles", "Tile bounds are degenerate.")
            return
        sx = W / span_x
        sy = H / span_y
        if abs(sx - sy) / max(sx, sy) < 0.05:
            s = (sx + sy) / 2.0
            self.global_to_pixel_scale = (s, s)
        else:
            self.global_to_pixel_scale = (sx, sy)
        tx = -minx * self.global_to_pixel_scale[0]
        ty = -miny * self.global_to_pixel_scale[1]
        self.global_to_pixel_translate = (tx, ty)
        QtWidgets.QMessageBox.information(self, "Calibrated", f"Scale≈({self.global_to_pixel_scale[0]:.3f}, {self.global_to_pixel_scale[1]:.3f}),Translate≈({tx:.1f}, {ty:.1f})")
        self._overlay_selection_preview()

    def _auto_align_from_mpp(self):
        """If shapes are in microns and image is in pixels, scale by 1/MPP. If MPP missing, prompt."""
        img = self._get_image_layer()
        if img is None:
            QtWidgets.QMessageBox.warning(self, "No image", "Open a WSI image layer first.")
            return
        # derive image size
        if isinstance(img.data, list):
            H, W = img.data[0].shape[-2:]
        else:
            H, W = img.data.shape[-2:]
        minx, miny, maxx, maxy = self.tiles.geometry.total_bounds
        span_x, span_y = maxx - minx, maxy - miny

        mpp = self._mpp
        if mpp is None:
            val, ok = QtWidgets.QInputDialog.getDouble(self, "Set MPP", "Enter pixel size (µm/px):", 0.5, 0.01, 10.0, 6)
            if not ok:
                return
            mpp = float(val)
            self._mpp = mpp

        # Heuristic: if tiles already span the image roughly, they're likely in pixels already
        already_pixels = (0.5 <= span_x / W <= 2.0) and (0.5 <= span_y / H <= 2.0)
        if already_pixels:
            QtWidgets.QMessageBox.information(self, "No scaling applied", "Tiles appear to be in pixel units already; skipping 1/MPP scaling.")
            self.global_to_pixel_scale = None
            self.global_to_pixel_translate = None
            self._overlay_selection_preview()
            return

        s = 1.0 / float(mpp)
        self.global_to_pixel_scale = (s, s)
        self.global_to_pixel_translate = None
        QtWidgets.QMessageBox.information(self, "Alignment applied", f"Scaled tiles by 1/MPP = {s:.3f}.")
        self._overlay_selection_preview()

    def _clear_alignment(self):
        self.global_to_pixel_scale = None
        self.global_to_pixel_translate = None
        QtWidgets.QMessageBox.information(self, "Alignment cleared", "Scale/translate reset.")
        self._overlay_selection_preview()


# -------------------------- Public API -------------------------- #

def histomap(sda: SpatialData,
                  *,
                  global_to_pixel_scale: Tuple[float, float] | None = None,
                  global_to_pixel_translate: Tuple[float, float] | None = None,
                  theme: str = "dark",
                  canvas_bg: str = "white",
                  imagePath: Optional[str] = None,   # NEW: custom H&E path
                  mpp: Optional[float] = None,      # NEW: µm/px (used only if scale not provided)
                  ) -> napari.Viewer:
    """Launch napari with a dock for SpatialData overlays."""
    viewer = napari.Viewer()
    # hardcode UI theme to dark
    try:
        viewer.theme = "dark"
    except Exception:
        pass

    # If caller provided MPP and no explicit scale, compute scale = 1/MPP (tiles in microns → pixels)
    if global_to_pixel_scale is None and mpp is not None:
        try:
            s = 1.0 / float(mpp)
            global_to_pixel_scale = (s, s)
        except Exception:
            pass  # ignore bad mpp, fall back to None    
    
    # Create dock 
    dock = SpatialOverlayDock(viewer, sda,
                              global_to_pixel_scale=global_to_pixel_scale,
                              global_to_pixel_translate=global_to_pixel_translate)
    
    # If you keep _mpp on the dock, set it for later 'Auto-align (use MPP)' use
    try:
        dock._mpp = float(mpp) if mpp is not None else dock._mpp
    except Exception:
        pass
    
    viewer.window.add_dock_widget(dock, name="Spatial overlays", area="right")

    # hardcode canvas (view area) background to white
    try:
        dock._set_canvas_background("white")
    except Exception:
        pass

    # Resolve image path: prefer user-provided > parsed
    import os
    path = imagePath or get_wsi_path(sda)

    if path and os.path.exists(path):
        try:
            viewer.open(path)
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                None,
                "Failed to open H&E image",
                f"Could not open image at '{path}': {e}"
            )
    else:
        QtWidgets.QMessageBox.warning(
            None,
            "H&E Image Missing",
            "No H&E image path found. Please pass it explicitly via:\n"
            "  histomap(sda, imagePath='/path/to/image.svs')"
        )

    return viewer

# Backwards-compatible alias
launch_viewer = histomap

if __name__ == "__main__":
    print("This module provides histomap(sda). Import and call from your analysis script.")
