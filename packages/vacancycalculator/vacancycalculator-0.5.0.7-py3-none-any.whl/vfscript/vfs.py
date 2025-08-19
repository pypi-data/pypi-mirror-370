# main.py

from .core import *  
from .config_loader import cargar_json_usuario
from pathlib import Path
import os
import pandas as pd
import warnings
warnings.filterwarnings('ignore', message='.*OVITO.*PyPI')



def _predict_vacancies_with_nn(
    train_json="outputs/json/training_graph.json",
    csv_in="outputs/csv/finger_data_full_features.csv",
    out_csv="outputs/csv/results_keras_oop.csv",
    artifacts_dir="artifacts_keras",
    epochs=300,
    patience=20,
):
    """
    Predice el número de vacancias usando:
      1) Un modelo Keras preentrenado si existen artefactos en artifacts_dir/
      2) Sino, entrena al vuelo con VacancyNN (OOP) y luego predice.

    Devuelve: (df_pred, total_vacancies_int)
    """
    # Opción 1: usar artefactos ya entrenados (si existen y tenemos la clase disponible)
    best_model = Path(artifacts_dir) / "best_model.keras"
    if best_model.exists() and (ModelConfig is not None) and (VacancyClassifierKeras is not None):
        cfg = ModelConfig(artifacts_dir=str(artifacts_dir))
        clf = VacancyClassifierKeras(cfg)
        clf.load_artifacts(best=True)  # levanta best_model.keras, scaler, orden de features
        df_out = clf.predict_csv(csv_in, out_csv, return_probs=True)  # agrega 'pred_vacancys' y 'prob_*'
        try:
            total_vac = int(df_out["pred_vacancys"].astype(int).sum())
        except Exception:
            total_vac = None
        print(f"✅ Predicciones (artefactos) en: {out_csv}")
        if total_vac is not None:
            print(f"🔢 Vacancias totales (pred): {total_vac}")
        return df_out, total_vac

    # Opción 2: entrenar al vuelo con la clase OOP
    print("[INFO] No se hallaron artefactos entrenados. Entrenando modelo OOP Keras...")
    nn = VacancyNN(epochs=epochs, patience=patience)
    nn.fit_from_json(train_json)                       # entrena con training_graph.json
    df_out = nn.predict_csv(csv_in, out_csv)           # predice sobre full_features
    try:
        total_vac = int(df_out["pred_vacancys"].astype(int).sum())
    except Exception:
        total_vac = None
    print(f"✅ Predicciones (entrenado al vuelo) en: {out_csv}")
    if total_vac is not None:
        print(f"🔢 Vacancias totales (pred): {total_vac}")
    return df_out, total_vac

def VacancyAnalysis():
    
    base = "outputs"
    for sub in ("csv", "dump", "json"):
        os.makedirs(os.path.join(base, sub), exist_ok=True)

    


    
    CONFIG = cargar_json_usuario()
    
    if "CONFIG" not in CONFIG or not isinstance(CONFIG["CONFIG"], list) or len(CONFIG["CONFIG"]) == 0:
        raise ValueError("input_params.json debe contener una lista 'CONFIG' con al menos un objeto.")

    configuracion = CONFIG["CONFIG"][0]
    raw_defects = configuracion.get('defect', [])  
    defect_files = raw_defects if isinstance(raw_defects, list) else [raw_defects]  
    
    
    
    
    cs_out_dir = Path("inputs")
    cs_generator = CrystalStructureGenerator(configuracion, cs_out_dir)
    dump_path = cs_generator.generate()
    #print(f"Estructura relajada generada en: {dump_path}")
    if configuracion['training']:
        gen = AtomicGraphGenerator()
        gen.run()   
    
    for FILE in defect_files:



        analyzer = DeformationAnalyzer(FILE, configuracion['generate_relax'][0], configuracion['generate_relax'][5], threshold=0.02)
        delta = analyzer.compute_metric()
        method = analyzer.select_method()

        if method == 'geometric' and configuracion['geometric_method']:
           
            vac_analyzer = WSMet(
                defect_dump_path=FILE,
                lattice_type=configuracion['generate_relax'][0],
                element=configuracion['generate_relax'][5],
                tolerance=0.5
            )
            vacancies = vac_analyzer.run()
        elif method == 'ml' or configuracion['geometric_method']==False :
            vac_analyzer = WSMet(
                defect_dump_path=FILE,
                lattice_type=configuracion['generate_relax'][0],
                element=configuracion['generate_relax'][5],
                tolerance=0.5
            )
            vac_analyzer.generate_perfect_atoms()
            
            processor = ClusterProcessor(FILE)
            processor.run()
            separator = KeyFilesSeparator(configuracion, os.path.join("outputs/json", "clusters.json"))
            separator.run()

            clave_criticos = ClusterDumpProcessor.cargar_lista_archivos_criticos("outputs/json/key_archivos.json")
            for archivo in clave_criticos:
                try:
                    dump_proc = ClusterDumpProcessor(archivo, decimals=5)
                    dump_proc.load_data()
                    dump_proc.process_clusters()
                    dump_proc.export_updated_file(f"{archivo}_actualizado.txt")
                except Exception as e:
                    print(f"Error procesando {archivo}: {e}")

            
            lista_criticos = ClusterDumpProcessor.cargar_lista_archivos_criticos("outputs/json/key_archivos.json")
            for archivo in lista_criticos:
                machine_proc = ClusterProcessorMachine(archivo)  
                machine_proc.process_clusters()
                machine_proc.export_updated_file()


            # 5. Separar archivos finales vs críticos
            separator = KeyFilesSeparator(configuracion, os.path.join("outputs/json", "clusters.json"))
            separator.run()

            # 6. Generar nuevos dumps por cluster
            export_list = ExportClusterList("outputs/json/key_archivos.json")
            export_list.process_files()

            # 7. Calcular superficies de dump
            surf_proc = SurfaceProcessor(configuracion)
            surf_proc.process_all_files()
            surf_proc.export_results()



            exporter = ClusterFeatureExporter("outputs/json/key_archivos.json")
            exporter.export()


            # ------------------------------------------------------------------------
            # 8. Entrenar y clasificar defectos con el nuevo modelo ensemble
            if configuracion['geometric_method']:
                analyzer = WSMet("inputs/void_15.dump", "bcc", "Fe", tolerance=0.5)
                vac_positions = analyzer.run()
            # Instancia y entrena el modelo
            clf = ImprovedVacancyClassifier(json_path='outputs/json/training_graph.json')
            clf.train()  
            # → ya imprime mejores parámetros y reporte de clasificación

            # Clasifica tu CSV de defectos (añade columna 'grupo_predicho')
            df_clasif = clf.classify_csv(
                csv_path='outputs/csv/defect_data.csv',
                output_path='outputs/csv/finger_data_clasificado.csv'
            )
    
            df_pred = clf.classify_csv(
                csv_path='outputs/csv/finger_data_clasificado.csv',
                output_path='outputs/csv/finger_data_predicha.csv'
            )

            assigner = FingerprintVacancyAssigner(
                base_csv_path="outputs/csv/finger_data.csv",
                query_csv_path="outputs/csv/finger_key_files.csv",
                weight_N=1
            )
            df_result = assigner.assign()
            df_result.to_csv("outputs/csv/finger_key_files_clasificado.csv", index=False)

            df_key = pd.read_csv("outputs/csv/finger_key_files.csv")
            df_cls = pd.read_csv("outputs/csv/defect_data.csv")

            df_full = df_cls.merge(df_key, left_on="archivo", right_on="file_name", how="left")
            df_full.to_csv("outputs/csv/finger_data_full_features.csv", index=False)
            



     
            try:
                _, total_vac = _predict_vacancies_with_nn(
                    train_json="outputs/json/training_graph.json",
                    csv_in="outputs/csv/finger_data_full_features.csv",
                    out_csv="outputs/csv/results_keras_oop.csv",
                    artifacts_dir="artifacts_keras",  # si existe, usa modelo preentrenado
                    epochs=300,
                    patience=20,
                )
                if total_vac is not None:
                    print(f"\n=== RESULTADO NN: Vacancias totales predichas = {total_vac} ===")
                else:
                    print("\n[WARN] No se pudo calcular la suma total (columna 'pred_vacancys' no entera).")
            except Exception as e:
                print(f"[ERROR] Falló la predicción NN de vacancias: {e}")

if __name__ == "__main__":
    VacancyAnalysis()
    print("Script ejecutado correctamente.")



