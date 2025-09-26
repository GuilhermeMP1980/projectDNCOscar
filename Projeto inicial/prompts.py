from langchain.prompts import PromptTemplate

def get_custom_prompt():
    template = """
Você é um analista de varejo. Analise os dados abaixo e responda de forma técnica e neutra.
Pergunta: {question}
"""
    return PromptTemplate.from_template(template)
