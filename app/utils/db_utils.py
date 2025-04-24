import psycopg2
import streamlit as st


# Подключение к базе данных PostgreSQL
def get_db_connection():
    conn = psycopg2.connect(
        dbname=st.session_state["params_DB"]['DB_NAME'],
        user=st.session_state["params_DB"]['DB_USER'],
        password=st.session_state["params_DB"]['DB_PASSWORD'],
        host=st.session_state["params_DB"]['DB_HOST'],
        port=st.session_state["params_DB"]['DB_PORT']
    )
    return conn


# Создание таблиц, если они не существуют
def create_tables():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id SERIAL PRIMARY KEY,
            chat_id INTEGER REFERENCES chats(id) ON DELETE CASCADE,
            role VARCHAR(50),
            content TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cur.close()
    conn.close()


# Получение списка чатов
def get_chats():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM chats ORDER BY created_at DESC;")
    chats = cur.fetchall()
    cur.close()
    conn.close()
    return chats


# Создание нового чата
def create_new_chat():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO chats (name) VALUES (%s) RETURNING id;", ("Новый чат",))
    chat_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return chat_id


# Загрузка истории для выбранного чата
def load_chat_history(chat_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT role, content FROM chat_history WHERE chat_id = %s ORDER BY timestamp ASC;", (chat_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"role": row[0], "content": row[1]} for row in rows]


# Сохранение сообщения в БД
def save_message_to_db(chat_id, role, content):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO chat_history (chat_id, role, content)
        VALUES (%s, %s, %s)
    """, (chat_id, role, content))
    conn.commit()
    cur.close()
    conn.close()


def get_chat_name(chat_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT name FROM chats WHERE id = %s;", (chat_id,))
    chat_name = cur.fetchone()[0]
    cur.close()
    conn.close()
    return chat_name


def update_chat_name(chat_id, new_name):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE chats
        SET name = %s
        WHERE id = %s;
    """, (new_name, chat_id))
    conn.commit()
    cur.close()
    conn.close()
