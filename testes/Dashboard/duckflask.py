from flask import Flask, request, jsonify
from pathlib import Path
import pandas as pd
import duckdb

app = Flask(__name__)
DATA_DIR = Path("data")

ARQUIVOS = {
    "devolucao": "devolucao_2025.csv",
    "cancelamento": "cancelamento_2025.csv",
    "ajustes": "ajustes_estoque_2025.csv",
    "inventario": "inventario_062025.csv"
}

def carregar_csv(tipo: str) -> pd.DataFrame:
    caminho = DATA_DIR / ARQUIVOS.get(tipo, "")
    try:
        return pd.read_csv(caminho)
    except FileNotFoundError:
        return pd.DataFrame()

@app.route("/resumo", methods=["POST"])
def gerar_resumo():
    tipo = request.json.get("tipo")

    if tipo == "devolucao":
        df = carregar_csv("devolucao")
        if df.empty:
            return jsonify({"resposta": "Nenhuma devolução registrada."})
        total = len(df)
        produtos = df["SKU"].value_counts().head(3).to_dict()
        valor_total = df["VALORDEVPRODUTO"].sum()
        return jsonify({
            "resposta": f"Foram registradas {total} devoluções, totalizando R$ {valor_total:.2f}.",
            "principais_SKUs": produtos
        })

    elif tipo == "cancelamento":
        df = carregar_csv("cancelamento")
        if df.empty:
            return jsonify({"resposta": "Nenhum cancelamento registrado."})
        total = len(df)
        condicoes = df["IDCONDICAOPAGAMENTO"].value_counts().head(3).to_dict()
        valor_total = df["VALORBRUTO"].sum()
        return jsonify({
            "resposta": f"Foram registrados {total} cancelamentos, somando R$ {valor_total:.2f}.",
            "condicoes_mais_comuns": condicoes
        })

    elif tipo == "ajustes":
        df = carregar_csv("ajustes")
        if df.empty:
            return jsonify({"resposta": "Nenhum ajuste de estoque registrado."})
        total = len(df)
        tipos = df["TIPO_AJUSTE"].value_counts().to_dict()
        return jsonify({
            "resposta": f"Foram feitos {total} ajustes de estoque.",
            "tipos_mais_frequentes": tipos
        })

    elif tipo == "cruzar":
        df1 = carregar_csv("devolucao")
        df2 = carregar_csv("cancelamento")
        df3 = carregar_csv("ajustes")

        if df1.empty or df2.empty or df3.empty:
            return jsonify({"resposta": "Um ou mais arquivos estão vazios. Cruzamento parcial."})

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
            con.close()
            return resultado.to_json(orient="records")
        except Exception as e:
            con.close()
            return jsonify({"erro": str(e)})

    else:
        return jsonify({"erro": "Tipo inválido. Use devolucao, cancelamento, ajustes ou cruzar."})

if __name__ == "__main__":
    app.run(debug=True)
