import pandas as pd
from sqlalchemy import create_engine

# Configuração da conexão com PostgreSQL
DB_USER = "seu_usuario"
DB_PASS = "sua_senha"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "retail_db"

engine = create_engine(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# Função para carregar e enviar para o banco
def ingest_csv_to_postgres(file_path, table_name):
    df = pd.read_csv(file_path)
    
    # Normalização básica (exemplo)
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
    
    # Envia para o PostgreSQL
    df.to_sql(table_name, engine, if_exists='append', index=False)
    print(f"Tabela '{table_name}' criada com sucesso!")

# Exemplo de uso
if __name__ == "__main__":
    ingest_csv_to_postgres("../data/devolucao.csv", "Devolução")
    ingest_csv_to_postgres("../data/cancelamento.csv", "Cancelamento")
    ingest_csv_to_postgres("../data/ajustes_estoque.csv", "Ajustes")

def carregar_e_normalizar(path):
    df = pd.read_csv(path)
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
    df.dropna(how="all", inplace=True)
    return df
