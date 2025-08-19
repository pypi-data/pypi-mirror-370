import sys
import io
import json
import contextlib
import traceback
from pathlib import Path
import os
os.environ['QT_QPA_PLATFORM'] = 'xcb'

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFormLayout, QCheckBox,
    QDoubleSpinBox, QSpinBox, QLineEdit, QPushButton, QFileDialog,
    QMessageBox, QHBoxLayout, QPlainTextEdit, QVBoxLayout,
    QProgressBar, QSizePolicy, QComboBox, QTableWidget, QTableWidgetItem
)
from pyvistaqt import QtInteractor
import pyvista as pv
import numpy as np
from ovito.io import import_file
from ovito.modifiers import ConstructSurfaceModifier
from vfscript import vfs  # import VacancyAnalysis
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# Directorio base de la GUI (donde está este script)
GUI_ROOT = Path(__file__).resolve().parent
PARAMS_FILE = GUI_ROOT / 'input_params.json'


def load_params():
    if PARAMS_FILE.exists():
        return json.loads(PARAMS_FILE.read_text())
    return {}


def save_params(params):
    PARAMS_FILE.write_text(json.dumps(params, indent=4))


class SettingsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Maximizar ventana
        self.showMaximized()
        self.setWindowTitle("VacancyFinder-SiMAF   0.3.6.1")

        # Carga parámetros
        self.params = load_params()
        cfg = self.params.setdefault('CONFIG', [{}])[0]

        # Layout principal de controles
        form_layout = QFormLayout()

        # Progreso
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        form_layout.addRow("Progreso:", self.progress)

        # Log de salida
        self.log_output = QPlainTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMinimumHeight(200)
        self.log_output.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        form_layout.addRow("Output Log:", self.log_output)

        # Checkboxes
        self.check_training = QCheckBox()
        self.check_training.setChecked(cfg.get('training', False))
        self.check_geometric = QCheckBox()
        self.check_geometric.setChecked(cfg.get('geometric_method', False))
        self.check_activate_relax = QCheckBox()
        self.check_activate_relax.setChecked(cfg.get('activate_generate_relax', False))
        form_layout.addRow("Enable Training:", self.check_training)
        form_layout.addRow("Geometric Method:", self.check_geometric)
        form_layout.addRow("Activate Generate Relax:", self.check_activate_relax)

        # Campos generate_relax
        gr = cfg.get('generate_relax', ["bcc", 1.0]) + [1,1,1,"Fe"]
        self.edit_lattice = QLineEdit(gr[0])
        self.edit_lattice_a = QLineEdit(str(gr[1]))
        self.spin_rx = QSpinBox(); self._configure_spin(self.spin_rx, 1, 100, gr[2])
        self.spin_ry = QSpinBox(); self._configure_spin(self.spin_ry, 1, 100, gr[3])
        self.spin_rz = QSpinBox(); self._configure_spin(self.spin_rz, 1, 100, gr[4])
        self.edit_atom = QLineEdit(gr[5])
        form_layout.addRow("Lattice Type:", self.edit_lattice)
        form_layout.addRow("Lattice Param a:", self.edit_lattice_a)
        form_layout.addRow("Replicas X:", self.spin_rx)
        form_layout.addRow("Replicas Y:", self.spin_ry)
        form_layout.addRow("Replicas Z:", self.spin_rz)
        form_layout.addRow("Atom Type:", self.edit_atom)

        # Selectores de dump
        self.edit_relax = QLineEdit(cfg.get('relax', ''))
        btn_relax = QPushButton("Browse Relax")
        btn_relax.clicked.connect(lambda: self.browse_file(self.edit_relax))
        rbx = QHBoxLayout(); rbx.addWidget(self.edit_relax); rbx.addWidget(btn_relax)
        form_layout.addRow("Relax Dump:", rbx)

        self.edit_defect = QLineEdit(cfg.get('defect', [''])[0])
        btn_defect = QPushButton("Browse Defect")
        btn_defect.clicked.connect(lambda: self.browse_file(self.edit_defect))
        dbx = QHBoxLayout(); dbx.addWidget(self.edit_defect); dbx.addWidget(btn_defect)
        form_layout.addRow("Defect Dump:", dbx)

        # Selector de CSV y botón
        self.csv_combo = QComboBox()
        self._refresh_csv_list()
        form_layout.addRow("Resultados CSV:", self.csv_combo)
        btn_csv = QPushButton("Cargar CSV")
        btn_csv.clicked.connect(self.load_csv_results)
        form_layout.addRow(btn_csv)

        # Campos numéricos configurables
        fields = [
            ("radius", QDoubleSpinBox, 0, 100, cfg.get('radius', 0.0), 3),
            ("cutoff", QDoubleSpinBox, 0, 100, cfg.get('cutoff', 0.0), 3),
            ("max_graph_size", QSpinBox, 0, 10000, cfg.get('max_graph_size', 0), 0),
            ("max_graph_variations", QSpinBox, 0, 10000, cfg.get('max_graph_variations', 0), 0),
            ("radius_training", QDoubleSpinBox, 0, 100, cfg.get('radius_training', 0.0), 3),
            ("training_file_index", QSpinBox, 0, 10000, cfg.get('training_file_index', 0), 0),
            ("cluster tolerance", QDoubleSpinBox, 0, 100, cfg.get('cluster tolerance', 0.0), 3),
            ("divisions_of_cluster", QSpinBox, 0, 10000, cfg.get('divisions_of_cluster', 0), 0),
            ("iteraciones_clusterig", QSpinBox, 0, 10000, cfg.get('iteraciones_clusterig', 0), 0)
        ]
        for name, cls, mn, mx, val, dec in fields:
            widget = cls()
            if issubclass(cls, QDoubleSpinBox):
                widget.setDecimals(dec)
            widget.setRange(mn, mx)
            widget.setValue(val)
            self._configure_spin(widget, mn, mx, val)
            setattr(self, f"spin_{name}".replace(' ', '_'), widget)
            form_layout.addRow(f"{name.replace('_',' ').title()}:", widget)

        # Botones de acción
        btn_save = QPushButton("Save Settings")
        btn_save.clicked.connect(self.save_settings_and_notify)
        btn_run = QPushButton("Run VacancyAnalysis")
        btn_run.clicked.connect(self.run_vacancy_analysis)
        hb = QHBoxLayout(); hb.addWidget(btn_save); hb.addWidget(btn_run)
        form_layout.addRow(hb)

        # Widget de controles
        controls_widget = QWidget()
        controls_widget.setLayout(form_layout)
        controls_widget.setFixedWidth(int(320 * 1.3))
        controls_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        # Panel de visualización 3D, 2D y tabla
        viewer_widget = QWidget()
        viewer_layout = QVBoxLayout(viewer_widget)
        viewer_layout.setContentsMargins(0, 0, 0, 0)

        # 3D
        self.plotter = QtInteractor(viewer_widget)
        viewer_layout.addWidget(self.plotter)
        # 2D
        self.fig = plt.figure(figsize=(4,4))
        self.canvas = FigureCanvas(self.fig)
        viewer_layout.addWidget(self.canvas)
        # Tabla CSV
        self.table = QTableWidget()
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        viewer_layout.addWidget(self.table)

        # Set central
        main = QWidget()
        hl = QHBoxLayout(main)
        hl.setContentsMargins(5,5,5,5)
        hl.setSpacing(10)
        hl.addWidget(controls_widget)
        hl.addWidget(viewer_widget, 1)
        self.setCentralWidget(main)

        # Carga inicial de dump
        dump_path = Path.cwd() / 'outputs' / 'dump' / 'key_areas.dump'
        if dump_path.exists():
            self.load_dump(str(dump_path))
        else:
            QMessageBox.warning(self, "No encontrado",
                                f"No existe el fichero:\n{dump_path}")

    def _configure_spin(self, spin, mn, mx, val):
        """Habilita edición por teclado en spin boxes"""
        spin.setRange(mn, mx)
        spin.setValue(val)
        spin.setKeyboardTracking(True)
        spin.setReadOnly(False)
        spin.setFocusPolicy(Qt.StrongFocus)

    def _refresh_csv_list(self):
        """Rellena el combo con todos los .csv de outputs/csv/"""
        csv_dir = Path.cwd() / 'outputs' / 'csv'
        self.csv_combo.clear()
        if csv_dir.exists():
            for f in sorted(csv_dir.glob('*.csv')):
                self.csv_combo.addItem(f.name)

    def load_csv_results(self):
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
        # Rellenar tabla
        self.table.clear()
        self.table.setColumnCount(len(df.columns))
        self.table.setRowCount(len(df))
        self.table.setHorizontalHeaderLabels(df.columns.tolist())
        for i in range(len(df)):
            for j, col in enumerate(df.columns):
                self.table.setItem(i, j, QTableWidgetItem(str(df.iat[i, j])))
        self.table.resizeColumnsToContents()

    def save_settings_and_notify(self):
        self.save_settings()
        QMessageBox.information(self, "Settings Saved", "Parameters saved to input_params.json")

    def save_settings(self):
        cfg = self.params['CONFIG'][0]
        cfg['training'] = self.check_training.isChecked()
        cfg['geometric_method'] = self.check_geometric.isChecked()
        cfg['activate_generate_relax'] = self.check_activate_relax.isChecked()
        cfg['generate_relax'] = [
            self.edit_lattice.text(),
            float(self.edit_lattice_a.text()),
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
        save_params(self.params)

    def browse_file(self, line_edit):
        abs_path, _ = QFileDialog.getOpenFileName(
            self, "Select Dump File", "", "Dump Files (*.dump);;All Files (*)"
        )
        if abs_path:
            try:
                line_edit.setText(Path(abs_path).relative_to(GUI_ROOT).as_posix())
            except ValueError:
                line_edit.setText(abs_path)

    def load_dump(self, dump_path):
        """Carga dump y actualiza vista 3D/2D"""
        self.progress.setValue(0)
        pipeline = import_file(dump_path)
        modifier = ConstructSurfaceModifier(radius=1.0)
        pipeline.modifiers.append(modifier)
        data = pipeline.compute()
        self.progress.setValue(33)

        # Geometría 3D
        raw_cell = data.cell.matrix
        a1, a2, a3 = np.array(raw_cell[0][:3]), np.array(raw_cell[1][:3]), np.array(raw_cell[2][:3])
        corners = [np.zeros(3), a1, a2, a3, a1+a2, a1+a3, a2+a3, a1+a2+a3]
        edges = [(0,1),(0,2),(0,3),(1,4),(1,5),(2,4),(2,6),(3,5),(3,6),(4,7),(5,7),(6,7)]
        self.plotter.clear()
        for i,j in edges:
            self.plotter.add_mesh(pv.Line(corners[i], corners[j]), color='blue', line_width=2)
        pos_prop = data.particles.positions
        positions = pos_prop.array if hasattr(pos_prop, 'array') else pos_prop[:]
        self.plotter.add_mesh(pv.PolyData(positions),
                              color='black', render_points_as_spheres=True, point_size=8)
        self.plotter.reset_camera()
        self.progress.setValue(66)

        # Vista 2D
        self.fig.clf()
        ax = self.fig.add_subplot(111)
        for i,j in edges:
            x0,y0 = corners[i][0], corners[i][1]
            x1,y1 = corners[j][0], corners[j][1]
            ax.plot([x0,x1], [y0,y1], '-', linewidth=1)
        ax.scatter(positions[:,0], positions[:,1], s=10)
        ax.set_xlabel('X'); ax.set_ylabel('Y')
        ax.set_aspect('equal', 'box')
        self.canvas.draw()
        self.progress.setValue(100)


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
            # refrescar CSV
            self._refresh_csv_list()
            dump_path = Path.cwd() / 'outputs' / 'dump' / 'key_areas.dump'
            if dump_path.exists():
                self.load_dump(str(dump_path))
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
