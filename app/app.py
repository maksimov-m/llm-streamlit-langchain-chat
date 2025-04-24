import os
from dotenv import load_dotenv
import streamlit as st
from utils import db_utils

from ui.sidebar_ui import render_sidebar
from ui.chat_ui import render_chat

# Загружаем переменные окружения
load_dotenv()

# Параметры для БД
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_PASSWORD = os.environ.get("DB_PASSWORD")

# Параметры для RAG
ARTIFACTS_PATH = os.environ.get("ARTIFACTS_PATH")
EMBEDDING_MODEL_NAME = os.environ.get("EMBEDDING_MODEL_NAME")
DATAFRAME_PATH = os.environ.get("DATAFRAME_PATH")
DESCRIPTION_ROUTER_PATH = os.environ.get("DESCRIPTION_ROUTER_PATH")

# настройка API
PROVIDER_API = os.environ.get("PROVIDER_API")

def main():

    if 'params_DB' not in st.session_state:
        st.session_state['params_DB'] = {
            "DB_NAME": DB_NAME,
            "DB_USER": DB_USER,
            "DB_HOST": DB_HOST,
            "DB_PORT": DB_PORT,
            "DB_PASSWORD": DB_PASSWORD
        }

    if 'params_RAG' not in st.session_state:
        st.session_state['params_RAG'] = {
            "ARTIFACTS_PATH": ARTIFACTS_PATH,
            "EMBEDDING_MODEL_NAME": EMBEDDING_MODEL_NAME,
            "DATAFRAME_PATH": DATAFRAME_PATH,
            "PROVIDER_API": PROVIDER_API,
            "DESCRIPTION_ROUTER_PATH": DESCRIPTION_ROUTER_PATH
        }

    if 'process_complete' not in st.session_state:
        st.session_state.process_complete = False
    
    if 'last_result' not in st.session_state:
        st.session_state.last_result = None

    if 'file_manager' not in st.session_state:
        st.session_state['file_manager'] = None

    if 'workflow' not in st.session_state:
        st.session_state['workflow'] = None

    if 'selected_chat_id' not in st.session_state:
        st.session_state['selected_chat_id'] = None

    if 'chats' not in st.session_state:
        st.session_state['chats'] = None

    st.set_page_config(page_title="Мульти-чат с LLM", layout="wide")

    db_utils.create_tables()
    
    render_sidebar()
    render_chat()

if __name__ == "__main__":
    main()
