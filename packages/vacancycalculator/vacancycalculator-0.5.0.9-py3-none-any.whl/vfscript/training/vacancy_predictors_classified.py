import json
import pandas as pd
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import joblib
import os

class VacancyModelTrainer:
    def __init__(self, json_path, target='vacancys'):
        self.json_path = json_path
        self.target = target
        self.features = ['surface_area', 'filled_volume', 'cluster_size']
        self.models = {}
        self.data = None
        self.df = None

    def load_data(self):
        with open(self.json_path, 'r') as f:
            self.data = json.load(f)
        self.df = pd.DataFrame(self.data)
        self.df['grupo'] = self.df['vacancys'].apply(self._clasificar_grupo)
        print("✅ Datos cargados y clasificados.")

    def _clasificar_grupo(self, vac):
        if 1 <= vac <= 3:
            return "1-3"
        elif 4 <= vac <= 6:
            return "4-6"
        elif 7 <= vac <= 9:
            return "7-9"
        else:
            return "10+"

    def train_all_models(self):
        for grupo in ['1-3', '4-6', '7-9', '10+']:
            df_grupo = self.df[self.df['grupo'] == grupo]

            if df_grupo.shape[0] < 3:
                print(f"⚠️ No hay suficientes datos para el grupo {grupo}, se omite.")
                continue

            X = df_grupo[self.features]
            y = df_grupo[self.target]

            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            model = XGBRegressor(n_estimators=100, max_depth=4, learning_rate=0.1)
            model.fit(X_train, y_train)

            y_pred = model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            print(f"✅ Modelo grupo {grupo} entrenado. MSE: {mse:.4f}")

            self.models[grupo] = model
            joblib.dump(model, f"xgb_model_{grupo}.pkl")

        print("✔️ Todos los modelos entrenados y guardados.")

    def predict(self, grupo, sample_dict):
        model_path = f"xgb_model_{grupo}.pkl"
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"❌ Modelo para el grupo {grupo} no encontrado.")
        
        model = joblib.load(model_path)
        df_sample = pd.DataFrame([sample_dict])
        prediction = model.predict(df_sample)
        print(f"🔮 Predicción para grupo {grupo}: {prediction[0]}")
        return prediction[0]

    def predict_from_csv(self, csv_path):
        df = pd.read_csv(csv_path)

        if 'grupo_predicho' not in df.columns:
            raise ValueError("❌ El CSV debe tener una columna 'grupo_predicho' para saber qué modelo usar por fila.")
        
        if not all(col in df.columns for col in self.features):
            raise ValueError(f"❌ El CSV debe contener las columnas: {self.features}")

        predictions = []
        for idx, row in df.iterrows():
            grupo = row['grupo_predicho']
            model_path = f"xgb_model_{grupo}.pkl"

            if not os.path.exists(model_path):
                raise FileNotFoundError(f"❌ Modelo para el grupo '{grupo}' no encontrado en: {model_path}")
            
            model = joblib.load(model_path)
            X_row = row[self.features].values.reshape(1, -1)
            pred = model.predict(X_row)[0]
            predictions.append(pred)

        df['predicted_vacancy'] = predictions
        print("🔮 Predicciones completadas:")
        print(df[['grupo_predicho', 'predicted_vacancy']])
        return df

