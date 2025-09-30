from pathlib import Path
import pandas as pd
import duckdb

DATA_DIR = Path("data")

ARQUIVOS = {
    "devolucao": "devolucao_2025.csv",
    "cancelamento": "cancelamento_2025.csv",
    "ajustes": "ajustes_estoque_2025.csv"
}

def carregar_csv(tipo: str) -> pd.DataFrame:
    caminho = DATA_DIR / ARQUIVOS[tipo]
    try:
        df = pd.read_csv(caminho)
        return df
    except FileNotFoundError:
        print(f"Arquivo não encontrado: {caminho}")
        return pd.DataFrame()

def devolucao_2025() -> str:
    df = carregar_csv("devolucao")
    if df.empty:
        return "Nenhuma devolução registrada."

    total = len(df)
    produtos = df["produto"].value_counts().head(3).to_dict()
    return f"Foram registradas {total} devoluções. Principais produtos devolvidos: {produtos}"

def cancelamento_2025() -> str:
    df = carregar_csv("cancelamento")
    if df.empty:
        return "Nenhum cancelamento registrado."

    total = len(df)
    motivos = df["motivo_cancelamento"].value_counts().to_dict()
    return f"Foram registrados {total} cancelamentos. Motivos mais comuns: {motivos}"

def ajustes_estoque_2025() -> str:
    df = carregar_csv("ajustes")
    if df.empty:
        return "Nenhum ajuste de estoque registrado."

    total = len(df)
    tipos = df["tipo_ajuste"].value_counts().to_dict()
    return f"Foram feitos {total} ajustes de estoque. Tipos mais frequentes: {tipos}"

def cruzar_dados() -> pd.DataFrame:
    df1 = carregar_csv("devolucao")
    df2 = carregar_csv("cancelamento")
    df3 = carregar_csv("ajustes")

    if df1.empty or df2.empty or df3.empty:
        print("Um ou mais arquivos estão vazios. Cruzamento parcial.")

    # Agregação para evitar duplicações
    df1 = df1.groupby("produto").agg({"quantidade_vendida": "sum"}).reset_index()
    df2 = df2.groupby("produto").agg({"motivo_cancelamento": "first"}).reset_index()
    df3 = df3.groupby("produto").agg({
        "tipo_ajuste": "first",
        "quantidade_ajustada": "sum"
    }).reset_index()

    con = duckdb.connect()
    con.register("devolucao", df1)
    con.register("cancelamento", df2)
    con.register("ajustes", df3)

    query = """
        SELECT 
            d.produto, 
            d.quantidade_vendida, 
            c.motivo_cancelamento, 
            a.tipo_ajuste, 
            a.quantidade_ajustada
        FROM devolucao d
        LEFT JOIN cancelamento c ON d.produto = c.produto
        LEFT JOIN ajustes a ON d.produto = a.produto
    """

    try:
        resultado = con.execute(query).fetchdf()
    except Exception as e:
        print(f"Erro ao executar consulta DuckDB: {e}")
        resultado = pd.DataFrame()

    con.close()
    return resultado
