import os
from dotenv import load_dotenv
import streamlit as st
from utils import db_utils

from ui.sidebar_ui import render_sidebar
from ui.chat_ui import render_chat

# Загружаем переменные окружения
load_dotenv()

DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_PASSWORD = os.environ.get("DB_PASSWORD")

# Инициализация приложения



def main():

    if 'LLM_agent' not in st.session_state:
        st.session_state['LLM_agent'] = None

    if 'selected_chat_id' not in st.session_state:
        st.session_state['selected_chat_id'] = None

    if 'chats' not in st.session_state:
        st.session_state['chats'] = None

    st.set_page_config(page_title="Мульти-чат с LLM", layout="wide")

    db_utils.create_tables(DB_NAME, DB_USER, DB_HOST, DB_PORT, DB_PASSWORD)
    
    render_sidebar(DB_NAME, DB_USER, DB_HOST, DB_PORT, DB_PASSWORD)
    render_chat(DB_NAME, DB_USER, DB_HOST, DB_PORT, DB_PASSWORD)

if __name__ == "__main__":
    main()
