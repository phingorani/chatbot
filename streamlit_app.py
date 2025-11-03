import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as gpt
from functions import *

# Load environment variables
load_dotenv()

# Configure Streamlit page settings
st.set_page_config(
    page_title="Chat with Tony Stark!",
    page_icon=":robot_face:",  # Favicon emoji
    layout="wide",  # Page layout option
)

API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = os.getenv("GOOGLE_API_KEY") or "gemini-2.0-flash"
BOT_TITLE = os.getenv("BOT_TITLE") or "AI bot"
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT")

# Set up Google Gemini-Pro AI model
gpt.configure(api_key=API_KEY)
model = gpt.GenerativeModel(
    model_name=GEMINI_MODEL,
    system_instruction=SYSTEM_PROMPT)

# Initialize chat session in Streamlit if not already present
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[
        {
            "role": "model",
            "parts": [
                {"text": "Alright, let's get this show on the road. What cosmic queries do you have for me today? Don't waste my time with anything boring."}
            ],
        }
    ])

# Display the chatbot's title on the page
st.title("🤖 Chat with " + BOT_TITLE)
# Display the chat history
for msg in st.session_state.chat_session.history:
    role = getattr(msg, "role", None) if not isinstance(msg, dict) else msg.get("role")
    parts = getattr(msg, "parts", None) if not isinstance(msg, dict) else msg.get("parts")
    text = ""
    if parts:
        collected = []
        for p in parts:
            if hasattr(p, "text") and getattr(p, "text"):
                collected.append(p.text)
            elif isinstance(p, dict):
                t = p.get("text")
                if t:
                    collected.append(t)
        text = "\n".join(collected)
    else:
        content = getattr(msg, "content", None) if not isinstance(msg, dict) else msg.get("content")
        if content:
            text = str(content)
    with st.chat_message(map_role(role)):
        st.markdown(text or "")

# Input field for user's message
user_input = st.chat_input("Ask " +BOT_TITLE+"...")
if user_input:
    # Add user's message to chat and display it
    st.chat_message("user").markdown(user_input)

    # Send user's message to Gemini and get the response
    gemini_response = fetch_gemini_response(user_input)

    # Display Gemini's response
    with st.chat_message("assistant"):
        st.markdown(gemini_response)

    # No manual history mutation needed; ChatSession updates history automatically
