import os
import streamlit as st

from utils import db_utils


def render_chat(DB_NAME, DB_USER, DB_HOST, DB_PORT, DB_PASSWORD):
    st.title("Чат с LLM")

    # Инициализация состояния остановки генерации
    if 'stop_generation' not in st.session_state:
        st.session_state['stop_generation'] = False


    # Загружаем сообщения для выбранного чата
    if st.session_state['selected_chat_id'] is not None and st.session_state['LLM_agent'] is not None:
        st.session_state['messages'] = db_utils.load_chat_history(st.session_state['selected_chat_id'], DB_NAME,
                                                                  DB_USER, DB_HOST, DB_PORT, DB_PASSWORD)

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
                    ai_answer = st.session_state['LLM_agent'].send_message(
                        messages=st.session_state['messages'],
                        temperature=st.session_state['temperature'],
                        chat_id=st.session_state['selected_chat_id']
                    )

                    ai_answer = st.write_stream(ai_answer)

                placeholder.empty()
                # Сохраняем ответ, если генерация завершена
                st.session_state['messages'].append({"role": "assistant", "content": ai_answer})

                # Сохраняем в базу
                db_utils.save_message_to_db(st.session_state['selected_chat_id'], "user", prompt, DB_NAME, DB_USER,
                                            DB_HOST, DB_PORT, DB_PASSWORD)
                db_utils.save_message_to_db(st.session_state['selected_chat_id'], "assistant", ai_answer, DB_NAME,
                                            DB_USER, DB_HOST, DB_PORT, DB_PASSWORD)

                chat_name = db_utils.get_chat_name(st.session_state['selected_chat_id'], DB_NAME, DB_USER, DB_HOST,
                                                   DB_PORT, DB_PASSWORD)

                if chat_name == "Новый чат":
                    first_message = st.session_state['messages'][0]['content']

                    title_messages = [
                        {"role": "system",
                         "content": "Пожалуйста, сгенерируй тему разговора на основе сообщения пользователя. Тема должна быть краткой, четкой и отражать основную тему или идею сообщения. Она должно быть простой и понятной, без использования кавычек, цифр и спецсимволов. Тема должна состоять из русских слов. Не используй вводные слова, только тема разговора."},
                        {"role": "user", "content": f"Сообщение пользователя: {first_message}"}
                    ]

                    chat_name = st.session_state['LLM_agent'].llm.invoke(title_messages).content

                    chat_name = chat_name.strip()[:50]

                    db_utils.update_chat_name(st.session_state['selected_chat_id'], chat_name, DB_NAME, DB_USER,
                                              DB_HOST, DB_PORT, DB_PASSWORD)
                    st.rerun()
            else:
                # Если генерация была остановлена, ничего не делаем
                st.session_state['stop_generation'] = False  # Сбросить флаг, если нужно
    else:
        st.info("Перед началом общения, введите настройки модели в левой панели")
            
            
            
            
