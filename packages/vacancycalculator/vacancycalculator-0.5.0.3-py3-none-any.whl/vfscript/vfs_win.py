import sys
import io
import json
import contextlib
import traceback
from pathlib import Path
import shutil
import os

# Evita issues Wayland
os.environ["QT_QPA_PLATFORM"] = "xcb"

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFormLayout, QCheckBox,
    QDoubleSpinBox, QSpinBox, QLineEdit, QPushButton, QFileDialog,
    QMessageBox, QHBoxLayout, QPlainTextEdit, QVBoxLayout,
    QProgressBar, QSizePolicy, QComboBox, QTableWidget, QTableWidgetItem,
    QScrollArea, QLabel, QTabWidget, QListWidget, QListWidgetItem,
    QAbstractItemView
)
from pyvistaqt import QtInteractor
import pyvista as pv
import numpy as np
from ovito.io import import_file
from vfscript import vfs
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

GUI_ROOT = Path(__file__).resolve().parent

def runtime_params_path():
    cwd_params = Path.cwd() / "input_params.json"
    if cwd_params.exists():
        return cwd_params
    src_params = GUI_ROOT / "input_params.json"
    if src_params.exists():
        shutil.copy(src_params, cwd_params)
        return cwd_params
    return src_params

PARAMS_FILE = runtime_params_path()

def load_params():
    if PARAMS_FILE.exists():
        return json.loads(PARAMS_FILE.read_text())
    return {}

def save_params(params, target_path: Path = None):
    if target_path is None:
        target_path = Path.cwd() / "input_params.json"
    target_path.write_text(json.dumps(params, indent=4))
    return target_path

# ---------------- RENDER DUMP (3D + 2D) ----------------
def render_dump_to(plotter: QtInteractor, fig: plt.Figure, dump_path: str):
    pipeline = import_file(dump_path)
    data = pipeline.compute()

    M = np.asarray(data.cell.matrix, dtype=float)
    a1, a2, a3, origin = M[:, 0], M[:, 1], M[:, 2], M[:, 3]
    corners = [
        origin,
        origin + a1,
        origin + a2,
        origin + a3,
        origin + a1 + a2,
        origin + a1 + a3,
        origin + a2 + a3,
        origin + a1 + a2 + a3
    ]
    edges = [(0,1),(0,2),(0,3),(1,4),(1,5),(2,4),(2,6),(3,5),(3,6),(4,7),(5,7),(6,7)]

    pos_prop = data.particles.positions
    positions = pos_prop.array if hasattr(pos_prop, "array") else np.asarray(pos_prop, dtype=float)

    cluster_vals = None
    for name in ("Cluster","cluster","c_Cluster","c_cluster","ClusterID","cluster_id"):
        if name in data.particles:
            prop = data.particles[name]
            arr = prop.array if hasattr(prop, "array") else prop
            cluster_vals = np.asarray(arr).astype(int).reshape(-1)
            break

    cluster_idx = None
    unique_clusters = None
    if cluster_vals is not None and cluster_vals.shape[0] == positions.shape[0]:
        unique_clusters = np.unique(cluster_vals)
        map_idx = {val: i for i, val in enumerate(unique_clusters)}
        cluster_idx = np.vectorize(map_idx.get, otypes=[int])(cluster_vals)

    # 3D
    plotter.clear()
    for i, j in edges:
        plotter.add_mesh(pv.Line(corners[i], corners[j]), color="blue", line_width=2)

    if cluster_idx is not None:
        pts = pv.PolyData(positions)
        pts["cluster"] = cluster_idx
        plotter.add_mesh(pts, scalars="cluster", render_points_as_spheres=True,
                         point_size=8, cmap="tab20", show_scalar_bar=False)
    else:
        plotter.add_mesh(pv.PolyData(positions), color="black",
                         render_points_as_spheres=True, point_size=8)
    plotter.reset_camera()
    plotter.set_scale(1, 1, 1)

    # 2D
    fig.clf()
    ax = fig.add_subplot(111)
    for i, j in edges:
        x0, y0 = corners[i][0], corners[i][1]
        x1, y1 = corners[j][0], corners[j][1]
        ax.plot([x0, x1], [y0, y1], '-', linewidth=1)
    ax.scatter(positions[:, 0], positions[:, 1], s=10, c="k")
    ax.set_xlabel('X'); ax.set_ylabel('Y')
    ax.set_aspect('equal', 'box'); ax.grid(True, linewidth=0.3)
    fig.canvas.draw()

# ---------------- Widgets de viewers ----------------
class DumpViewerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        top = QWidget(); top_l = QHBoxLayout(top)
        self.path_edit = QLineEdit()
        self.btn_browse = QPushButton("Browse")
        self.btn_load = QPushButton("Load")
        top_l.addWidget(QLabel("File:"))
        top_l.addWidget(self.path_edit, 1)
        top_l.addWidget(self.btn_browse)
        top_l.addWidget(self.btn_load)

        center = QWidget(); center_l = QVBoxLayout(center)
        self.plotter = QtInteractor(center); center_l.addWidget(self.plotter)
        self.fig = plt.figure(figsize=(4, 4))
        self.canvas = FigureCanvas(self.fig); center_l.addWidget(self.canvas)

        root_l = QVBoxLayout(self)
        root_l.addWidget(top)
        root_l.addWidget(center, 1)

        self.btn_browse.clicked.connect(self._browse)
        self.btn_load.clicked.connect(self._load_clicked)

    def _browse(self):
        filtros = "All Files (*);;Dump Files (*.dump)"
        start_dir = getattr(self, "_last_dir", str(Path.cwd()))
        abs_path, _ = QFileDialog.getOpenFileName(self, "Select File", start_dir, filtros)
        if abs_path:
            self._last_dir = str(Path(abs_path).parent)
            self.path_edit.setText(abs_path)

    def _load_clicked(self):
        p = self.path_edit.text().strip()
        if not p:
            QMessageBox.warning(self, "Sin archivo", "Seleccione un archivo primero.")
            return
        try:
            render_dump_to(self.plotter, self.fig, p)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def render_dump(self, p: str):
        self.path_edit.setText(p)
        render_dump_to(self.plotter, self.fig, p)

class KeyAreaSeqWidget(QWidget):
    def __init__(self, parent=None, pattern: str = "outputs/dump/key_area_{i}.dump"):
        super().__init__(parent)
        self.pattern = pattern
        top = QWidget(); top_l = QHBoxLayout(top)
        self.idx = QSpinBox(); self.idx.setRange(0, 1_000_000)
        self.btn_prev = QPushButton("◀ Prev")
        self.btn_next = QPushButton("Next ▶")
        self.btn_load = QPushButton("Load")
        self.path_lbl = QLineEdit(); self.path_lbl.setReadOnly(True)
        top_l.addWidget(QLabel("key_area_{i}.dump   i="))
        top_l.addWidget(self.idx)
        top_l.addWidget(self.btn_prev); top_l.addWidget(self.btn_next)
        top_l.addWidget(self.btn_load)
        top_l.addWidget(QLabel("Archivo:")); top_l.addWidget(self.path_lbl, 1)

        center = QWidget(); center_l = QVBoxLayout(center)
        self.plotter = QtInteractor(center); center_l.addWidget(self.plotter)
        self.fig = plt.figure(figsize=(4, 4))
        self.canvas = FigureCanvas(self.fig); center_l.addWidget(self.canvas)

        root_l = QVBoxLayout(self)
        root_l.addWidget(top)
        root_l.addWidget(center, 1)

        self.btn_prev.clicked.connect(lambda: self._step(-1))
        self.btn_next.clicked.connect(lambda: self._step(+1))
        self.btn_load.clicked.connect(self._load_idx)
        self._auto_seed_index()

    def _pattern_path(self, i: int) -> str:
        return self.pattern.format(i=i)

    def _auto_seed_index(self):
        for i in range(0, 10000):
            if Path(self._pattern_path(i)).exists():
                self.idx.setValue(i)
                self._load_idx()
                return
        self.path_lbl.setText("(no encontrado)")

    def _step(self, delta: int):
        new_i = max(0, self.idx.value() + delta)
        self.idx.setValue(new_i)
        self._load_idx()

    def _load_idx(self):
        p = self._pattern_path(self.idx.value())
        self.path_lbl.setText(p)
        if not Path(p).exists():
            QMessageBox.warning(self, "No existe", f"No se encontró:\n{p}")
            return
        try:
            render_dump_to(self.plotter, self.fig, p)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

# ---------------- Pestaña METRICS (como tu captura) ----------------
class MetricsTab(QWidget):
    """
    Layout:
    [Cargar results.csv] [ QLineEdit(path) ]
    [ Tabla (archivo, surface_area, filled_volume, predicted_vacancy)   ]
    [ 2x2 subplots: hist SA | hist FV
                     barras vacancias | scatter SA vs FV (size~vac)   ]
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        # Barra superior
        top = QWidget(); top_l = QHBoxLayout(top)
        self.btn_load = QPushButton("Cargar results.csv")
        self.edit_path = QLineEdit()
        top_l.addWidget(self.btn_load)
        top_l.addWidget(self.edit_path, 1)

        # Tabla
        self.table = QTableWidget()
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Figura 2x2
        self.fig = plt.figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.fig)

        # Root layout
        root = QVBoxLayout(self)
        root.addWidget(top)
        root.addWidget(QLabel("Vista de resultados (archivo, surface_area, filled_volume, predicted_vacancy):"))
        root.addWidget(self.table, 1)
        root.addWidget(self.canvas, 2)

        # Estado
        self.df = None
        self.btn_load.clicked.connect(self.load_results_clicked)

        # Autoload default
        default = Path.cwd() / "outputs" / "csv" / "results.csv"
        if default.exists():
            self.edit_path.setText(str(default))
            self.load_results(default)

    # -------- carga y plotting ----------
    def load_results_clicked(self):
        # Si hay texto, intenta ese path; si no, abre diálogo
        ptxt = self.edit_path.text().strip()
        if ptxt:
            self.load_results(Path(ptxt))
            return
        p, _ = QFileDialog.getOpenFileName(self, "Elegir results.csv",
                                           str(Path.cwd() / "outputs" / "csv"),
                                           "CSV (*.csv);;All Files (*)")
        if p:
            self.edit_path.setText(p)
            self.load_results(Path(p))

    def load_results(self, path: Path):
        try:
            df = pd.read_csv(path)
        except Exception as e:
            QMessageBox.critical(self, "Error al leer CSV", str(e))
            return
        self.df = df
        self._fill_table(df)
        self._draw_plots(df)

    @staticmethod
    def _pick_col(df: pd.DataFrame, candidates):
        for c in candidates:
            if c in df.columns:
                return c
        return None

    def _fill_table(self, df: pd.DataFrame):
        col_file = self._pick_col(df, ["archivo", "file", "path", "dump", "name"])
        col_sa   = self._pick_col(df, ["surface_area","surface","area"])
        col_fv   = self._pick_col(df, ["filled_volume","volume_filled","filled"])
        col_vac  = self._pick_col(df, ["predicted_vacancy","pred_vacancys","vacancys","predicted","vacancy"])

        cols = [col_file, col_sa, col_fv, col_vac]
        headers = ["archivo","surface_area","filled_volume","predicted_vacancy"]
        data_cols = [c if c is not None else "" for c in cols]

        # Construir tabla
        view = df.copy()
        # si faltan, crea columnas vacías para no romper
        for hdr, real in zip(headers, data_cols):
            if real == "":
                view[hdr] = ""
            elif hdr != real:
                view.rename(columns={real: hdr}, inplace=True)

        # Orden de columnas:
        view = view[headers] if all(h in view.columns for h in headers) else view

        self.table.clear()
        self.table.setColumnCount(len(view.columns))
        self.table.setRowCount(len(view))
        self.table.setHorizontalHeaderLabels(view.columns.tolist())
        for i in range(len(view)):
            for j, col in enumerate(view.columns):
                self.table.setItem(i, j, QTableWidgetItem(str(view.iat[i, j])))
        self.table.resizeColumnsToContents()

    def _draw_plots(self, df: pd.DataFrame):
        col_sa  = self._pick_col(df, ["surface_area","surface","area"])
        col_fv  = self._pick_col(df, ["filled_volume","volume_filled","filled"])
        col_vac = self._pick_col(df, ["predicted_vacancy","pred_vacancys","vacancys","predicted","vacancy"])

        # Datos numéricos seguros
        vals_sa  = pd.to_numeric(df[col_sa], errors="coerce").dropna() if col_sa else pd.Series([], dtype=float)
        vals_fv  = pd.to_numeric(df[col_fv], errors="coerce").dropna() if col_fv else pd.Series([], dtype=float)
        vals_vac = pd.to_numeric(df[col_vac], errors="coerce").dropna() if col_vac else pd.Series([], dtype=float)

        # Figure 2x2
        self.fig.clf()
        ax1 = self.fig.add_subplot(221)  # hist SA
        ax2 = self.fig.add_subplot(222)  # hist FV
        ax3 = self.fig.add_subplot(223)  # barras VAC
        ax4 = self.fig.add_subplot(224)  # scatter SA vs FV (size~vac)

        # 1) Hist SA
        if len(vals_sa):
            ax1.hist(vals_sa.values, bins=20)
        ax1.set_title("Distribución: surface_area")
        ax1.set_xlabel("surface_area"); ax1.set_ylabel("Frecuencia"); ax1.grid(True, linewidth=0.3)

        # 2) Hist FV
        if len(vals_fv):
            ax2.hist(vals_fv.values, bins=20)
        ax2.set_title("Distribución: filled_volume")
        ax2.set_xlabel("filled_volume"); ax2.set_ylabel("Frecuencia"); ax2.grid(True, linewidth=0.3)

        # 3) Barras VAC (conteo)
        if len(vals_vac):
            # Agrupa por valor (redondeado a int)
            vac_int = vals_vac.round().astype(int)
            grp = vac_int.value_counts().sort_index()
            ax3.bar(grp.index.astype(str), grp.values)
        ax3.set_title("Conteo: predicted_vacancy")
        ax3.set_xlabel("predicted_vacancy"); ax3.set_ylabel("Cantidad de poros")
        ax3.grid(True, linewidth=0.3)

        # 4) Scatter SA vs FV (size ~ VAC)
        if len(vals_sa) and len(vals_fv):
            if len(vals_vac) == len(df):
                # Alinear tamaños con filas válidas
                # crea máscara de filas válidas para SA y FV
                mask = (~pd.to_numeric(df[col_sa], errors="coerce").isna()) & \
                       (~pd.to_numeric(df[col_fv], errors="coerce").isna())
                vac_sizes = pd.to_numeric(df[col_vac], errors="coerce").fillna(0.0)
                vac_sizes = vac_sizes[mask]
                sa_sc = pd.to_numeric(df[col_sa], errors="coerce")[mask]
                fv_sc = pd.to_numeric(df[col_fv], errors="coerce")[mask]
            else:
                # fallback simple
                sa_sc, fv_sc = vals_sa, vals_fv
                vac_sizes = vals_vac.reindex_like(vals_sa).fillna(v_vals := (np.ones(len(sa_sc))*3))
            # tamaño proporcional (evita 0)
            sizes = (np.clip(vac_sizes.values, 0.5, None) * 10.0)
            ax4.scatter(sa_sc.values, fv_sc.values, s=sizes)
        ax4.set_title("surface_area vs filled_volume (size ~ vac)")
        ax4.set_xlabel("surface_area"); ax4.set_ylabel("filled_volume"); ax4.grid(True, linewidth=0.3)

        self.fig.tight_layout()
        self.canvas.draw()

# ---------------- Ventana Principal ----------------
class SettingsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.showMaximized()
        self.setWindowTitle("VacancyFinder-SiMAF   0.3.9.6")

        self.params = load_params()
        cfg = self.params.setdefault('CONFIG', [{}])[0]

        form_layout = QFormLayout()

        # Progreso + log
        self.progress = QProgressBar(); self.progress.setRange(0, 100); self.progress.setValue(0)
        form_layout.addRow("Progreso:", self.progress)

        self.log_output = QPlainTextEdit(); self.log_output.setReadOnly(True)
        self.log_output.setMinimumHeight(200)
        self.log_output.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        form_layout.addRow("Output Log:", self.log_output)

        # Checkboxes
        self.check_training = QCheckBox(); self.check_training.setChecked(cfg.get('training', False))
        self.check_geometric = QCheckBox(); self.check_geometric.setChecked(cfg.get('geometric_method', False))
        self.check_activate_relax = QCheckBox(); self.check_activate_relax.setChecked(cfg.get('activate_generate_relax', False))
        form_layout.addRow("Enable Training:", self.check_training)
        form_layout.addRow("Geometric Method:", self.check_geometric)
        form_layout.addRow("Activate Generate Relax:", self.check_activate_relax)

        # generate_relax
        gr = cfg.get('generate_relax', ["bcc", 1.0]) + [1, 1, 1, "Fe"]
        self.edit_lattice = QLineEdit(gr[0])
        self.spin_lattice_a = QDoubleSpinBox()
        self._configure_spin(self.spin_lattice_a, 0.0, 100.0, float(gr[1]), step=0.1, decimals=3)
        self.spin_rx = QSpinBox(); self._configure_spin(self.spin_rx, 1, 100, gr[2], step=1)
        self.spin_ry = QSpinBox(); self._configure_spin(self.spin_ry, 1, 100, gr[3], step=1)
        self.spin_rz = QSpinBox(); self._configure_spin(self.spin_rz, 1, 100, gr[4], step=1)
        self.edit_atom = QLineEdit(gr[5])

        form_layout.addRow("Lattice Type:", self.edit_lattice)
        form_layout.addRow("Lattice Param a:", self.spin_lattice_a)
        form_layout.addRow("Replicas X:", self.spin_rx)
        form_layout.addRow("Replicas Y:", self.spin_ry)
        form_layout.addRow("Replicas Z:", self.spin_rz)
        form_layout.addRow("Atom Type:", self.edit_atom)

        # Selectores dumps
        self.edit_relax = QLineEdit(cfg.get('relax', ''))
        btn_relax = QPushButton("Browse Relax"); btn_relax.clicked.connect(lambda: self.browse_file(self.edit_relax))
        relax_layout = QHBoxLayout(); relax_layout.addWidget(self.edit_relax); relax_layout.addWidget(btn_relax)
        form_layout.addRow("Relax Dump:", self._wrap(relax_layout))

        self.edit_defect = QLineEdit(cfg.get('defect', [''])[0])
        btn_defect = QPushButton("Browse Defect"); btn_defect.clicked.connect(lambda: self.browse_file(self.edit_defect))
        defect_layout = QHBoxLayout(); defect_layout.addWidget(self.edit_defect); defect_layout.addWidget(btn_defect)
        form_layout.addRow("Defect Dump:", self._wrap(defect_layout))

        # Campos numéricos
        fields = [
            ("radius", QDoubleSpinBox, 0, 100, cfg.get('radius', 0.0), 3),
            ("cutoff", QDoubleSpinBox, 0, 100, cfg.get('cutoff', 0.0), 3),
            ("max_graph_size", QSpinBox, 0, 10000, cfg.get('max_graph_size', 0), 0),
            ("max_graph_variations", QSpinBox, 0, 10000, cfg.get('max_graph_variations', 0), 0),
            ("radius_training", QDoubleSpinBox, 0, 100, cfg.get('radius_training', 0.0), 3),
            ("training_file_index", QSpinBox, 0, 10000, cfg.get('training_file_index', 0), 0),
            ("cluster tolerance", QDoubleSpinBox, 0, 100, cfg.get('cluster tolerance', 0.0), 3),
            ("divisions_of_cluster", QSpinBox, 0, 10000, cfg.get('divisions_of_cluster', 0), 0),
            ("iteraciones_clusterig", QSpinBox, 0, 10000, cfg.get('iteraciones_clusterig', 0), 0),
        ]
        for name, cls, mn, mx, val, dec in fields:
            widget = cls()
            step = 0.1 if cls is QDoubleSpinBox else 1
            decimals = dec if cls is QDoubleSpinBox else None
            self._configure_spin(widget, mn, mx, val, step=step, decimals=decimals)
            setattr(self, f"spin_{name}".replace(' ', '_'), widget)
            form_layout.addRow(f"{name.replace('_',' ').title()}:", widget)

        # Botones
        btn_save = QPushButton("Save Settings"); btn_save.clicked.connect(self.save_settings_and_notify)
        btn_run = QPushButton("Run VacancyAnalysis"); btn_run.clicked.connect(self.run_vacancy_analysis)
        btn_total = QPushButton("Total Vacancies"); btn_total.clicked.connect(self.show_total_vacancies)
        hb = QHBoxLayout(); hb.addWidget(btn_save); hb.addWidget(btn_run); hb.addWidget(btn_total)
        form_layout.addRow(hb)

        # Panel izquierdo
        controls_widget = QWidget(); controls_widget.setLayout(form_layout)
        controls_widget.setFixedWidth(int(320 * 1.3))
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setWidget(controls_widget)

        # Panel derecho (tabs)
        self.tabs = QTabWidget()

        # Tab Main
        main_tab = QWidget(); main_layout = QVBoxLayout(main_tab)
        self.plotter = QtInteractor(main_tab); main_layout.addWidget(self.plotter)
        self.fig = plt.figure(figsize=(4, 4)); self.canvas = FigureCanvas(self.fig); main_layout.addWidget(self.canvas)
        self.table = QTableWidget(); main_layout.addWidget(self.table)
        self.tabs.addTab(main_tab, "Main")

        # Tab Viewer 1
        self.viewer1 = DumpViewerWidget()
        self.tabs.addTab(self.viewer1, "Viewer 1")

        # Tab Metrics (igual a tu captura)
        self.metrics_tab = MetricsTab()
        self.tabs.addTab(self.metrics_tab, "Metrics")

        # Tab Key Areas
        self.viewer2 = KeyAreaSeqWidget()
        self.tabs.addTab(self.viewer2, "Key Areas")

        # Layout principal
        main = QWidget(); hl = QHBoxLayout(main); hl.addWidget(scroll); hl.addWidget(self.tabs, 1)
        self.setCentralWidget(main)

        # Carga inicial de key_areas.dump si existe
        dump_path = Path.cwd() / 'outputs' / 'dump' / 'key_areas.dump'
        if dump_path.exists():
            self.load_dump(str(dump_path))
            try:
                self.viewer1.render_dump(str(dump_path))
            except Exception:
                pass

    # ====== Utils UI ======
    def _wrap(self, layout: QHBoxLayout) -> QWidget:
        w = QWidget(); w.setLayout(layout); return w

    def _configure_spin(self, spin, mn, mx, val, step=None, decimals=None):
        spin.setRange(mn, mx)
        if isinstance(spin, QDoubleSpinBox):
            if decimals is not None:
                spin.setDecimals(decimals)
            spin.setSingleStep(step if step is not None else 0.1)
        else:
            spin.setSingleStep(step if step is not None else 1)
        spin.setValue(val)

    def save_settings_and_notify(self):
        saved_path = self.save_settings()
        QMessageBox.information(self, "Settings Saved", f"Parameters saved to:\n{saved_path}")

    def save_settings(self):
        cfg = self.params['CONFIG'][0]
        cfg['training'] = self.check_training.isChecked()
        cfg['geometric_method'] = self.check_geometric.isChecked()
        cfg['activate_generate_relax'] = self.check_activate_relax.isChecked()
        cfg['generate_relax'] = [
            self.edit_lattice.text(),
            float(self.spin_lattice_a.value()),
            self.spin_rx.value(), self.spin_ry.value(), self.spin_rz.value(),
            self.edit_atom.text().strip() or 'Fe'
        ]
        cfg['relax'] = self.edit_relax.text()
        cfg['defect'] = [self.edit_defect.text()]
        for key in ['radius', 'cutoff', 'max_graph_size', 'max_graph_variations',
                    'radius_training', 'training_file_index', 'cluster tolerance',
                    'divisions_of_cluster', 'iteraciones_clusterig']:
            widget = getattr(self, f"spin_{key}".replace(' ', '_'))
            cfg[key] = widget.value()
        return save_params(self.params)

    def browse_file(self, line_edit):
        filtros = "All Files (*);;Dump Files (*.dump)"
        start_dir = getattr(self, "_last_dir", str(Path.cwd()))
        abs_path, _ = QFileDialog.getOpenFileName(self, "Select File", start_dir, filtros)
        if abs_path:
            self._last_dir = str(Path(abs_path).parent)
            try:
                line_edit.setText(Path(abs_path).relative_to(GUI_ROOT).as_posix())
            except ValueError:
                line_edit.setText(abs_path)

    # Visual principal
    def load_dump(self, dump_path):
        self.progress.setValue(0)
        try:
            render_dump_to(self.plotter, self.fig, dump_path)
            self.canvas.draw()
            self.progress.setValue(100)
        except Exception as e:
            self.progress.setValue(0)
            QMessageBox.critical(self, "Error al cargar dump", str(e))

    def show_total_vacancies(self):
        try:
            path = Path.cwd() / 'outputs' / 'csv' / 'results.csv'
            if not path.exists():
                QMessageBox.warning(self, "Archivo no encontrado", f"No existe:\n{path.as_posix()}")
                return
            df = pd.read_csv(path)
            candidates = ["predicted_vacancy","pred_vacancys","vacancys","predicted","vacancy"]
            col = next((c for c in candidates if c in df.columns), None)
            if col is None:
                QMessageBox.critical(self, "Columna no encontrada",
                                     "No se encontró columna de vacancias en results.csv")
                return
            vals = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
            total = int(np.ceil(float(vals.sum())))
            msg = QMessageBox(self); msg.setWindowTitle("Total de vacancias")
            msg.setText(f"<h2 style='margin:0'>Total de vacancias: {total}</h2>")
            msg.exec()
            print(f"Vacancias totales: {total}")
        except Exception:
            QMessageBox.critical(self, "Error calculando total", traceback.format_exc())

    # Run
    def run_vacancy_analysis(self):
        self.log_output.clear()
        buf = io.StringIO()
        self.progress.setRange(0, 0)
        try:
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                vfs.VacancyAnalysis()
            self.progress.setRange(0, 100)
            self.progress.setValue(100)
            self.log_output.setPlainText(buf.getvalue())
            QMessageBox.information(self, "Análisis completado", "VacancyAnalysis terminó correctamente.")

            # Auto-refrescar Metrics con results.csv (o resultados NN)
            out_dir = Path.cwd() / 'outputs' / 'csv'
            for name in ("results_keras_oop.csv", "results.csv"):
                p = out_dir / name
                if p.exists():
                    self.metrics_tab.edit_path.setText(str(p))
                    self.metrics_tab.load_results(p)
                    break

            # Refrescar viewers
            dump_path = Path.cwd() / 'outputs' / 'dump' / 'key_areas.dump'
            if dump_path.exists():
                self.load_dump(str(dump_path))
                try:
                    self.viewer1.render_dump(str(dump_path))
                except Exception:
                    pass

        except Exception:
            self.progress.setRange(0, 100)
            self.progress.setValue(0)
            buf.write(traceback.format_exc())
            self.log_output.setPlainText(buf.getvalue())
            QMessageBox.critical(self, "Error en análisis", "Falló VacancyAnalysis. Revisa el log.")

def main():
    app = QApplication(sys.argv)
    win = SettingsWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
