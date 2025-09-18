from neo4j import GraphDatabase
import os

uri = os.getenv("NEO4J_URI")
user = os.getenv("NEO4J_USER")
password = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(uri, auth=(user, password))

def salvar_em_neo4j(pergunta, resposta, fontes):
    with driver.session() as session:
        session.run("""
            MERGE (p:Pergunta {texto: $pergunta})
            MERGE (r:Resposta {texto: $resposta})
            MERGE (p)-[:RESPONDE]->(r)
        """, pergunta=pergunta, resposta=resposta)

        for fonte in fontes:
            session.run("""
                MERGE (f:Fonte {texto: $fonte})
                MERGE (r:Resposta {texto: $resposta})
                MERGE (r)-[:BASEADO_EM]->(f)
            """, fonte=fonte, resposta=resposta)
