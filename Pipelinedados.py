#Extração de dados
import pandas as pd
df = pd.read_csv('dados.csv')

#Transformação e limpeza de Dados
df = df.drop('coluna_irrelevante', axis=1)
df = df.fillna(df.mean())
df_agrupado = df.groupby('categoria').sum()

#Carregamento de Dados
from sqlalchemy import create_engine
engine = create_engine('mysql+pymysql://usuario:senha@host/db')
df.to_sql('tabela_destino', con=engine, if_exists='replace')
