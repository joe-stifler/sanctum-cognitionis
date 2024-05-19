import pandas as pd
# import List from python types
from typing import List

def convert_csv_to_json(file_paths_csv: List[str]):
    for file_path_csv in file_paths_csv:
        df = pd.read_csv(file_path_csv)

        # substitute '.csv' for '.json'
        file_path_json = file_path_csv.replace(".csv", ".json")

        # save df as json
        df.to_json(file_path_json)


base_dir = "dados/vestibulares/unicamp/redacao/"
convert_csv_to_json([
    base_dir + "redacoes_comentadas_por_corretores_da_unicamp.csv",
    base_dir + "redacoes_alunos_corrigidas_por_dani_stella.csv",
])
