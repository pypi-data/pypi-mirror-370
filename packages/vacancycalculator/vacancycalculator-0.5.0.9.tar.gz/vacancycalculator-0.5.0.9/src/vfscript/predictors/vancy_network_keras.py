# neural_network_oop.py
import os, re, json, warnings, argparse
from typing import List, Dict, Tuple

os.environ["CUDA_VISIBLE_DEVICES"] = ""   # fuerza CPU
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"  # menos ruido TF
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from pathlib import Path
import pandas as pd
import numpy as np
import json
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score

class VacancyNN:
    def __init__(
        self,
        lr: float = 1e-3,
        hidden_units: Tuple[int, int] = (128, 64),
        dropout: float = 0.2,
        batch_size: int = 64,
        epochs: int = 300,
        patience: int = 20,
        seed: int = 42,
    ):
        self.lr = lr
        self.hidden_units = hidden_units
        self.dropout = dropout
        self.batch_size = batch_size
        self.epochs = epochs
        self.patience = patience
        self.seed = seed

        # Artefactos aprendidos
        self.model: tf.keras.Model = None
        self.scaler: StandardScaler = None
        self.feature_cols: List[str] = None
        self.orig_labels: np.ndarray = None
        self.label_to_idx: Dict[int, int] = None
        self.idx_to_label: Dict[int, int] = None

        np.random.seed(seed)
        tf.random.set_seed(seed)
        try:
            tf.config.set_visible_devices([], "GPU")
        except Exception:
            pass

    # ---------- Utilidades ----------
    @staticmethod
    def _load_training_json(path: str) -> pd.DataFrame:
        try:
            df = pd.read_json(path)
            if isinstance(df, pd.Series):
                df = df.to_frame().T
            if not isinstance(df, pd.DataFrame) or df.empty:
                raise ValueError
            return df
        except Exception:
            with open(path, "r", encoding="utf-8") as f:
                obj = json.load(f)
            if isinstance(obj, list):
                return pd.DataFrame(obj)
            if isinstance(obj, dict):
                for v in obj.values():
                    if isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict):
                        return pd.DataFrame(v)
                return pd.DataFrame(obj)
            raise ValueError("Formato de JSON no reconocido.")

    @staticmethod
    def _autodetect_label_col(df: pd.DataFrame) -> str:
        candidates = [
            "vacancias","vacancia","vacancys","vacancies","vacancy",
            "grupo_predicho","grupo","group","label","target","y","class","clase"
        ]
        lowmap = {c.lower(): c for c in df.columns}
        for cand in candidates:
            if cand in lowmap:
                return lowmap[cand]
        numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
        for c in numeric_cols:
            uniq = pd.unique(df[c].dropna())
            if 1 < len(uniq) <= 30:
                return c
        raise ValueError("No pude detectar la columna de etiqueta. Renómbrala a 'vacancias' o 'label'.")

    def _build_model(self, input_dim: int, n_classes: int) -> tf.keras.Model:
        model = tf.keras.Sequential([
            tf.keras.layers.Input(shape=(input_dim,)),
            tf.keras.layers.Dense(self.hidden_units[0], activation="relu"),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Dropout(self.dropout),
            tf.keras.layers.Dense(self.hidden_units[1], activation="relu"),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Dropout(self.dropout),
            tf.keras.layers.Dense(n_classes, activation="softmax"),
        ])
        model.compile(
            optimizer=tf.keras.optimizers.Adam(self.lr),
            loss="sparse_categorical_crossentropy",
            metrics=[
                tf.keras.metrics.SparseCategoricalAccuracy(name="accuracy"),
                tf.keras.metrics.SparseTopKCategoricalAccuracy(k=3, name="top3_acc"),
            ],
        )
        return model

    # ---------- API pública ----------
    def fit_from_json(self, train_json_path: str) -> None:
        df_tr = self._load_training_json(train_json_path)
        label_col = self._autodetect_label_col(df_tr)

        # Deja solo numéricas (salvo la etiqueta si no es numérica)
        drop_cols = [c for c in df_tr.columns if not pd.api.types.is_numeric_dtype(df_tr[c]) and c != label_col]
        if drop_cols:
            df_tr = df_tr.drop(columns=drop_cols, errors="ignore")

        # Convierte etiqueta a int si viene como string (e.g., "Grupo 5")
        if not pd.api.types.is_numeric_dtype(df_tr[label_col]):
            df_tr[label_col] = df_tr[label_col].apply(
                lambda x: int(re.search(r"\d+", str(x)).group(0)) if pd.notna(x) and re.search(r"\d+", str(x)) else np.nan
            )
        df_tr = df_tr.dropna(subset=[label_col])
        df_tr[label_col] = df_tr[label_col].astype(int)

        # Mapas etiqueta <-> índice
        self.orig_labels = np.sort(df_tr[label_col].unique())
        self.label_to_idx = {lab: i for i, lab in enumerate(self.orig_labels)}
        self.idx_to_label = {i: lab for lab, i in self.label_to_idx.items()}

        y = df_tr[label_col].map(self.label_to_idx).astype(int).values
        self.feature_cols = [c for c in df_tr.columns if c != label_col and pd.api.types.is_numeric_dtype(df_tr[c])]
        if not self.feature_cols:
            raise ValueError("No hay columnas numéricas de features en el JSON.")
        X = df_tr[self.feature_cols].fillna(0.0).astype(float).values

        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.15, random_state=self.seed, stratify=y
        )
        self.scaler = StandardScaler()
        X_train = self.scaler.fit_transform(X_train)
        X_val = self.scaler.transform(X_val)

        self.model = self._build_model(input_dim=X_train.shape[1], n_classes=len(self.orig_labels))
        callbacks = [
            tf.keras.callbacks.EarlyStopping(monitor="val_accuracy", mode="max", patience=self.patience, restore_best_weights=True),
            tf.keras.callbacks.ReduceLROnPlateau(monitor="val_loss", mode="min", factor=0.5, patience=8, verbose=1),
        ]
        self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=self.epochs,
            batch_size=self.batch_size,
            verbose=1,
            callbacks=callbacks
        )

    def predict_csv(self, csv_in: str, csv_out: str) -> pd.DataFrame:
        if self.model is None or self.scaler is None or self.feature_cols is None:
            raise RuntimeError("El modelo no está entrenado. Llama primero a fit_from_json().")

        df_in = pd.read_csv(csv_in)
        id_cols = [c for c in ["archivo", "file_name"] if c in df_in.columns]

        df_pred = df_in.copy()
        for col in self.feature_cols:
            if col not in df_pred.columns:
                df_pred[col] = 0.0

        X_new = df_pred[self.feature_cols].fillna(0.0).astype(float).values
        X_new = self.scaler.transform(X_new)

        probs = self.model.predict(X_new, verbose=0)  # (N, C)
        pred_idx = probs.argmax(axis=1)
        pred_labels = [self.idx_to_label[i] for i in pred_idx]

        out = pd.DataFrame()
        if id_cols:
            out[id_cols] = df_in[id_cols]
        out["pred_vacancys"] = pred_labels
        for j, lab in enumerate(self.orig_labels):
            out[f"prob_{lab}"] = probs[:, j]

        out.to_csv(csv_out, index=False, encoding="utf-8")
        print(f"✅ Predicciones guardadas en: {csv_out}")
        print(f"Total filas predichas: {len(out)}")
        counts = out["pred_vacancys"].value_counts().sort_index()
        print("Distribución por clase (vacancias):")
        for lab, cnt in counts.items():
            print(f"  {lab}: {cnt}")
        try:
            print("Vacancias totales (suma de clases):", int(np.array(pred_labels, dtype=int).sum()))
        except Exception:
            pass
        return out

    def compute_and_save_training_metrics(
        train_json="outputs/json/training_graph.json",
        artifacts_dir="artifacts_keras",
        tmp_train_csv="outputs/csv/_tmp_train_features.csv",
        pred_csv="outputs/csv/training_predictions.csv",
        cm_png="outputs/img/confusion_matrix.png",
        metrics_json="outputs/json/training_metrics.json",
        label_candidates=("vacancys","vacancies","vacancy","label","target","class","grupo","group"),
        feature_blacklist=("archivo","file","file_name","path","dump","name"),
        epochs=300,
        patience=20,
    ):
        """
        Genera predicciones sobre el set de entrenamiento y guarda:
        - PNG de matriz de confusión,
        - JSON con métricas,
        - CSV con etiquetas reales vs. predichas.
        """
        Path("outputs/img").mkdir(parents=True, exist_ok=True)
        Path("outputs/csv").mkdir(parents=True, exist_ok=True)
        Path("outputs/json").mkdir(parents=True, exist_ok=True)

        # 1) Cargar entrenamiento
        df_tr = pd.read_json(train_json) if train_json.endswith(".json") else pd.read_csv(train_json)
        # Detectar columna de etiqueta
        lab_col = None
        lowmap = {c.lower(): c for c in df_tr.columns}
        for cand in label_candidates:
            if cand in lowmap:
                lab_col = lowmap[cand]
                break
        if lab_col is None:
            raise ValueError(f"No pude detectar la columna de etiqueta. Probé: {label_candidates}")

        # Dejar solo numéricas + etiqueta
        drop_non_num = [c for c in df_tr.columns if (c != lab_col) and (not pd.api.types.is_numeric_dtype(df_tr[c]))]
        df_tr = df_tr.drop(columns=drop_non_num, errors="ignore").copy()
        if not pd.api.types.is_numeric_dtype(df_tr[lab_col]):
            df_tr[lab_col] = (
                df_tr[lab_col].astype(str).str.extract(r"(\d+)", expand=False).astype(float)
            )
        df_tr = df_tr.dropna(subset=[lab_col]).copy()
        df_tr[lab_col] = df_tr[lab_col].astype(int)

        # Features = numéricas salvo etiqueta y blacklist
        feat_cols = [c for c in df_tr.columns if c != lab_col and pd.api.types.is_numeric_dtype(df_tr[c])]
        feat_cols = [c for c in feat_cols if c not in feature_blacklist]
        if not feat_cols:
            raise ValueError("No hay columnas numéricas de features en el JSON.")

        tmp_df = df_tr[feat_cols].copy()
        if "archivo" in df_tr.columns:
            tmp_df["archivo"] = df_tr["archivo"]
        tmp_df.to_csv(tmp_train_csv, index=False)

        # 2) Entrenar modelo (usa VacancyNN ya definido en este módulo)
        nn = VacancyNN(epochs=epochs, patience=patience)
        nn.fit_from_json(train_json)
        df_pred = nn.predict_csv(tmp_train_csv, pred_csv)

        # 3) Métricas
        y_true = df_tr[lab_col].values[:len(df_pred)]
        y_pred = pd.to_numeric(df_pred["pred_vacancys"], errors="coerce").fillna(0).astype(int).values[:len(y_true)]
        labels_sorted = np.unique(np.concatenate([y_true, y_pred]))
        cm = confusion_matrix(y_true, y_pred, labels=labels_sorted)
        acc = accuracy_score(y_true, y_pred)
        report = classification_report(y_true, y_pred, labels=labels_sorted, output_dict=True, zero_division=0)

        # 4) PNG matriz de confusión
        plt.figure(figsize=(6, 5))
        im = plt.imshow(cm, interpolation="nearest")
        plt.colorbar(im, fraction=0.046, pad=0.04)
        plt.xticks(np.arange(len(labels_sorted)), labels_sorted)
        plt.yticks(np.arange(len(labels_sorted)), labels_sorted)
        plt.xlabel("Predicho"); plt.ylabel("Real")
        plt.title(f"Matriz de confusión (acc={acc:.3f})")
        for i in range(cm.shape[0]):
            for j in range(cm.shape[1]):
                plt.text(j, i, str(cm[i, j]), ha="center", va="center")
        plt.tight_layout()
        plt.savefig(cm_png, dpi=150)
        plt.close()

        # 5) Guardar JSON métricas
        out = {
            "labels": labels_sorted.tolist(),
            "accuracy": float(acc),
            "classification_report": report,
            "confusion_matrix": cm.tolist(),
            "train_json": train_json,
            "pred_csv": str(pred_csv),
        }
        with open(metrics_json, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2)
        print(f"✅ Métricas guardadas en {metrics_json}, {cm_png}")
        return out
# ====== COMPAT: artefactos pre-entrenados (shim) ======
from dataclasses import dataclass
from pathlib import Path
import json
import numpy as np
import pandas as pd

try:
    import joblib
except Exception:
    joblib = None  # avisaremos si falta
import tensorflow as tf

@dataclass
class ModelConfig:
    artifacts_dir: str = "artifacts_keras"

class VacancyClassifierKeras:
    """
    Cargador simple de artefactos Keras:
      - best_model.keras (o last_model.keras)
      - scaler.pkl
      - feature_order.json
      - (opcional) labels.json o classes.json  -> lista de labels originales
    API:
      .load_artifacts(best=True)
      .predict_csv(csv_in, csv_out, return_probs=True) -> DataFrame
    """
    def __init__(self, cfg: ModelConfig):
        self.cfg = cfg
        self.model = None
        self.scaler = None
        self.feature_order = None
        self.labels = None

    def _art(self, name: str) -> Path:
        return Path(self.cfg.artifacts_dir) / name

    def load_artifacts(self, best: bool = True):
        base = Path(self.cfg.artifacts_dir)
        if not base.exists():
            raise FileNotFoundError(f"No existe artifacts_dir: {base.as_posix()}")

        model_path = self._art("best_model.keras" if best else "last_model.keras")
        scaler_path = self._art("scaler.pkl")
        feats_path  = self._art("feature_order.json")
        labels_path = None
        for cand in ("labels.json", "classes.json", "labels.txt"):
            p = self._art(cand)
            if p.exists():
                labels_path = p; break

        if not model_path.exists():
            raise FileNotFoundError(f"Falta el modelo: {model_path.name}")
        if not feats_path.exists():
            raise FileNotFoundError(f"Falta el orden de features: {feats_path.name}")
        if joblib is None or not scaler_path.exists():
            raise FileNotFoundError(
                "Falta scaler.pkl o joblib no está instalado. Instala joblib y asegúrate de exportar el scaler."
            )

        # cargar
        self.model = tf.keras.models.load_model(model_path)
        self.scaler = joblib.load(scaler_path)
        with open(feats_path, "r", encoding="utf-8") as f:
            obj = json.load(f)
        # soporta formato {"feature_order":[...]} o lista directa
        self.feature_order = obj["feature_order"] if isinstance(obj, dict) and "feature_order" in obj else obj

        # labels opcionales
        if labels_path is not None:
            if labels_path.suffix == ".txt":
                self.labels = [int(x.strip()) for x in labels_path.read_text().splitlines() if x.strip()]
            else:
                self.labels = json.loads(labels_path.read_text())
        else:
            # si no hay archivo de labels, generamos [0..C-1] al predecir
            self.labels = None
        return self

    def predict_csv(self, csv_in: str, csv_out: str, return_probs: bool = True) -> pd.DataFrame:
        if any(x is None for x in (self.model, self.scaler, self.feature_order)):
            raise RuntimeError("Llama primero a load_artifacts().")

        df = pd.read_csv(csv_in)
        # asegurar columnas
        for col in self.feature_order:
            if col not in df.columns:
                df[col] = 0.0

        X = df[self.feature_order].fillna(0.0).astype(float).values
        X = self.scaler.transform(X)

        probs = self.model.predict(X, verbose=0)
        n, C = probs.shape

        if self.labels is None:
            labels = list(range(C))
        else:
            # recorta/expande por si hay mismatch (dejar tamaño exacto C)
            labels = list(self.labels)[:C]
            if len(labels) < C:
                labels.extend(list(range(len(labels), C)))

        pred_idx = probs.argmax(axis=1)
        pred_labels = [int(labels[i]) for i in pred_idx]

        out = pd.DataFrame()
        # si hay columna 'archivo' o 'file_name' la preservamos
        for idc in ("archivo", "file_name"):
            if idc in df.columns:
                out[idc] = df[idc]

        out["pred_vacancys"] = pred_labels
        if return_probs:
            for j, lab in enumerate(labels):
                out[f"prob_{lab}"] = probs[:, j]

        Path(csv_out).parent.mkdir(parents=True, exist_ok=True)
        out.to_csv(csv_out, index=False, encoding="utf-8")
        print(f"✅ Predicciones (artefactos) -> {csv_out} | filas={len(out)}")
        return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="VacancyNN (Keras OOP): entrena con JSON y predice CSV.")
    parser.add_argument("--train_json", default="outputs/json/training_graph.json", help="Ruta a training_graph.json")
    parser.add_argument("--csv_in", default="outputs/csv/finger_data_full_features.csv", help="CSV con filas a predecir")
    parser.add_argument("--csv_out", default="outputs/csv/results_keras_oop.csv", help="CSV de salida")
    parser.add_argument("--epochs", type=int, default=300)
    parser.add_argument("--patience", type=int, default=20)
    args = parser.parse_args()

    nn = VacancyNN(epochs=args.epochs, patience=args.patience)
    nn.fit_from_json(args.train_json)
    nn.predict_csv(args.csv_in, args.csv_out)
