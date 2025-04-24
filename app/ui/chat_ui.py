import os
import streamlit as st


from utils import db_utils
from utils.prompts import title_conversation_instruction

from langchain_core.messages import HumanMessage

def render_chat():
    st.title("Чат с LLM")

    # Инициализация состояния остановки генерации
    if 'stop_generation' not in st.session_state:
        st.session_state['stop_generation'] = False

    # Загружаем сообщения для выбранного чата
    if (st.session_state['selected_chat_id'] is not None and
            st.session_state['workflow'] is not None and
            os.path.exists(st.session_state['params_RAG']['ARTIFACTS_PATH']) and
            len(os.listdir(st.session_state['params_RAG']['ARTIFACTS_PATH'])) > 0):
        st.session_state['messages'] = db_utils.load_chat_history(st.session_state['selected_chat_id'])

        if st.session_state['workflow'].retriever.context_data is None:
            st.session_state['workflow'].retriever.init_context_data()

        # Отображаем сообщения
        for message in st.session_state['messages']:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Поле ввода
        if prompt := st.chat_input("Сообщение"):

            st.session_state['messages'].append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            placeholder = st.empty()
            # Кнопка для остановки генерации
            stop_button = placeholder.button("Остановить генерацию", key="stop_gen_button")

            # Обработка нажатия на кнопку остановки генерации
            if stop_button:
                st.session_state['stop_generation'] = True
                st.warning("Остановка генерации...")

            # Генерация ответа
            ai_answer = ""
            if not st.session_state['stop_generation']:
                with st.chat_message("assistant"):
                    # Передаем параметры temperature в функцию инференса
                    ai_answer = st.session_state['workflow'].send_message(
                        messages=st.session_state['messages'],
                        temperature=st.session_state['temperature'],
                        chat_id=st.session_state['selected_chat_id'],
                        d_descriptions_domen=st.session_state['d_descriptions_domens']
                    )

                    ai_answer = st.write_stream(ai_answer)

                placeholder.empty()
                # Сохраняем ответ, если генерация завершена
                st.session_state['messages'].append({"role": "assistant", "content": ai_answer})

                # Сохраняем в базу
                db_utils.save_message_to_db(st.session_state['selected_chat_id'], "user", prompt)
                db_utils.save_message_to_db(st.session_state['selected_chat_id'], "assistant", ai_answer)

                chat_name = db_utils.get_chat_name(st.session_state['selected_chat_id'])

                if chat_name == "Новый чат":
                    first_message = st.session_state['messages'][0]['content']

                    message = HumanMessage(content=f"Сообщение пользователя: {first_message}")
                    st.session_state['workflow'].base_generator.set_system_prompt(title_conversation_instruction)
                    
                    chat_name = st.session_state['workflow'].generate_conversation_title([message])

                    chat_name = chat_name.strip()[:50]

                    db_utils.update_chat_name(st.session_state['selected_chat_id'], chat_name)
                    st.rerun()
            else:
                # Если генерация была остановлена, ничего не делаем
                st.session_state['stop_generation'] = False  # Сбросить флаг, если нужно
    else:
        st.info("Приятной работы!")
