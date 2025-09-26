import pandas as pd, os

def consolidate_data():
    path = "data"
    dev = pd.read_csv(f"{path}/devolucao.csv")
    canc = pd.read_csv(f"{path}/cancelamento.csv")
    ajus = pd.read_csv(f"{path}/ajustes_estoque.csv")

    for df in [dev, canc, ajus]:
        df.columns = df.columns.str.lower().str.replace(" ", "_")

    df = canc.merge(ajus, on="produto_id", how="outer")
    df = df.merge(dev, on="produto_id", how="outer")
    df.to_csv(f"{path}/consolidado.csv", index=False)
    return df
