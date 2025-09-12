import pandas as pd
import os

DATA_DIR = "../data"

def load_csv_files():
    """Carrega os arquivos CSV do diretório de dados."""
    devolucao = pd.read_csv(os.path.join(DATA_DIR, "devolucao.csv"))
    cancelamento = pd.read_csv(os.path.join(DATA_DIR, "cancelamento.csv"))
    ajustes_estoque = pd.read_csv(os.path.join(DATA_DIR, "ajustes_estoque.csv"))
    return estoque, devolucoes, inventario

def normalize_dataframe(df):
    """Padroniza colunas e tipos de dados."""
    df.columns = df.columns.str.lower().str.strip().str.replace(" ", "_")
    return df

def consolidate_data(devolucao, cancelamento, ajustes_estoque):
    """Mescla os dados em um único DataFrame consolidado."""
    df_devolucao = normalize_dataframe(devolucao)
    df_cancelamento = normalize_dataframe(cancelamento)
    df_ajustes_estoque = normalize_dataframe(ajustes_estoque)

    # Mescla por produto_id
    df = df_estoque.merge(df_inventario, on="produto_id", how="outer")
    df = df.merge(df_devolucoes, on="produto_id", how="outer")
    return df

def save_consolidated(df, filename="consolidado.csv"):
    """Salva o DataFrame consolidado em CSV."""
    output_path = os.path.join(DATA_DIR, filename)
    df.to_csv(output_path, index=False)
    print(f"Arquivo salvo em: {output_path}")

if __name__ == "__main__":
    estoque, devolucoes, inventario = load_csv_files()
    consolidado = consolidate_data(devolucao, cancelamento, ajustes_estoque)
    save_consolidated(consolidado)