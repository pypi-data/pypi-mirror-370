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
