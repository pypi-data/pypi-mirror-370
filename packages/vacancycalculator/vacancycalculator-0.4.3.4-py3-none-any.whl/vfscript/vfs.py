# main.py

from .core import *  
from .config_loader import cargar_json_usuario
from pathlib import Path
import os
import pandas as pd
import warnings
warnings.filterwarnings('ignore', message='.*OVITO.*PyPI')

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
            




if __name__ == "__main__":
    VacancyAnalysis()
    print("Script ejecutado correctamente.")



