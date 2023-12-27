import sqlite3

class DataLoader:
    def __init__(self, db_path):
        self.db_path = db_path

    def connect(self):
        """Estabelece conexão com o banco de dados SQLite."""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def execute_query(self, query, params=None):
        """Executa uma consulta SQL e retorna os resultados."""
        self.connect()
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        finally:
            self.close()

    def close(self):
        """Fecha a conexão com o banco de dados."""
        self.cursor.close()
        self.conn.close()

    # Outras funções específicas para buscar dados conforme necessário
