import sys
import io
import json
import contextlib
import traceback
from pathlib import Path
import shutil
import os

# Forzar backend XCB en Wayland (evita problemas en algunas distros)
os.environ["QT_QPA_PLATFORM"] = "xcb"

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFormLayout, QCheckBox,
    QDoubleSpinBox, QSpinBox, QLineEdit, QPushButton, QFileDialog,
    QMessageBox, QHBoxLayout, QPlainTextEdit, QVBoxLayout,
    QProgressBar, QSizePolicy, QComboBox, QTableWidget, QTableWidgetItem,
    QScrollArea, QLabel, QTabWidget, QListWidget, QListWidgetItem,
    QAbstractItemView,   # ← AGREGA ESTO
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


# ---------- Render común (3D + 2D) ----------
def render_dump_to(plotter: QtInteractor, fig: plt.Figure, dump_path: str):
    """Dibuja celda + puntos; colorea por 'Cluster' si existe."""
    pipeline = import_file(dump_path)
    data = pipeline.compute()

    # Celda (3x4)
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

    # Partículas
    pos_prop = data.particles.positions
    positions = pos_prop.array if hasattr(pos_prop, "array") else np.asarray(pos_prop, dtype=float)

    # Cluster opcional
    cluster_vals = None
    for name in ("Cluster", "cluster", "c_Cluster", "c_cluster", "ClusterID", "cluster_id"):
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
        plotter.add_mesh(
            pts,
            scalars="cluster",
            render_points_as_spheres=True,
            point_size=8,
            cmap="tab20",
            show_scalar_bar=False,
        )
    else:
        plotter.add_mesh(
            pv.PolyData(positions),
            color="black",
            render_points_as_spheres=True,
            point_size=8
        )
    plotter.reset_camera()
    plotter.set_scale(1, 1, 1)

    # 2D
    fig.clf()
    ax = fig.add_subplot(111)
    for i, j in edges:
        x0, y0 = corners[i][0], corners[i][1]
        x1, y1 = corners[j][0], corners[j][1]
        ax.plot([x0, x1], [y0, y1], '-', linewidth=1)

    if cluster_idx is not None:
        ax.scatter(
            positions[:, 0], positions[:, 1], s=10,
            c=cluster_idx, cmap="tab20",
            vmin=0, vmax=len(unique_clusters)-1
        )
    else:
        ax.scatter(positions[:, 0], positions[:, 1], s=10, color="k")

    ax.set_xlabel('X'); ax.set_ylabel('Y')
    ax.set_aspect('equal', 'box')
    ax.grid(True, linewidth=0.3)
    fig.canvas.draw()


# ---------- Widgets auxiliares ----------
class DumpViewerWidget(QWidget):
    """Viewer con selector de archivo .dump."""
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
    """Viewer para outputs/dump/key_area_{i}.dump con controles de índice."""
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


# ---------- Pestaña de Resultados (Histogramas) ----------
class ResultsTabWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Controles arriba
        top = QWidget(); top_l = QHBoxLayout(top)

        self.csv_combo = QComboBox(); self.csv_combo.setEditable(True)
        self.btn_reload_list = QPushButton("⟳")
        self.btn_load_csv = QPushButton("Cargar CSV")

        self.list_cols = QListWidget()
        self.list_cols.setSelectionMode(QAbstractItemView.SingleSelection)

        self.spin_bins = QSpinBox(); self.spin_bins.setRange(2, 200); self.spin_bins.setValue(30)
        self.chk_norm = QCheckBox("Normalizar (densidad)")
        self.lbl_total = QLabel("Total vacancias: —")

        top_l.addWidget(QLabel("Resultados CSV:"))
        top_l.addWidget(self.csv_combo, 1)
        top_l.addWidget(self.btn_reload_list)
        top_l.addWidget(self.btn_load_csv)
        top_l.addWidget(QLabel("Bins:"))
        top_l.addWidget(self.spin_bins)
        top_l.addWidget(self.chk_norm)
        top_l.addWidget(self.lbl_total)

        # Figura
        self.fig = plt.figure(figsize=(5, 4))
        self.canvas = FigureCanvas(self.fig)

        # Layout
        root = QVBoxLayout(self)
        root.addWidget(top)
        mid = QHBoxLayout()
        mid.addWidget(QLabel("Columnas numéricas:"))
        mid.addWidget(self.list_cols, 1)
        root.addLayout(mid)
        root.addWidget(self.canvas, 2)

        # Estado
        self.df = None
        self._refresh_csv_list()

        # Conexiones
        self.btn_reload_list.clicked.connect(self._refresh_csv_list)
        self.btn_load_csv.clicked.connect(self._load_csv_clicked)
        self.list_cols.itemSelectionChanged.connect(self._plot_selected)
        self.spin_bins.valueChanged.connect(self._plot_selected)
        self.chk_norm.toggled.connect(self._plot_selected)

    def _refresh_csv_list(self):
        csv_dir = Path.cwd() / 'outputs' / 'csv'
        self.csv_combo.clear()
        if csv_dir.exists():
            for f in sorted(csv_dir.glob('*.csv')):
                self.csv_combo.addItem(f.name)

    def load_csv(self, path: Path):
        try:
            self.df = pd.read_csv(path)
        except Exception as e:
            QMessageBox.critical(self, "Error al leer CSV", str(e))
            return
        # Columnas numéricas
        num_cols = [c for c in self.df.columns if pd.api.types.is_numeric_dtype(self.df[c])]
        self.list_cols.clear()
        for c in num_cols:
            self.list_cols.addItem(QListWidgetItem(c))

        # Total de vacancias si existe columna conocida
        total = self._compute_total_vacancies(self.df)
        if total is None:
            self.lbl_total.setText("Total vacancias: —")
        else:
            self.lbl_total.setText(f"Total vacancias: {total}")

        # Autoselect: pred_vacancys si está, si no primera numérica
        sel = None
        for c in ("pred_vacancys", "vacancys_est", "vacancys", "predicted_vacancy", "predicted", "vacancy"):
            if c in num_cols:
                sel = c; break
        if sel is None and num_cols:
            sel = num_cols[0]
        if sel is not None:
            items = self.list_cols.findItems(sel, Qt.MatchExactly)
            if items:
                self.list_cols.setCurrentItem(items[0])
                self._plot_selected()

    def _load_csv_clicked(self):
        nombre = self.csv_combo.currentText().strip()
        if not nombre:
            QMessageBox.warning(self, "Sin selección", "No has elegido ningún CSV.")
            return
        ruta = Path.cwd() / 'outputs' / 'csv' / nombre
        self.load_csv(ruta)

    def _plot_selected(self):
        if self.df is None:
            return
        items = self.list_cols.selectedItems()
        if not items:
            return
        col = items[0].text()
        bins = self.spin_bins.value()
        density = self.chk_norm.isChecked()

        self.fig.clf()
        ax = self.fig.add_subplot(111)
        vals = pd.to_numeric(self.df[col], errors='coerce').dropna()
        ax.hist(vals.values, bins=bins, density=density)
        ax.set_title(f"Histograma: {col}")
        ax.set_xlabel(col); ax.set_ylabel("Densidad" if density else "Frecuencia")
        ax.grid(True, linewidth=0.3)
        self.canvas.draw()

    @staticmethod
    def _compute_total_vacancies(df: pd.DataFrame):
        candidates = ["pred_vacancys", "vacancys_est", "vacancys", "predicted_vacancy", "predicted", "vacancy"]
        col = next((c for c in candidates if c in df.columns), None)
        if col is None:
            return None
        vals = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
        return int(np.ceil(float(vals.sum())))


# ---------- Ventana principal ----------
class SettingsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.showMaximized()
        self.setWindowTitle("VacancyFinder-SiMAF   0.3.9.5")

        self.params = load_params()
        cfg = self.params.setdefault('CONFIG', [{}])[0]

        form_layout = QFormLayout()

        # Barra de progreso
        self.progress = QProgressBar()
        self.progress.setRange(0, 100); self.progress.setValue(0)
        form_layout.addRow("Progreso:", self.progress)

        # Log de salida
        self.log_output = QPlainTextEdit()
        self.log_output.setReadOnly(True)
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

        # Selectores de dump
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

        # Panel izquierdo (controles)
        controls_widget = QWidget(); controls_widget.setLayout(form_layout)
        controls_widget.setFixedWidth(int(320 * 1.3))
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setWidget(controls_widget)

        # Panel derecho con pestañas
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

        # Tab Key Areas
        self.viewer2 = KeyAreaSeqWidget()
        self.tabs.addTab(self.viewer2, "Key Areas")

        # Tab Results (histogramas)
        self.results_tab = ResultsTabWidget()
        self.tabs.addTab(self.results_tab, "Results")

        # Layout principal
        main = QWidget(); hl = QHBoxLayout(main); hl.addWidget(scroll); hl.addWidget(self.tabs, 1)
        self.setCentralWidget(main)

        # Carga inicial (si existe)
        dump_path = Path.cwd() / 'outputs' / 'dump' / 'key_areas.dump'
        if dump_path.exists():
            self.load_dump(str(dump_path))
            try:
                self.viewer1.render_dump(str(dump_path))
            except Exception:
                pass

    # ===== Utils UI =====
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

    def _refresh_csv_list(self):
        # Mantengo para compatibilidad con tab Main (tabla simple)
        csv_dir = Path.cwd() / 'outputs' / 'csv'
        if hasattr(self, "csv_combo"):  # por si lo usás en otro lado
            self.csv_combo.clear()
            if csv_dir.exists():
                for f in sorted(csv_dir.glob('*.csv')):
                    self.csv_combo.addItem(f.name)

    def load_csv_results(self):
        # Mantengo esta rutina para la tabla del tab Main
        nombre = self.csv_combo.currentText()
        if not nombre:
            QMessageBox.warning(self, "Sin selección", "No has elegido ningún CSV.")
            return
        ruta = Path.cwd() / 'outputs' / 'csv' / nombre
        try:
            df = pd.read_csv(ruta)
        except Exception as e:
            QMessageBox.critical(self, "Error al leer CSV", str(e))
            return
        self.table.clear()
        self.table.setColumnCount(len(df.columns))
        self.table.setRowCount(len(df))
        self.table.setHorizontalHeaderLabels(df.columns.tolist())
        for i in range(len(df)):
            for j, col in enumerate(df.columns):
                self.table.setItem(i, j, QTableWidgetItem(str(df.iat[i, j])))
        self.table.resizeColumnsToContents()

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

    # --- Visual principal ---
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
        """Total de vacancias desde outputs/csv/results.csv (si existe)."""
        try:
            path = Path.cwd() / 'outputs' / 'csv' / 'results.csv'
            if not path.exists():
                QMessageBox.warning(self, "Archivo no encontrado",
                                    f"No existe:\n{path.as_posix()}")
                return

            df = pd.read_csv(path)
            candidates = ["pred_vacancys", "vacancys_est", "vacancys", "predicted_vacancy", "predicted", "vacancy"]
            col = next((c for c in candidates if c in df.columns), None)
            if col is None:
                QMessageBox.critical(self, "Columna no encontrada",
                                     "No se encontró ninguna de estas columnas en results.csv:\n"
                                     + ", ".join(candidates))
                return

            vals = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
            total = float(vals.sum())
            total_int = int(np.ceil(total))

            msg = QMessageBox(self)
            msg.setWindowTitle("Total de vacancias")
            msg.setText(f"<h2 style='margin:0'>Total de vacancias: {total_int}</h2>")
            msg.exec()
            print(f"Vacancias totales: {total_int}")

        except Exception as e:
            QMessageBox.critical(self, "Error calculando total", str(e))

    # --- Run del análisis ---
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

            # Actualizar pestaña de resultados automáticamente
            out_dir = Path.cwd() / 'outputs' / 'csv'
            best_csv = None
            for name in ("results_keras_oop.csv", "results.csv"):
                p = out_dir / name
                if p.exists():
                    best_csv = p; break
            if best_csv is not None:
                self.results_tab._refresh_csv_list()
                # Selecciona y carga el mejor CSV
                idx = self.results_tab.csv_combo.findText(best_csv.name, Qt.MatchExactly)
                if idx >= 0:
                    self.results_tab.csv_combo.setCurrentIndex(idx)
                self.results_tab.load_csv(best_csv)

            # Refrescar viewers con key_areas.dump si existe
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
