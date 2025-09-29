import pandas as pd
import os

# Lista de arquivos e seus tipos
arquivos = {
    "devolucao_2025.csv": "devolucao",
    "cancelamento_2025.csv": "cancelamento",
    "ajustes_estoque_2025.csv": "ajustes",
    "inventario_012025.csv": "inventario",
    "inventario_022025.csv": "inventario",
    "inventario_032025.csv": "inventario",
    "inventario_042025.csv": "inventario",
    "inventario_052025.csv": "inventario",
    "inventario_062025.csv": "inventario"
}

# Função para gerar perguntas/respostas
def gerar_perguntas(tipo, df):
    perguntas_respostas = []

    if tipo == "inventario":
        if "LOJA" in df.columns and "VALOR" in df.columns:
            total_por_loja = df.groupby("LOJA")["VALOR"].sum()
            for loja, valor in total_por_loja.items():
                perguntas_respostas.append((f"Qual foi o valor total movimentado na loja {loja}?", f"R$ {valor:.2f}"))

        if "SKU" in df.columns and "QTDEMOVIMENTADA" in df.columns:
            mais_movimentado = df.groupby("SKU")["QTDEMOVIMENTADA"].sum().sort_values(ascending=False).head(1)
            sku = mais_movimentado.index[0]
            qtd = mais_movimentado.iloc[0]
            perguntas_respostas.append((f"Qual SKU teve maior movimentação?", f"{sku} com {qtd} unidades"))

    elif tipo == "devolucao":
        if "LOJA" in df.columns and "VALORDEVPRODUTO" in df.columns:
            total_dev = df.groupby("LOJA")["VALORDEVPRODUTO"].sum()
            for loja, valor in total_dev.items():
                perguntas_respostas.append((f"Qual foi o valor total devolvido na loja {loja}?", f"R$ {valor:.2f}"))

        if "SKU" in df.columns:
            mais_devolvido = df["SKU"].value_counts().head(1)
            sku = mais_devolvido.index[0]
            qtd = mais_devolvido.iloc[0]
            perguntas_respostas.append((f"Qual SKU teve mais devoluções?", f"{sku} com {qtd} devoluções"))

    elif tipo == "cancelamento":
        if "LOJA" in df.columns:
            cancelamentos = df["LOJA"].value_counts()
            for loja, qtd in cancelamentos.items():
                perguntas_respostas.append((f"Quantos cancelamentos ocorreram na loja {loja}?", f"{qtd} cancelamentos"))

        if "VALORBRUTO" in df.columns:
            total_cancelado = df["VALORBRUTO"].sum()
            perguntas_respostas.append(("Qual foi o valor bruto total cancelado?", f"R$ {total_cancelado:.2f}"))

    elif tipo == "ajustes":
        if "TIPO_AJUSTE" in df.columns:
            tipo_mais_comum = df["TIPO_AJUSTE"].value_counts().head(1)
            tipo = tipo_mais_comum.index[0]
            qtd = tipo_mais_comum.iloc[0]
            perguntas_respostas.append((f"Qual foi o tipo de ajuste mais comum?", f"{tipo} com {qtd} ocorrências"))

    return perguntas_respostas

# Loop pelos arquivos
for nome_arquivo, tipo in arquivos.items():
    try:
        df = pd.read_csv(nome_arquivo)
        perguntas = gerar_perguntas(tipo, df)
        print(f"\n📄 Perguntas geradas a partir de {nome_arquivo}:")
        for p, r in perguntas:
            print(f" Pergunta: {p}\n Resposta: {r}\n")
    except Exception as e:
        print(f" Erro ao processar {nome_arquivo}: {e}")
