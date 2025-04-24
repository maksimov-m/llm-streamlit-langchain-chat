import os
import streamlit as st
import tempfile
import json
import shutil
from utils import db_utils
from utils.file_processor_pipeline import FileProcessorPipeline, generate_descriptions_for_dones

from workflow.rag_workflow import RAGWorkflow


def render_sidebar():
    with st.sidebar:
        render_model_settings()
        render_chat_list()
        render_file_manager()

def render_model_settings():
    if st.session_state['workflow'] is None:
        st.header("Настройки модели")
        model = st.text_input("Название модели", value=os.getenv("MODEL_NAME"))
        base_url = st.text_input("Базовый URL", value=os.getenv("API_URL"))
        api_key = st.text_input("API ключ", value=os.getenv("API_KEY"), type="password")

        if st.button("Сохранить настройки"):
            os.environ["MODEL_NAME"] = model
            os.environ["MODEL_PROVIDER"] = st.session_state['params_RAG']['PROVIDER_API']
            os.environ["API_URL"] = base_url
            os.environ["API_KEY"] = api_key
            # Initialization
            if st.session_state['params_RAG']['PROVIDER_API'] == "openai":

                config_1 = {
                    'model': model,
                    'api_url': base_url,
                    'api_key': api_key
                }

                config_2 = {
                    'artifacts_path': st.session_state['params_RAG']['ARTIFACTS_PATH'],
                    'dataframe_path': st.session_state['params_RAG']['DATAFRAME_PATH'],
                    'embedding_model_name': st.session_state['params_RAG']['EMBEDDING_MODEL_NAME']
                }

                with st.spinner("Модель загружается..."):
                    workflow = RAGWorkflow(config_1, config_2)

                st.session_state['workflow'] = workflow
                st.success("Модель успешно подключена")
                st.rerun()

            else:
                st.error("Не поддерживаемый поставщик модели, попробуйте openai")


def render_chat_list():
    if (st.session_state['workflow'] is not None and
            os.path.exists(st.session_state['params_RAG']['ARTIFACTS_PATH']) and
            len(os.listdir(st.session_state['params_RAG']['ARTIFACTS_PATH'])) > 0):

        if "d_descriptions_domens" not in st.session_state:
            with open(os.path.join(st.session_state['params_RAG']['ARTIFACTS_PATH'],
                                   st.session_state['params_RAG']["DESCRIPTION_ROUTER_PATH"]), "r") as f:
                st.session_state["d_descriptions_domens"] = json.load(f)

        st.header("Чаты")
        st.session_state['chats'] = db_utils.get_chats()

        if st.button("➕ Новый чат"):
            new_chat_id = db_utils.create_new_chat()
            st.session_state['selected_chat_id'] = new_chat_id
            st.session_state['chats'] = db_utils.get_chats()

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


def render_file_manager():
    # Показываем виджеты только если file_manager не True
    if ((not os.path.exists(st.session_state['params_RAG']['ARTIFACTS_PATH']) or
            len(os.listdir(st.session_state['params_RAG']['ARTIFACTS_PATH'])) == 0) and
            st.session_state['workflow'] is not None and
            st.session_state.file_manager is None):
        # Инициализация состояния
        st.session_state.setdefault('uploaded_files', [])
        st.session_state.setdefault('process_complete', False)
        st.session_state.setdefault('last_result', None)

        # Основной интерфейс
        st.title("📁 Для работы с сервисом загрузите текстовые данные!")
        st.text("Ваши файлы должны быть в формате pdf или txt, а также не превышать 5 мб.")
        st.text("После загрузки файлов будет происходить их обработка. Это может занять определенное время.")

        # Секция загрузки файлов
        with st.expander("➕ Загрузить файлы", expanded=True):
            uploaded_files = st.file_uploader(
                "Выберите файлы",
                accept_multiple_files=True,
                type=['pdf', 'txt'],
                label_visibility="collapsed"
            )

            # Обновляем список файлов
            if uploaded_files:
                current_files = st.session_state.uploaded_files.copy()
                for new_file in uploaded_files:
                    if not any(f.name == new_file.name and f.size == new_file.size for f in current_files):
                        current_files.append(new_file)
                st.session_state.uploaded_files = current_files
                st.session_state.process_complete = False

        # Секция обработки
        if st.session_state.uploaded_files and not st.session_state.process_complete:
            st.divider()
            if st.button("⚙️ Подготовить данные",
                         type="primary",
                         use_container_width=True):
                process_files_for_rag()
                # После завершения обработки скрываем виджеты
                st.session_state.file_manager = True
                st.rerun()

        # Показ результатов
        if st.session_state.process_complete and st.session_state.last_result:
            st.session_state.file_manager = True
            st.rerun()
    else:
        # Показываем сообщение после завершения
        if (st.session_state['workflow'] is not None and
                st.button("🔄 Загрузить новые файлы")):
            shutil.rmtree(st.session_state['params_RAG']['ARTIFACTS_PATH'])
            # Полный сброс состояния
            st.session_state.uploaded_files = []
            st.session_state.process_complete = False
            st.session_state.file_manager = None
            st.session_state.last_result = None
            st.rerun()


def process_files_for_rag():
    """Обработка файлов с использованием временной директории"""
    # try:
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Сохраняем загруженные файлы во временную директорию
        for uploaded_file in st.session_state.uploaded_files:
            file_path = os.path.join(tmp_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

        # Параметры обработки (настройте под свои нужды)
        output_path = st.session_state['params_RAG']['ARTIFACTS_PATH']  # Или другая постоянная директория

        if not os.path.exists(output_path):
            os.makedirs(output_path)

        embedding_model_name = st.session_state['params_RAG']['EMBEDDING_MODEL_NAME']  # Замените на реальное имя модели

        with st.spinner("Идет обработка файлов..."):
            fileprocessor = FileProcessorPipeline(
                input_path=tmp_dir,
                output_path=output_path,
                embedding_model_name=embedding_model_name
            )

            df = fileprocessor.start_process()

            if df is not None:
                print(f"init_context_data for Retriever -> "
                      f"{st.session_state['workflow'].retriever.init_context_data()}")

                d_descriptions_domens = generate_descriptions_for_dones(df,
                    st.session_state['workflow'].base_generator.get_llm())

                with open(os.path.join(st.session_state['params_RAG']['ARTIFACTS_PATH'],
                                       st.session_state['params_RAG']["DESCRIPTION_ROUTER_PATH"]), "w") as f:
                    json.dump(d_descriptions_domens, f)

                st.session_state["d_descriptions_domens"] = d_descriptions_domens

                st.session_state.last_result = True

            if df is not None:
                st.sidebar.success("✅ Все файлы успешно обработаны!")
            else:
                st.sidebar.warning("Файлы не загружены. Повторите попытку")

    if 'tmp_dir' in locals() and os.path.exists(tmp_dir):
        try:
            for f in os.listdir(tmp_dir):
                os.remove(os.path.join(tmp_dir, f))
            os.rmdir(tmp_dir)
        except Exception as cleanup_error:
            st.error(f"Ошибка очистки временных файлов: {cleanup_error}")

    st.session_state.process_complete = True
