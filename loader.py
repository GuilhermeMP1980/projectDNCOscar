import pandas as pd
import os

def load_files(folder_path):
    dfs = []
    for file in os.listdir(folder_path):
        if file.endswith("C:\\Users\\Manoel\\Documents\\DNC\\Exercícios Analista de Dados\\Desafios Analista de Dados\\data.csv"):
            df = pd.read_csv(os.path.join(folder_path, file))
        elif file.endswith("C:\\Users\\Manoel\\Documents\\DNC\\Exercícios Analista de Dados\\Desafios Analista de Dados\\Desafio PBI.xlsx"):
            df = pd.read_excel(os.path.join(folder_path, file))
        else:
            continue
        df.columns = df.columns.str.strip().str.lower()
        dfs.append(df)
    return dfs