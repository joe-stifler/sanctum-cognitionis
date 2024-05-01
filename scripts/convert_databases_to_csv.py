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

convert_csv_to_json([
    "databases/unicamp/redacao/unicamp_redacoes_alunos.csv",
    "databases/unicamp/redacao/unicamp_redacoes_propostas.csv",
    "databases/unicamp/redacao/unicamp_redacoes_candidatos.csv",
])
