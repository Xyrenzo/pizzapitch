import sqlite3
import psycopg2
import json
from datetime import datetime
from config import DB_URL

def migrate_data():
    # Подключение к SQLite
    sqlite_conn = sqlite3.connect('users.db')
    sqlite_cursor = sqlite_conn.cursor()
    
    # Подключение к PostgreSQL
    pg_conn = psycopg2.connect(DB_URL, sslmode='require')
    pg_cursor = pg_conn.cursor()
    
    try:
        print("Начало миграции данных...")
        
        # 1. Миграция пользователей
        print("Миграция пользователей...")
        sqlite_cursor.execute("SELECT id, username, email, password, created_at FROM users")
        users = sqlite_cursor.fetchall()
        
        for user in users:
            try:
                pg_cursor.execute(
                    "INSERT INTO users (id, username, email, password, created_at) VALUES (%s, %s, %s, %s, %s)",
                    user
                )
            except Exception as e:
                print(f"Ошибка при миграции пользователя {user[0]}: {e}")
        
        print(f"Мигрировано пользователей: {len(users)}")
        
        # 2. Миграция сессий
        print("Миграция сессий...")
        sqlite_cursor.execute("SELECT id, user_id, ip_address, created_at FROM user_sessions")
        sessions = sqlite_cursor.fetchall()
        
        for session in sessions:
            try:
                pg_cursor.execute(
                    "INSERT INTO user_sessions (id, user_id, ip_address, created_at) VALUES (%s, %s, %s, %s)",
                    session
                )
            except Exception as e:
                print(f"Ошибка при миграции сессии {session[0]}: {e}")
        
        print(f"Мигрировано сессий: {len(sessions)}")
        
        # 3. Миграция ответов на квиз
        print("Миграция ответов на квиз...")
        sqlite_cursor.execute("SELECT id, user_id, answers, results_json, completed_at FROM user_answers")
        answers = sqlite_cursor.fetchall()
        
        for answer in answers:
            try:
                pg_cursor.execute(
                    "INSERT INTO user_answers (id, user_id, answers, results_json, completed_at) VALUES (%s, %s, %s, %s, %s)",
                    answer
                )
            except Exception as e:
                print(f"Ошибка при миграции ответа {answer[0]}: {e}")
        
        print(f"Мигрировано ответов: {len(answers)}")
        
        # 4. Миграция прогресса квиза
        print("Миграция прогресса квиза...")
        sqlite_cursor.execute("SELECT id, user_id, current_question, answers_json, results_json, updated_at FROM quiz_progress")
        progress = sqlite_cursor.fetchall()
        
        for prog in progress:
            try:
                pg_cursor.execute(
                    "INSERT INTO quiz_progress (id, user_id, current_question, answers_json, results_json, updated_at) VALUES (%s, %s, %s, %s, %s, %s)",
                    prog
                )
            except Exception as e:
                print(f"Ошибка при миграции прогресса {prog[0]}: {e}")
        
        print(f"Мигрировано записей прогресса: {len(progress)}")
        
        # 5. Миграция чатов
        print("Миграция чатов...")
        sqlite_cursor.execute("SELECT id, user_id, title, created_at, updated_at FROM user_chats")
        chats = sqlite_cursor.fetchall()
        
        for chat in chats:
            try:
                pg_cursor.execute(
                    "INSERT INTO user_chats (id, user_id, title, created_at, updated_at) VALUES (%s, %s, %s, %s, %s)",
                    chat
                )
            except Exception as e:
                print(f"Ошибка при миграции чата {chat[0]}: {e}")
        
        print(f"Мигрировано чатов: {len(chats)}")
        
        # 6. Миграция сообщений чатов
        print("Миграция сообщений чатов...")
        sqlite_cursor.execute("SELECT id, chat_id, role, content, created_at FROM chat_messages")
        messages = sqlite_cursor.fetchall()
        
        for message in messages:
            try:
                pg_cursor.execute(
                    "INSERT INTO chat_messages (id, chat_id, role, content, created_at) VALUES (%s, %s, %s, %s, %s)",
                    message
                )
            except Exception as e:
                print(f"Ошибка при миграции сообщения {message[0]}: {e}")
        
        print(f"Мигрировано сообщений: {len(messages)}")
        
        # 7. Миграция активных чатов
        print("Миграция активных чатов...")
        sqlite_cursor.execute("SELECT user_id, active_chat_id FROM user_active_chats")
        active_chats = sqlite_cursor.fetchall()
        
        for active_chat in active_chats:
            try:
                pg_cursor.execute(
                    "INSERT INTO user_active_chats (user_id, active_chat_id) VALUES (%s, %s)",
                    active_chat
                )
            except Exception as e:
                print(f"Ошибка при миграции активного чата для пользователя {active_chat[0]}: {e}")
        
        print(f"Мигрировано активных чатов: {len(active_chats)}")
        
        # 8. Миграция отзывов
        print("Миграция отзывов...")
        sqlite_cursor.execute("SELECT id, user_id, rating, comment, likes, created_at, updated_at FROM reviews")
        reviews = sqlite_cursor.fetchall()
        
        for review in reviews:
            try:
                pg_cursor.execute(
                    "INSERT INTO reviews (id, user_id, rating, comment, likes, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    review
                )
            except Exception as e:
                print(f"Ошибка при миграции отзыва {review[0]}: {e}")
        
        print(f"Мигрировано отзывов: {len(reviews)}")
        
        # 9. Миграция лайков отзывов
        print("Миграция лайков отзывов...")
        sqlite_cursor.execute("SELECT id, review_id, user_id, created_at FROM review_likes")
        review_likes = sqlite_cursor.fetchall()
        
        for like in review_likes:
            try:
                pg_cursor.execute(
                    "INSERT INTO review_likes (id, review_id, user_id, created_at) VALUES (%s, %s, %s, %s)",
                    like
                )
            except Exception as e:
                print(f"Ошибка при миграции лайка {like[0]}: {e}")
        
        print(f"Мигрировано лайков: {len(review_likes)}")
        
        # Фиксируем изменения в PostgreSQL
        pg_conn.commit()
        print("Миграция завершена успешно!")
        
    except Exception as e:
        print(f"Критическая ошибка миграции: {e}")
        pg_conn.rollback()
    finally:
        sqlite_conn.close()
        pg_conn.close()

def verify_migration():
    """Проверка целостности миграции"""
    print("\nПроверка целостности миграции...")
    
    sqlite_conn = sqlite3.connect('users.db')
    sqlite_cursor = sqlite_conn.cursor()
    
    pg_conn = psycopg2.connect(DB_URL, sslmode='require')
    pg_cursor = pg_conn.cursor()
    
    try:
        # Проверяем количество записей в каждой таблице
        tables = [
            'users', 'user_sessions', 'user_answers', 'quiz_progress',
            'user_chats', 'chat_messages', 'user_active_chats', 'reviews', 'review_likes'
        ]
        
        for table in tables:
            sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table}")
            sqlite_count = sqlite_cursor.fetchone()[0]
            
            pg_cursor.execute(f"SELECT COUNT(*) FROM {table}")
            pg_count = pg_cursor.fetchone()[0]
            
            print(f"{table}: SQLite - {sqlite_count}, PostgreSQL - {pg_count}, {'✓' if sqlite_count == pg_count else '✗'}")
    
    except Exception as e:
        print(f"Ошибка при проверке: {e}")
    finally:
        sqlite_conn.close()
        pg_conn.close()

if __name__ == "__main__":
    print("=== Миграция данных из SQLite в PostgreSQL ===")
    
    # Сначала создаем таблицы в PostgreSQL
    from database.connection import init_db
    print("Инициализация базы данных PostgreSQL...")
    init_db()
    print("Таблицы созданы успешно!")
    
    # Запускаем миграцию
    migrate_data()
    
    # Проверяем целостность
    verify_migration()
    
    print("\nМиграция завершена!")