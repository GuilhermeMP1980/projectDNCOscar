import pandas as pd
import sqlite3
import random
from faker import Faker

# Inicializa gerador de dados fictícios
fake = Faker('pt_BR')

# Gera dados simulados
def gerar_dados(n=100):
    dados = []
    for _ in range(n):
        dados.append({
            'nome': fake.name(),
            'email': fake.email(),
            'cidade': fake.city(),
            'idade': random.randint(18, 70),
            'data_cadastro': fake.date_this_decade()
        })
    return pd.DataFrame(dados)

# Transforma os dados (exemplo: padroniza nomes)
def transformar_dados(df):
    df['nome'] = df['nome'].str.title()
    df['email'] = df['email'].str.lower()
    return df

# Carrega os dados em um banco SQLite
def carregar_dados(df, nome_banco='simulacao.db'):
    conn = sqlite3.connect(nome_banco)
    df.to_sql('usuarios', conn, if_exists='replace', index=False)
    conn.close()
    print(f"{len(df)} registros carregados em '{nome_banco}'.")

# Pipeline completo
def pipeline_simulado():
    print("Iniciando pipeline de carga simulada...")
    df = gerar_dados(100)
    df = transformar_dados(df)
    carregar_dados(df)
    print("Pipeline concluído com sucesso.")

# Executa
if __name__ == "__main__":
    pipeline_simulado()
