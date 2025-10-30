import sqlite3
from typing import Optional, Dict, Any, List
from database.connection import get_db_connection




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
    def get_user_by_email(email: str) -> Optional[tuple]:
        """Получить пользователя по email"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, username, email, password FROM users WHERE email = ?",
                (email,)
            )
            return cursor.fetchone()

    @staticmethod
    def save_oauth_info(user_id: int, provider: str, provider_id: str):
        """Сохранить информацию о OAuth провайдере"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            
            cursor.execute(
                "SELECT id FROM user_oauth WHERE user_id = ? AND provider = ?",
                (user_id, provider)
            )
            existing = cursor.fetchone()
            
            if existing:
                
                cursor.execute(
                    "UPDATE user_oauth SET provider_id = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ? AND provider = ?",
                    (provider_id, user_id, provider)
                )
            else:
                
                cursor.execute(
                    "INSERT INTO user_oauth (user_id, provider, provider_id) VALUES (?, ?, ?)",
                    (user_id, provider, provider_id)
                )
            
            conn.commit()
            print(f"OAuth info saved for user {user_id}, provider {provider}")

    @staticmethod
    def get_user_by_oauth(provider: str, provider_id: str) -> Optional[tuple]:
        """Получить пользователя по OAuth данным"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT u.id, u.username, u.email, u.password 
                   FROM users u 
                   JOIN user_oauth uo ON u.id = uo.user_id 
                   WHERE uo.provider = ? AND uo.provider_id = ?""",
                (provider, provider_id)
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
            cursor.execute(
                'DELETE FROM quiz_progress WHERE user_id = ?', (user_id,))
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
        print(f"REPOSITORY: Getting active chat for user {user_id}")
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
                print(f"REPOSITORY: Active chat found: {chat[0]} - {chat[1]}")
                return {
                    "id": chat[0],
                    "title": chat[1],
                    "created_at": chat[2],
                    "updated_at": chat[3]
                }
            print(f"REPOSITORY: No active chat found")
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

            cursor.execute(
                "DELETE FROM chat_messages WHERE chat_id = ?", (chat_id,))
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
        print(
            f"REPOSITORY: Adding message to chat {chat_id}, role: {role}, content: {content[:50]}...")
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
        print(f"REPOSITORY: Message added successfully")


    @staticmethod
    def get_messages(chat_id: int) -> List[dict]:
        print(f"REPOSITORY: Getting messages for chat {chat_id}")
        with get_db_connection() as conn:
            cursor = conn.cursor()

        
            cursor.execute("SELECT id FROM user_chats WHERE id = ?", (chat_id,))
            chat_exists = cursor.fetchone()
            print(f"REPOSITORY: Chat exists: {bool(chat_exists)}")

            cursor.execute('''
                SELECT role, content, created_at 
                FROM chat_messages 
                WHERE chat_id = ? 
                ORDER BY created_at ASC
            ''', (chat_id,))
            messages = cursor.fetchall()

            print(f"REPOSITORY: Found {len(messages)} messages in database")

            return [{
                "role": msg[0],
                "content": msg[1],
                "created_at": msg[2]
            } for msg in messages]


class ReviewRepository:
    @staticmethod
    def create_review(user_id: int, rating: int, comment: str) -> bool:
        """Создание отзыва (один отзыв на пользователя)"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO reviews (user_id, rating, comment, created_at) VALUES (?, ?, ?, datetime('now', 'localtime'))",
                    (user_id, rating, comment)
                )
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            
            return False

    @staticmethod
    def get_review_by_user(user_id: int) -> Optional[dict]:
        """Получить отзыв пользователя"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT r.id, r.user_id, u.username, r.rating, r.comment, 
                       r.likes, r.created_at, r.updated_at
                FROM reviews r
                JOIN users u ON r.user_id = u.id
                WHERE r.user_id = ?
            ''', (user_id,))
            result = cursor.fetchone()
            
            if result:
                return {
                    "id": result[0],
                    "user_id": result[1],
                    "username": result[2],
                    "rating": result[3],
                    "comment": result[4],
                    "likes": result[5],
                    "created_at": result[6],
                    "updated_at": result[7]
                }
            return None

    @staticmethod
    def get_all_reviews(sort_by: str = "newest") -> List[dict]:
        """Получить все отзывы с сортировкой"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            
            order_by = {
                "newest": "r.created_at DESC",
                "oldest": "r.created_at ASC",
                "highest": "r.rating DESC, r.created_at DESC",
                "lowest": "r.rating ASC, r.created_at DESC",
                "popular": "r.likes DESC, r.created_at DESC"
            }.get(sort_by, "r.created_at DESC")
            
            cursor.execute(f'''
                SELECT r.id, r.user_id, u.username, r.rating, r.comment, 
                       r.likes, r.created_at, r.updated_at
                FROM reviews r
                JOIN users u ON r.user_id = u.id
                ORDER BY {order_by}
            ''')
            
            reviews = cursor.fetchall()
            return [{
                "id": review[0],
                "user_id": review[1],
                "username": review[2],
                "rating": review[3],
                "comment": review[4],
                "likes": review[5],
                "created_at": review[6],
                "updated_at": review[7]
            } for review in reviews]

    @staticmethod
    def get_average_rating() -> float:
        """Получить средний рейтинг"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT AVG(rating) FROM reviews")
            result = cursor.fetchone()
            return round(result[0] or 0, 1)

    @staticmethod
    def get_reviews_count() -> int:
        """Получить количество отзывов"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM reviews")
            return cursor.fetchone()[0]

    @staticmethod
    def update_review(user_id: int, rating: int, comment: str) -> bool:
        """Обновить отзыв пользователя"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE reviews 
                SET rating = ?, comment = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE user_id = ?
            ''', (rating, comment, user_id))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def delete_review(user_id: int) -> bool:
        """Удалить отзыв пользователя"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            
            cursor.execute('''
                DELETE FROM review_likes 
                WHERE review_id IN (SELECT id FROM reviews WHERE user_id = ?)
            ''', (user_id,))
            
            
            cursor.execute("DELETE FROM reviews WHERE user_id = ?", (user_id,))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def like_review(review_id: int, user_id: int) -> bool:
        """Лайкнуть отзыв"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                
                cursor.execute(
                    "SELECT id FROM review_likes WHERE review_id = ? AND user_id = ?",
                    (review_id, user_id)
                )
                if cursor.fetchone():
                    return False  
                
                
                cursor.execute(
                    "INSERT INTO review_likes (review_id, user_id) VALUES (?, ?)",
                    (review_id, user_id)
                )
                
                
                cursor.execute(
                    "UPDATE reviews SET likes = likes + 1 WHERE id = ?",
                    (review_id,)
                )
                
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False

    @staticmethod
    def unlike_review(review_id: int, user_id: int) -> bool:
        """Убрать лайк с отзыва"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute(
                "DELETE FROM review_likes WHERE review_id = ? AND user_id = ?",
                (review_id, user_id)
            )
            
            if cursor.rowcount > 0:
                
                cursor.execute(
                    "UPDATE reviews SET likes = likes - 1 WHERE id = ?",
                    (review_id,)
                )
                conn.commit()
                return True
            
            return False

    @staticmethod
    def has_user_liked(review_id: int, user_id: int) -> bool:
        """Проверить, лайкал ли пользователь отзыв"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM review_likes WHERE review_id = ? AND user_id = ?",
                (review_id, user_id)
            )
            return cursor.fetchone() is not None
