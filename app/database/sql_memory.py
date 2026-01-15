import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import json

class SQLMemory:
    def __init__(self, db_path: str = None):
        if db_path is None:
            project_root = Path(__file__).parent.parent.parent
            db_path = project_root / "chat_memory.db"
        
        self.db_path = db_path
        self.conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.init_tables()
    
    def init_tables(self):
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_message TEXT NOT NULL,
                bot_response TEXT NOT NULL,
                tool_used TEXT,
                retrieved_context TEXT,
                metadata TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tool_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                tool_name TEXT NOT NULL,
                input_query TEXT,
                output_summary TEXT,
                success BOOLEAN
            )
        ''')
        
        self.conn.commit()
    
    # https://community.openai.com/t/how-can-i-save-each-conversation-with-my-own-ai-chatbot-trained-only-with-my-data-and-answer-my-questions/308664/8
    def save_chat(self, user_message: str, bot_response: str, 
                  tool_used: str = None, context: str = None, 
                  session_id: str = None, metadata: dict = None):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO chat_logs 
            (session_id, user_message, bot_response, tool_used, retrieved_context, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            session_id,
            user_message,
            bot_response,
            tool_used,
            context,
            json.dumps(metadata) if metadata else None
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    def log_tool_usage(self, tool_name: str, input_query: str, 
                       output_summary: str = None, success: bool = True):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO tool_usage 
            (tool_name, input_query, output_summary, success)
            VALUES (?, ?, ?, ?)
        ''', (tool_name, input_query, output_summary, success))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_chat_history(self, limit: int = 10, session_id: str = None) -> List[Dict]:
        cursor = self.conn.cursor()
        
        if session_id:
            cursor.execute('''
                SELECT * FROM chat_logs 
                WHERE session_id = ?
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (session_id, limit))
        else:
            cursor.execute('''
                SELECT * FROM chat_logs 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def get_tool_stats(self) -> Dict:
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT tool_name, COUNT(*) as count, 
                   SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as success_count
            FROM tool_usage
            GROUP BY tool_name
        ''')
        
        stats = {}
        for row in cursor.fetchall():
            stats[row['tool_name']] = {
                'total': row['count'],
                'success': row['success_count']
            }
        
        return stats
    
    def get_recent_chats_by_tool(self, tool_name: str, limit: int = 5) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM chat_logs 
            WHERE tool_used = ?
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (tool_name, limit))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def clear_old_logs(self, days: int = 30):
        cursor = self.conn.cursor()
        cursor.execute('''
            DELETE FROM chat_logs 
            WHERE timestamp < datetime('now', '-' || ? || ' days')
        ''', (days,))
        
        cursor.execute('''
            DELETE FROM tool_usage 
            WHERE timestamp < datetime('now', '-' || ? || ' days')
        ''', (days,))
        
        self.conn.commit()
        return cursor.rowcount
    
    def close(self):
        self.conn.close()

memory = SQLMemory()
