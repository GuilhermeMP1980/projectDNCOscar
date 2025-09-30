from pathlib import Path
import pandas as pd
import duckdb

DATA_DIR = Path("data")

ARQUIVOS = {
    "devolucao": "devolucao_2025.csv",
    "cancelamento": "cancelamento_2025.csv",
    "ajustes": "ajustes_estoque_2025.csv",
    "inventario": "inventario_062025.csv"  # exemplo de um mês
}

def carregar_csv(tipo: str) -> pd.DataFrame:
    caminho = DATA_DIR / ARQUIVOS[tipo]
    try:
        return pd.read_csv(caminho)
    except FileNotFoundError:
        print(f"Arquivo não encontrado: {caminho}")
        return pd.DataFrame()

def resumo_devolucao() -> str:
    df = carregar_csv("devolucao")
    if df.empty:
        return "Nenhuma devolução registrada."

    total = len(df)
    produtos = df["SKU"].value_counts().head(3).to_dict()
    valor_total = df["VALORDEVPRODUTO"].sum()
    return f"Foram registradas {total} devoluções, totalizando R$ {valor_total:.2f}. Principais SKUs devolvidos: {produtos}"

def resumo_cancelamento() -> str:
    df = carregar_csv("cancelamento")
    if df.empty:
        return "Nenhum cancelamento registrado."

    total = len(df)
    mais_comuns = df["IDCONDICAOPAGAMENTO"].value_counts().head(3).to_dict()
    valor_total = df["VALORBRUTO"].sum()
    return f"Foram registrados {total} cancelamentos, somando R$ {valor_total:.2f}. Condições de pagamento mais comuns: {mais_comuns}"

def resumo_ajustes() -> str:
    df = carregar_csv("ajustes")
    if df.empty:
        return "Nenhum ajuste de estoque registrado."

    total = len(df)
    tipos = df["TIPO_AJUSTE"].value_counts().to_dict()
    return f"Foram feitos {total} ajustes de estoque. Tipos mais frequentes: {tipos}"

def cruzar_dados() -> pd.DataFrame:
    df1 = carregar_csv("devolucao")
    df2 = carregar_csv("cancelamento")
    df3 = carregar_csv("ajustes")

    if df1.empty or df2.empty or df3.empty:
        print("Um ou mais arquivos estão vazios. Cruzamento parcial.")

    df1 = df1.groupby("SKU").agg({"VALORDEVPRODUTO": "sum"}).reset_index()
    df2 = df2.groupby("SKU").agg({"VALORBRUTO": "sum"}).reset_index()
    df3 = df3.groupby("SKU").agg({
        "TIPO_AJUSTE": "first",
        "QTDE_AJUSTE": "sum"
    }).reset_index()

    con = duckdb.connect()
    con.register("devolucao", df1)
    con.register("cancelamento", df2)
    con.register("ajustes", df3)

    query = """
        SELECT 
            d.SKU, 
            d.VALORDEVPRODUTO, 
            c.VALORBRUTO, 
            a.TIPO_AJUSTE, 
            a.QTDE_AJUSTE
        FROM devolucao d
        LEFT JOIN cancelamento c ON d.SKU = c.SKU
        LEFT JOIN ajustes a ON d.SKU = a.SKU
    """

    try:
        resultado = con.execute(query).fetchdf()
    except Exception as e:
        print(f"Erro ao executar consulta DuckDB: {e}")
        resultado = pd.DataFrame()

    con.close()
    return resultado
