import pandas as pd
import matplotlib.pyplot as plt
import os

# Lista de arquivos a serem tratados
arquivos = [
    "devolucao_2025.csv",
    "cancelamento_2025.csv",
    "ajustes_estoque_2025.csv",
    "inventario_012025.csv",
    "inventario_022025.csv",
    "inventario_032025.csv",
    "inventario_042025.csv",
    "inventario_052025.csv",
    "inventario_062025.csv"
]

# Pasta de saída
pasta_saida = "relatorios_tratados"
os.makedirs(pasta_saida, exist_ok=True)

# Função para tratar cada arquivo
def tratar_arquivo(nome_arquivo):
    print(f"\n Tratando arquivo: {nome_arquivo}")
    try:
        dados = pd.read_csv(nome_arquivo, header=None)
        print("Dados carregados com sucesso.")

        if 2 in dados.columns and 3 in dados.columns:
            dados['inicio'] = pd.to_datetime(dados[2], errors='coerce')
            dados['fim'] = pd.to_datetime(dados[3], errors='coerce')
            dados['tempo_resposta'] = dados['fim'] - dados['inicio']
            dados['tempo_resposta_segundos'] = dados['tempo_resposta'].dt.total_seconds()

            # Visualização opcional
            plt.figure(figsize=(8, 4))
            plt.hist(dados['tempo_resposta_segundos'].dropna(), bins=20, color='blue', edgecolor='black')
            plt.title(f'Distribuição do Tempo de Resposta - {nome_arquivo}')
            plt.xlabel('Tempo de Resposta (segundos)')
            plt.ylabel('Frequência')
            plt.tight_layout()
            plt.show()

            # Exportar arquivo tratado
            nome_saida = os.path.join(pasta_saida, f"tratado_{nome_arquivo}")
            dados.to_csv(nome_saida, index=False)
            print(f"Arquivo tratado exportado para: {nome_saida}")
        else:
            print("Colunas 2 e 3 não encontradas. Verifique o formato do arquivo.")
    except Exception as e:
        print(f"Erro ao tratar {nome_arquivo}: {e}")

# Loop para tratar todos os arquivos
for arquivo in arquivos:
    tratar_arquivo(arquivo)
