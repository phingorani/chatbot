import os
import streamlit as st
import json
import time
from datetime import datetime
from dotenv import load_dotenv
from google import generativeai as gpt
from functions import *

load_dotenv()

st.set_page_config(
    page_title="Chat with AI Bot",
    page_icon="🤖",
    layout="wide",
)

API_KEY = os.getenv("GOOGLE_API_KEY")
DEFAULT_MODEL = os.getenv("GEMINI_MODEL") or "gemini-2.5-flash-lite"
DEFAULT_BOT_TITLE = os.getenv("BOT_TITLE") or "AI bot"
DEFAULT_SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT")

if not API_KEY:
    st.error(
        "Google API key not found. Please set GOOGLE_API_KEY in your environment or .env file."
    )
    st.stop()

gpt.configure(api_key=API_KEY)

DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 8192

if "chat_session" not in st.session_state:
    st.session_state.chat_session = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "model_name" not in st.session_state:
    st.session_state.model_name = DEFAULT_MODEL

if "bot_title" not in st.session_state:
    st.session_state.bot_title = DEFAULT_BOT_TITLE

if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = DEFAULT_SYSTEM_PROMPT

if "temperature" not in st.session_state:
    st.session_state.temperature = DEFAULT_TEMPERATURE

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Alright, let's get this show on the road. What cosmic queries do you have for me today? Don't waste my time with anything boring.",
        }
    ]

if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}

if "editing_chat_id" not in st.session_state:
    st.session_state.editing_chat_id = None

if "rename_input" not in st.session_state:
    st.session_state.rename_input = ""


def initialize_chat_session(reset=False):
    gpt.configure(api_key=API_KEY)
    model = gpt.GenerativeModel(
        model_name=st.session_state.model_name,
        system_instruction=st.session_state.system_prompt
        if st.session_state.system_prompt
        else None,
    )

    if reset or not st.session_state.chat_session:
        st.session_state.chat_session = model.start_chat(history=[])

        for msg in st.session_state.messages:
            st.session_state.chat_session.history.append(
                {
                    "role": "user" if msg["role"] == "user" else "model",
                    "parts": [{"text": msg["content"]}],
                }
            )


def get_available_models():
    try:
        models = gpt.list_models()
        return [
            m.name
            for m in models
            if "generateContent" in m.supported_generation_methods
        ]
    except Exception as e:
        st.error(f"Error fetching models: {e}")
        return [
            "gemini-2.5-flash-lite",
            "gemini-2.0-flash-exp",
            "gemini-1.5-pro",
            "gemini-1.5-flash",
        ]


initialize_chat_session()

with st.sidebar:
    st.header("⚙️ Configuration")

    model_options = get_available_models()
    selected_model = st.selectbox(
        "Select Model",
        model_options,
        index=model_options.index(st.session_state.model_name)
        if st.session_state.model_name in model_options
        else 0,
    )
    if selected_model != st.session_state.model_name:
        st.session_state.model_name = selected_model
        initialize_chat_session(reset=True)
        st.session_state.messages = []
        st.rerun()

    new_bot_title = st.text_input("Bot Name", value=st.session_state.bot_title)
    if new_bot_title != st.session_state.bot_title:
        st.session_state.bot_title = new_bot_title
        st.rerun()

    new_system_prompt = st.text_area(
        "System Prompt",
        value=st.session_state.system_prompt or "",
        height=150,
        help="Define the bot's personality and behavior",
    )
    if new_system_prompt != (st.session_state.system_prompt or ""):
        st.session_state.system_prompt = new_system_prompt
        initialize_chat_session(reset=True)
        st.session_state.messages = []
        st.rerun()

    st.divider()

    st.subheader("🔄 Chat Actions")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            initialize_chat_session(reset=True)
            st.rerun()

    with col2:
        saved_chats = get_saved_chats()
        if st.session_state.messages and len(saved_chats) < 10:
            if st.button("💾 Save Current Chat"):
                chat_id = save_chat_session(
                    st.session_state.messages,
                    f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                )
                st.session_state.chat_sessions[chat_id] = {
                    "title": f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                    "messages": st.session_state.messages.copy(),
                }
                st.success("Chat saved!")
                time.sleep(1)
                st.rerun()

    st.divider()

    st.subheader("📊 Configuration")
    st.session_state.temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=st.session_state.temperature,
        step=0.1,
        help="Controls randomness in responses",
    )

    st.divider()

    st.subheader("📚 Chat History")
    saved_chats = get_saved_chats()

    if saved_chats:
        for chat_id, chat_data in saved_chats.items():
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                if st.button(
                    f"💬 {chat_data['title']}",
                    key=f"load_{chat_id}",
                ):
                    loaded_chat = load_chat_session(chat_id)
                    st.session_state.messages = loaded_chat.get("messages", [])
                    st.session_state.chat_session = None
                    initialize_chat_session()
                    st.session_state.editing_chat_id = None
                    st.rerun()
            with col2:
                if st.button("✏️", key=f"rename_{chat_id}", help="Rename chat"):
                    st.session_state.editing_chat_id = chat_id
                    st.session_state.rename_input = chat_data["title"]
            with col3:
                if st.button("🗑️", key=f"delete_{chat_id}", help="Delete chat"):
                    if delete_chat_session(chat_id):
                        st.rerun()

        if st.session_state.editing_chat_id:
            st.text_input(
                "New title:",
                value=st.session_state.rename_input,
                key="new_title_input",
            )
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✓ Save", key="confirm_rename"):
                    if update_chat_title(
                        st.session_state.editing_chat_id,
                        st.session_state.new_title_input,
                    ):
                        st.success("Title updated!")
                        time.sleep(1)
                        st.session_state.editing_chat_id = None
                        st.rerun()
            with col2:
                if st.button("✗ Cancel", key="cancel_rename"):
                    st.session_state.editing_chat_id = None
                    st.rerun()
    else:
        st.info("No saved chats yet. Save your conversations to see them here.")

    st.divider()

    st.subheader("📂 Load Saved Chat")
    uploaded_file = st.file_uploader("Upload chat JSON", type=["json"])
    if uploaded_file is not None:
        try:
            chat_data = json.load(uploaded_file)
            if "messages" in chat_data:
                st.session_state.messages = chat_data["messages"]
                st.session_state.chat_session = None
                initialize_chat_session()
                st.success("Chat loaded successfully!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Invalid chat file format")
        except Exception as e:
            st.error(f"Error loading chat: {e}")

st.title(f"🤖 Chat with {st.session_state.bot_title}")

for msg in st.session_state.messages:
    with st.chat_message(str(msg["role"])):
        content = msg["content"]

        if "```" in content:
            import re

            try:
                from pygments import highlight
                from pygments.lexers import get_lexer_by_name
                from pygments.formatters import HtmlFormatter
                from markdown import markdown

                use_pygments = True
            except ImportError:
                use_pygments = False

            pattern = r"```(\w*)\n(.*?)\n```"
            parts = re.split(pattern, content, flags=re.DOTALL)

            if not use_pygments:
                for i, part in enumerate(parts):
                    if i % 3 == 1:
                        st.code(part, language=parts[i - 1] if i > 0 else None)
                    elif i % 3 == 2:
                        continue
                    else:
                        if part:
                            st.markdown(part)
                continue

            for i, part in enumerate(parts):
                if i % 3 == 1:
                    lang = parts[i - 1] if i > 0 else None
                    if lang and lang.lower() in [
                        "python",
                        "py",
                        "javascript",
                        "js",
                        "java",
                        "cpp",
                        "c",
                        "html",
                        "css",
                        "json",
                        "sql",
                        "bash",
                        "shell",
                    ]:
                        try:
                            lexer = get_lexer_by_name(
                                lang.lower() if lang.lower() != "py" else "python"
                            )
                            formatter = HtmlFormatter(style="friendly", noclasses=True)
                            highlighted = highlight(part, lexer, formatter)
                            st.markdown(
                                f'<pre style="background-color: #f5f5f5; padding: 10px; border-radius: 5px;">{highlighted}</pre>',
                                unsafe_allow_html=True,
                            )
                        except Exception:
                            st.code(part, language=lang)
                    else:
                        st.code(part, language=None)
                elif i % 3 == 2:
                    continue
                else:
                    if part:
                        st.markdown(part)
        else:
            st.markdown(content)

user_input = st.chat_input(f"Ask {st.session_state.bot_title}...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        with st.spinner(f"{st.session_state.bot_title} is thinking..."):
            try:
                if st.session_state.chat_session is None:
                    initialize_chat_session(reset=False)

                response = retry_api_call(
                    lambda: st.session_state.chat_session.send_message(user_input),
                    max_retries=3,
                    delay=1.0,
                )

                if response:
                    full_response = getattr(response, "text", str(response))
                else:
                    raise Exception("API returned empty response after retries")

                message_placeholder.markdown(full_response)

                st.session_state.messages.append(
                    {"role": "assistant", "content": full_response}
                )

            except Exception as e:
                error_msg = f"⚠️ Error: {str(e)}"
                st.error(error_msg)
                full_response = (
                    f"Sorry, I encountered an error: {str(e)}. Please try again."
                )
                message_placeholder.markdown(full_response)
