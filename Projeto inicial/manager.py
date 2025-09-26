from rag.agent import create_rag_agent
from indexing.vector_store import index_data

class SessionManager:
    def __init__(self):
        self.sessions = {}

    def create_session(self, user_id, dfs):
        vectorstore = index_data(dfs)
        agent = create_rag_agent(vectorstore)
        self.sessions[user_id] = agent

    def get_agent(self, user_id):
        return self.sessions.get(user_id)
