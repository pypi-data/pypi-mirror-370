# predict_csv_vacancies.py
from pathlib import Path
import pandas as pd
from .vancy_network_keras import ModelConfig, VacancyClassifierKeras

# Ajustá estas rutas
ARTIFACTS_DIR = "artifacts_keras"  # donde guardaste best_model.keras, scaler, feature_order.json
INPUT_CSV = "outputs/csv/finger_data_full_features.csv"  # tu CSV de entrada
OUTPUT_CSV = "outputs/csv/finger_data_predicho.csv"  # salida con predicciones

def main():
    cfg = ModelConfig(artifacts_dir=ARTIFACTS_DIR)
    clf = VacancyClassifierKeras(cfg)

    # Cargar modelo + scaler + orden de features
    clf.load_artifacts(best=True)  # usa el best_model.keras

    # Predecir el CSV completo (agrega pred_vacancys y prob_*)
    df_out = clf.predict_csv(INPUT_CSV, OUTPUT_CSV, return_probs=True)

    # Resumen rápido:
    print(f"\n✅ Guardado CSV con predicciones en: {OUTPUT_CSV}")
    print("Primeras filas con predicción:")
    print(df_out.head())

    # Si querés ver distribución de predicciones:
    if "pred_vacancys" in df_out.columns:
        print("\nConteo por clase predicha:")
        print(df_out["pred_vacancys"].value_counts().sort_index())

if __name__ == "__main__":
    main()