# Projeto6/src/data_loader.py

import sqlite3
from .models.message import Message

class DataLoader:
    def __init__(self, db_path):
        self.db_path = db_path

    def load_messages(self, conversation_id):
        query = """
                SELECT * 
                FROM message_view 
                WHERE chat_row_id = ?
                """
        rows = self.execute_query(query, (conversation_id,))
        return [Message.from_row(row) for row in rows]

    def execute_query(self, query, params):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
