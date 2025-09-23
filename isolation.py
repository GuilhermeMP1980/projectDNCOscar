from sklearn.ensemble import IsolationForest
import pandas as pd
import numpy as np

# Simulação de dados: 100 registros normais + 5 anômalos
rng = np.random.RandomState(42)
dados_normais = rng.normal(loc=0, scale=1, size=(100, 2))
dados_anomalos = rng.uniform(low=-6, high=6, size=(5, 2))
dados = np.vstack([dados_normais, dados_anomalos])
df = pd.DataFrame(dados, columns=["feature_1", "feature_2"])

# Treinamento do modelo
modelo = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
modelo.fit(df)

# Previsão: -1 = anômalo, 1 = normal
df["anomaly"] = modelo.predict(df)

# Visualização dos resultados
print(df[df["anomaly"] == -1])  # Exibe os registros detectados como anômalos
