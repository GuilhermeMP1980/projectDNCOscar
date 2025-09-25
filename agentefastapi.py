# flask_app.py
from flask import Flask, request, jsonify
from agente import app as agente_grafo, salvar_estado, session, EstadoAgente

app = Flask(__name__)

@app.route("/executar", methods=["POST"])
def executar_agente():
    entrada = request.json
    estado_inicial = {
        "llm": entrada.get("llm"),
        "tipo": entrada.get("tipo", "normal"),
        "n_estoques": entrada.get("n_estoques", 5),
        "n_skus": entrada.get("n_skus", 10),
        "pesos": {"adamic_adar": 0.5, "jaccard": 0.3, "co_ocorrencia": 0.2},
        "historico": []
    }
    final_state = agente_grafo.invoke(estado_inicial)
    salvar_estado(final_state)
    return jsonify({"resposta": final_state["resposta"], "consistencia": final_state.get("consistencia", "⚠️")})

@app.route("/sessao/<id>", methods=["GET"])
def recuperar_sessao(id):
    sessao = session.get(EstadoAgente, id)
    if not sessao:
        return jsonify({"erro": "Sessão não encontrada"}), 404
    return jsonify({"estado": sessao.estado, "consistencia": sessao.consistencia})

@app.route("/saude", methods=["GET"])
def saude():
    return jsonify({"status": "ok"})
