# projectDNCOscar
Projeto de criação de uma iA Generativa

#  projetoDNCOscar  
Sistema de Agentes Inteligentes com LangGraph, FastAPI, Streamlit e PostgreSQL

Este projeto integra agentes inteligentes com controle de estado, consolidação de dados operacionais, detecção de fraude, autenticação segura e visualização interativa. A solução é modular, escalável e pronta para produção com infraestrutura Docker.

---

## Funcionalidades

- 🔐 Autenticação de usuários com JWT
- 🧠 Execução de agentes inteligentes com LangGraph
- 📥 Consolidação de dados operacionais (estoque, devoluções, cancelamentos)
- 📊 Detecção de padrões suspeitos e possíveis fraudes
- 🌐 API REST com FastAPI
- 🖥️ Interface interativa com Streamlit
- 📈 Visualização de insights em gráficos e métricas
- 🧪 Testes unitários, de integração e end-to-end
- 🐳 Infraestrutura com Docker e PostgreSQL

---

## Estrutura do Projeto


---

## 📊 Relatórios Técnicos

### 1. Relatório de Desenvolvimento Backend
- Implementação de API REST com FastAPI
- Execução de agentes com LangGraph
- Persistência de sessões e usuários com PostgreSQL

### 2. Relatório de Desenvolvimento Frontend
- Interface com navegação guiada via Streamlit
- Autenticação, execução e consulta de sessões
- Visualização de dados consolidados e gráficos interativos

### 3. Relatório de Usabilidade
- Interface intuitiva com menus laterais e feedback visual
- Separação clara de funcionalidades
- Responsividade e acessibilidade para usuários não técnicos

### 4. Relatório de Detecção de Fraude
- Identificação de padrões suspeitos (valores altos, quantidades excessivas)
- Visualização analítica com métricas e gráficos
- Testes end-to-end simulando o fluxo completo

---

## 🧪 Testes Automatizados

| Tipo de Teste       | Arquivo                | Objetivo                                 |
|---------------------|------------------------|------------------------------------------|
| Unitário            | `test_agente.py`       | Valida execução do agente LangGraph      |
| API                 | `test_api.py`          | Testa autenticação e endpoints REST      |
| Banco de Dados      | `test_db.py`           | Verifica persistência de dados           |
| Integração          | `test_integracao.py`   | Simula fluxo completo entre módulos      |
| End-to-End (Fraude) | `test_e2e_fraude.py`   | Detecta padrões suspeitos e valida sessão|

---

## Referências Bibliográficas

- LangGraph Documentation – [docs.langgraph.dev](https://docs.langgraph.dev)  
- FastAPI Documentation – [fastapi.tiangolo.com](https://fastapi.tiangolo.com)  
- Streamlit Documentation – [docs.streamlit.io](https://docs.streamlit.io)  
- OWASP Top 10 – [owasp.org](https://owasp.org/www-project-top-ten)  
- Plotly Python – [plotly.com/python](https://plotly.com/python)  
- pytest Documentation – [docs.pytest.org](https://docs.pytest.org)

---

## Como Executar

1. Clone o repositório:

```bash
git clone https://github.com/seu-usuario/projetoDNCOscar.git
cd projetoDNCOscar
