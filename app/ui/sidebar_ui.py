import os
import streamlit as st

from utils import db_utils
from utils.llm_utils import LLMAgent


def render_sidebar(DB_NAME, DB_USER, DB_HOST, DB_PORT, DB_PASSWORD):
    with st.sidebar:
        render_model_settings()
        render_chat_list(DB_NAME, DB_USER, DB_HOST, DB_PORT, DB_PASSWORD)


def render_chat_list(DB_NAME, DB_USER, DB_HOST, DB_PORT, DB_PASSWORD):
    if st.session_state['LLM_agent'] is not None:
        st.header("Чаты")
        st.session_state['chats'] = db_utils.get_chats(DB_NAME, DB_USER, DB_HOST, DB_PORT, DB_PASSWORD)

        if st.button("➕ Новый чат"):
            new_chat_id = db_utils.create_new_chat(DB_NAME, DB_USER, DB_HOST, DB_PORT, DB_PASSWORD)
            st.session_state['selected_chat_id'] = new_chat_id
            st.session_state['chats'] = db_utils.get_chats(DB_NAME, DB_USER, DB_HOST, DB_PORT, DB_PASSWORD)

            show_chat_list()
            st.rerun()

        show_chat_list()


def show_chat_list():
    if st.session_state['chats'] is not None and len(st.session_state['chats']) > 0:
        chat_names = [chat[1] for chat in st.session_state['chats']]

        current_chat_id = st.session_state['selected_chat_id']
        default_index = 0

        if current_chat_id is not None:
            for i, chat in enumerate(st.session_state['chats']):
                if chat[0] == current_chat_id:
                    default_index = i
                    break
        selected_index = st.radio(
            "Выберите чат:",
            options=range(len(chat_names)),
            format_func=lambda i: chat_names[i],
            index=default_index,
            key="chat_selector"
        )
        if isinstance(selected_index, int):
            new_selected_chat_id = st.session_state['chats'][selected_index][0]
        else:
            new_selected_chat_id = st.session_state['chats'][0][0]

        if current_chat_id != new_selected_chat_id:
            st.session_state['selected_chat_id'] = new_selected_chat_id
            st.rerun()
        else:
            st.session_state['selected_chat_id'] = new_selected_chat_id

        st.session_state['temperature'] = st.slider("Temperature", min_value=0.0, max_value=1.5, value=0.7, step=0.01)
    else:
        st.write("У вас нет чатов. Создайте новый.")


def render_model_settings():
    if st.session_state['LLM_agent'] is None:
        st.header("Настройки модели")
        model = st.text_input("Название модели", value=os.getenv("MODEL_NAME"))
        model_provider = st.text_input("Поставщик модели", value=os.getenv("MODEL_PROVIDER"))
        base_url = st.text_input("Базовый URL", value=os.getenv("API_URL"))
        api_key = st.text_input("API ключ", value=os.getenv("API_KEY"), type="password")

        if st.button("Сохранить настройки"):
            os.environ["MODEL_NAME"] = model
            os.environ["MODEL_PROVIDER"] = model_provider
            os.environ["API_URL"] = base_url
            os.environ["API_KEY"] = api_key

            if model_provider == "openai":
                LLM_agent = LLMAgent(os.getenv("MODEL_NAME"), os.getenv("MODEL_PROVIDER"), os.getenv("API_URL"),
                                     os.getenv("API_KEY"))

                if LLM_agent.validate_model():
                    st.session_state['LLM_agent'] = LLM_agent
                    st.success("Модель успешно подключена")
                    st.rerun()
                else:
                    st.session_state['LLM_agent'] = None
                    st.error("Не удалось подключиться к модели. Попробуйте изменить настройки")

            else:
                st.error("Не поддерживаемый поставщик модели, попробуйте openai")
