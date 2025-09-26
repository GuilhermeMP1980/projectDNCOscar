import pandas as pd, duckdb

def load_and_clean_data():
    for name in ['estoque', 'devolucoes', 'inventario']:
        df = pd.read_csv(f'data/{name}.csv')
        df.columns = df.columns.str.lower().str.replace(' ', '_')
        con = duckdb.connect('retail.duckdb')
        con.execute(f"CREATE OR REPLACE TABLE {name} AS SELECT * FROM df")
        con.close()
