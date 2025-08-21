import os
import csv
import numpy as np
import json

from vfscript.training.utils import resolve_input_params_path

# \u2193\u2193\u2193 NUEVO: ConvexHull para \u00e1rea/volumen \u2193\u2193\u2193
try:
    from scipy.spatial import ConvexHull, QhullError
    _HAS_SCIPY = True
except Exception:
    _HAS_SCIPY = False
    ConvexHull = None
    QhullError = Exception


class DumpProcessor:
    """
    Se encarga de leer un archivo .dump de LAMMPS, desplazar las coordenadas
    al centro de masa y devolver las normas de las coordenadas desplazadas.

    Adem\u00e1s, calcula el \u00e1rea de superficie y el volumen del casco convexo
    (Convex Hull) usando las coordenadas at\u00f3micas.
    """
    def __init__(self, dump_path: str):
        self.dump_path = dump_path
        self.coords_originales = None      # (N, 3)
        self.center_of_mass = None         # (3,)
        self.coords_trasladadas = None     # (N, 3)
        self.norms = None                  # (N,)
        # \u2193\u2193\u2193 NUEVO \u2193\u2193\u2193
        self.hull_surface_area = np.nan
        self.hull_volume = np.nan

    def read_and_translate(self):
        """
        Lee el archivo .dump y traslada las coordenadas de modo que el
        centro de masa quede en el origen. Guarda en los atributos:
          - self.coords_originales
          - self.center_of_mass
          - self.coords_trasladadas
        """
        if not os.path.isfile(self.dump_path):
            raise FileNotFoundError(f"No se encontr\u00f3 el archivo: {self.dump_path}")

        coords = []
        with open(self.dump_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Buscar la l\u00ednea "ITEM: ATOMS"
        start_index = None
        for i, line in enumerate(lines):
            if line.strip().startswith("ITEM: ATOMS"):
                start_index = i + 1
                break

        if start_index is None:
            raise ValueError(f"No se encontr\u00f3 'ITEM: ATOMS' en {self.dump_path}")

        # Parsear coordenadas (asumiendo columnas id type x y z ...)
        for line in lines[start_index:]:
            parts = line.split()
            if not parts:
                continue
            if parts[0] == "ITEM:":
                break  # Llegamos al pr\u00f3ximo bloque
            if len(parts) < 5:
                continue
            try:
                x, y, z = float(parts[2]), float(parts[3]), float(parts[4])
                coords.append((x, y, z))
            except ValueError:
                # L\u00ednea no num\u00e9rica/encabezado residual
                continue

        if not coords:
            raise ValueError(
                f"No se hallaron coordenadas v\u00e1lidas tras 'ITEM: ATOMS' en {self.dump_path}"
            )

        self.coords_originales = np.array(coords, dtype=float)
        com = tuple(self.coords_originales.mean(axis=0))
        self.center_of_mass = com

        # Traslada al COM (invariante para \u00e1rea/volumen, pero mejora estabilidad num\u00e9rica)
        self.coords_trasladadas = self.coords_originales - np.array(com)

    def compute_norms(self):
        """
        Calcula la norma de cada vector de coordenadas trasladadas.
        Debe llamarse despu\u00e9s de read_and_translate().
        Guarda el resultado ordenado en self.norms (numpy array de tama\u00f1o N).
        """
        if self.coords_trasladadas is None:
            raise RuntimeError("Debes llamar primero a read_and_translate() antes de compute_norms().")

        self.norms = np.linalg.norm(self.coords_trasladadas, axis=1)
        self.norms = np.sort(self.norms)

    # \u2193\u2193\u2193 NUEVO: c\u00e1lculo de Convex Hull \u2193\u2193\u2193
    def compute_convex_hull(self, use_translated: bool = True):
        """
        Calcula el casco convexo en 3D y guarda:
            - self.hull_surface_area (\u00c1^2)
            - self.hull_volume (\u00c1^3)
        Si hay muy pocos puntos o son coplanares/colineales, deja NaN.
        """
        if not _HAS_SCIPY:
            raise ImportError(
                "Se requiere SciPy para calcular ConvexHull (pip install scipy)."
            )

        pts = self.coords_trasladadas if use_translated else self.coords_originales
        if pts is None:
            raise RuntimeError("Debes ejecutar read_and_translate() antes de compute_convex_hull().")

        # Necesitamos >= 4 puntos no coplanares para volumen > 0
        if pts.shape[0] < 4:
            self.hull_surface_area = np.nan
            self.hull_volume = np.nan
            return

        # Heur\u00edstica r\u00e1pida para detectar degeneraci\u00f3n geom\u00e9trica
        # (si el rango de la matriz es < 3, los puntos est\u00e1n en un subespacio)
        rank = np.linalg.matrix_rank(pts - pts.mean(axis=0))
        if rank < 3:
            self.hull_surface_area = np.nan
            self.hull_volume = np.nan
            return

        try:
            hull = ConvexHull(pts)
            # En 3D: hull.area = \u00e1rea superficial, hull.volume = volumen
            self.hull_surface_area = float(hull.area)
            self.hull_volume = float(hull.volume)
        except QhullError:
            # Datos degenerados o num\u00e9ricamente problem\u00e1ticos
            self.hull_surface_area = np.nan
            self.hull_volume = np.nan


class StatisticsCalculator:
    """
    Calcula un conjunto de estad\u00edsticas (min, max, mean, std, skewness, kurtosis,
    percentiles, IQR, histograma normalizado) sobre un array 1D de valores.
    """
    @staticmethod
    def compute_statistics(arr: np.ndarray) -> dict:
        stats = {}
        N = len(arr)
        stats['N'] = N

        if N == 0:
            stats.update({
                'mean': np.nan, 'std': np.nan,
                'skewness': np.nan, 'kurtosis': np.nan,
                'Q1': np.nan, 'median': np.nan, 'Q3': np.nan, 'IQR': np.nan
            })
            for i in range(1, 11):
                stats[f'hist_bin_{i}'] = 0.0
            return stats

        min_val = float(np.min(arr))
        max_val = float(np.max(arr))
        mean_val = float(np.mean(arr))
        std_val = float(np.std(arr, ddof=0))

        # Momentos adimensionales (si std > 0)
        skew_val = float(np.mean(((arr - mean_val) / std_val) ** 3)) if std_val > 0 else 0.0
        kurt_val = float(np.mean(((arr - mean_val) / std_val) ** 4) - 3) if std_val > 0 else 0.0

        Q1 = float(np.percentile(arr, 25))
        med = float(np.percentile(arr, 50))
        Q3 = float(np.percentile(arr, 75))
        IQR = Q3 - Q1

        # Histograma normalizado (10 bins en [min, max])
        hist_counts, _ = np.histogram(arr, bins=10, range=(min_val, max_val))
        hist_norm = hist_counts / N

        stats.update({
            'mean': mean_val,
            'std': std_val,
            'skewness': skew_val,
            'kurtosis': kurt_val,
            'Q1': Q1,
            'median': med,
            'Q3': Q3,
            'IQR': IQR
        })
        for i, h in enumerate(hist_norm, start=1):
            stats[f'hist_bin_{i}'] = float(h)

        return stats


class FeatureExporter:
    """
    Recorre una lista de archivos .dump, utiliza DumpProcessor para
    extraer normas y StatisticsCalculator para obtener estad\u00edsticas,
    y finalmente escribe un CSV con todas las caracter\u00edsticas.

    Adem\u00e1s, agrega dos columnas: hull_surface_area y hull_volume.
    """
    def __init__(self, dump_paths: list[str] = None, output_csv: str = "outputs/csv/finger_data.csv"):
        self.output_csv = output_csv

        # Cargar par\u00e1metros desde input_params.json
        json_params_path = resolve_input_params_path("input_params.json")
        with open(json_params_path, "r", encoding="utf-8") as f:
            all_params = json.load(f)

        if "CONFIG" not in all_params or not isinstance(all_params["CONFIG"], list) or len(all_params["CONFIG"]) == 0:
            raise KeyError("input_params.json debe contener la clave 'CONFIG' como lista no vac\u00eda.")

        config = all_params["CONFIG"][0]
        self.max_training_file_index = config["training_file_index"]

        # Si dump_paths no se pasa, lo generamos autom\u00e1ticamente
        if dump_paths is None:
            self.dump_paths = [
                f"outputs/dump/vacancy_{i}_training.dump"
                for i in range(1, self.max_training_file_index + 1)
            ]
        else:
            self.dump_paths = dump_paths

    def export(self):
        # Cabecera con primer campo renombrado a 'vacancys'
        header = [
            "vacancys", "N", "mean", "std",
            "skewness", "kurtosis", "Q1", "median", "Q3", "IQR"
        ] + [f"hist_bin_{i}" for i in range(1, 11)] \
          + ["hull_surface_area", "hull_volume"]  # \u2193\u2193\u2193 NUEVO

        os.makedirs(os.path.dirname(self.output_csv), exist_ok=True)
        with open(self.output_csv, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(header)

            # it arranca en 1 y cuenta hasta max_training_file_index
            it = 1
            for dump_path in self.dump_paths:
                if not os.path.isfile(dump_path):
                    print(f"\u26a0\ufe0f No se encontr\u00f3 {dump_path}, se salta.")
                    continue

                processor = DumpProcessor(dump_path)
                try:
                    processor.read_and_translate()
                    processor.compute_norms()
                    # \u2193\u2193\u2193 NUEVO: calcular hull
                    processor.compute_convex_hull(use_translated=True)
                except Exception as e:
                    print(f"\u274c Error en {dump_path}: {e}")
                    continue

                stats = StatisticsCalculator.compute_statistics(processor.norms)

                # Preparo la fila: primer elemento = n\u00famero de vacancias (it)
                row = [
                    it,
                    stats['N'],
                    stats['mean'],
                    stats['std'],
                    stats['skewness'],
                    stats['kurtosis'],
                    stats['Q1'],
                    stats['median'],
                    stats['Q3'],
                    stats['IQR']
                ] + [stats[f"hist_bin_{i}"] for i in range(1, 11)] \
                  + [processor.hull_surface_area, processor.hull_volume]

                writer.writerow(row)

                # Incremento y reseteo si supero el m\u00e1ximo
                it += 1
                if it > self.max_training_file_index:
                    it = 1

        print(f"Se gener\u00f3 el CSV con caracter\u00edsticas en: {self.output_csv}")


# if __name__ == "__main__":
#     exporter = FeatureExporter()
#     exporter.export()
