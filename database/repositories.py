import sqlite3
from typing import Optional, Dict, Any, List
from database.connection import get_db_connection


# взаимодействие с базами данных через статичные функции

class UserRepository:
    @staticmethod
    def create_user(username: str, email: str, password: str) -> int:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                (username, email, password)
            )
            user_id = cursor.lastrowid
            conn.commit()
            return user_id

    @staticmethod
    def get_user_by_credentials(email: str, password: str) -> Optional[tuple]:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, username, email FROM users WHERE email = ? AND password = ?",
                (email, password)
            )
            return cursor.fetchone()

    @staticmethod
    def get_all_users():
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, email, password FROM users")
            return cursor.fetchall()

class SessionRepository:
    @staticmethod
    def create_session(user_id: int, ip_address: str):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM user_sessions WHERE ip_address = ?", (ip_address,)
            )
            cursor.execute(
                "INSERT INTO user_sessions (user_id, ip_address) VALUES (?, ?)",
                (user_id, ip_address)
            )
            conn.commit()

    @staticmethod
    def verify_access(user_id: int, ip_address: str) -> bool:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM user_sessions WHERE user_id = ? AND ip_address = ?",
                (user_id, ip_address)
            )
            return cursor.fetchone() is not None

    @staticmethod
    def get_all_sessions():
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, user_id, ip_address, created_at FROM user_sessions")
            return cursor.fetchall()

class QuizRepository:
    @staticmethod
    def save_answers(user_id: int, answers: str, results: dict):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO user_answers (user_id, answers, results_json) VALUES (?, ?, ?)",
                (user_id, answers, str(results))
            )
            conn.commit()

    @staticmethod
    def get_latest_results(user_id: int) -> Optional[tuple]:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT answers, results_json FROM user_answers WHERE user_id = ? ORDER BY completed_at DESC LIMIT 1",
                (user_id,)
            )
            return cursor.fetchone()

    @staticmethod
    def save_quiz_progress(user_id: int, current_question: int, answers: dict, results: dict = None):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO quiz_progress 
                (user_id, current_question, answers_json, results_json, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (user_id, current_question, str(answers), str(results) if results else None))
            conn.commit()

    @staticmethod
    def get_quiz_progress(user_id: int) -> Optional[Dict[str, Any]]:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT current_question, answers_json, results_json 
                FROM quiz_progress WHERE user_id = ?
            ''', (user_id,))
            result = cursor.fetchone()
            if result:
                return {
                    'current_question': result[0],
                    'answers': eval(result[1]) if result[1] else {},
                    'results': eval(result[2]) if result[2] else None
                }
            return None

    @staticmethod
    def clear_quiz_progress(user_id: int):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM quiz_progress WHERE user_id = ?', (user_id,))
            conn.commit()

class ChatRepository:
    @staticmethod
    def create_chat(user_id: int, title: str) -> int:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO user_chats (user_id, title) VALUES (?, ?)",
                (user_id, title)
            )
            chat_id = cursor.lastrowid
            conn.commit()
            return chat_id

    @staticmethod
    def get_user_chats(user_id: int) -> List[dict]:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, title, created_at, updated_at 
                FROM user_chats 
                WHERE user_id = ? 
                ORDER BY updated_at DESC
            ''', (user_id,))
            chats = cursor.fetchall()
            
            return [{
                "id": chat[0],
                "title": chat[1],
                "created_at": chat[2],
                "updated_at": chat[3]
            } for chat in chats]

    @staticmethod
    def set_active_chat(user_id: int, chat_id: int) -> bool:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM user_chats WHERE id = ? AND user_id = ?",
                (chat_id, user_id)
            )
            if cursor.fetchone():
                cursor.execute('''
                    INSERT OR REPLACE INTO user_active_chats (user_id, active_chat_id)
                    VALUES (?, ?)
                ''', (user_id, chat_id))
                conn.commit()
                return True
            return False

    @staticmethod
    def get_active_chat(user_id: int) -> Optional[dict]:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT uc.id, uc.title, uc.created_at, uc.updated_at
                FROM user_chats uc
                JOIN user_active_chats uac ON uc.id = uac.active_chat_id
                WHERE uac.user_id = ?
            ''', (user_id,))
            chat = cursor.fetchone()
            
            if chat:
                return {
                    "id": chat[0],
                    "title": chat[1],
                    "created_at": chat[2],
                    "updated_at": chat[3]
                }
            return None

    @staticmethod
    def delete_chat(user_id: int, chat_id: int) -> bool:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM user_chats WHERE id = ? AND user_id = ?",
                (chat_id, user_id)
            )
            if not cursor.fetchone():
                return False
                
            cursor.execute("DELETE FROM chat_messages WHERE chat_id = ?", (chat_id,))
            cursor.execute("DELETE FROM user_chats WHERE id = ?", (chat_id,))
            
            cursor.execute(
                "SELECT active_chat_id FROM user_active_chats WHERE user_id = ?",
                (user_id,)
            )
            active_chat = cursor.fetchone()
            if active_chat and active_chat[0] == chat_id:
                cursor.execute(
                    "DELETE FROM user_active_chats WHERE user_id = ?",
                    (user_id,)
                )
                
            conn.commit()
            return True

    @staticmethod
    def add_message(chat_id: int, role: str, content: str):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO chat_messages (chat_id, role, content) VALUES (?, ?, ?)",
                (chat_id, role, content)
            )
            cursor.execute(
                "UPDATE user_chats SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (chat_id,)
            )
            conn.commit()

    @staticmethod
    def get_messages(chat_id: int) -> List[dict]:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT role, content, created_at 
                FROM chat_messages 
                WHERE chat_id = ? 
                ORDER BY created_at ASC
            ''', (chat_id,))
            messages = cursor.fetchall()
        
            return [{
                "role": msg[0],
                "content": msg[1],
                "created_at": msg[2]
            } for msg in messages]