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
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT")

# Set up Google Gemini-Pro AI model
gpt.configure(api_key=API_KEY)
model = gpt.GenerativeModel(
    model_name="gemini-pro",
    system_instruction=os.getenv(SYSTEM_PROMPT))

# Initialize chat session in Streamlit if not already present
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[
        {"role": "model",
         "content": "Alright, let's get this show on the road. What cosmic queries do you have for me today? Don't waste my time with anything boring."}
    ])

# Display the chatbot's title on the page
st.title("🤖 Chat with Tony Stark the Astrologer")
# Display the chat history
for msg in st.session_state.chat_session.history:
    with st.chat_message(map_role(msg["role"])):
        st.markdown(msg["content"])

# Input field for user's message
user_input = st.chat_input("Ask Tony...")
if user_input:
    # Add user's message to chat and display it
    st.chat_message("user").markdown(user_input)

    # Send user's message to Gemini and get the response
    gemini_response = fetch_gemini_response(user_input)

    # Display Gemini's response
    with st.chat_message("assistant"):
        st.markdown(gemini_response)

    # Add user and assistant messages to the chat history
    st.session_state.chat_session.history.append({"role": "user", "content": user_input})
    st.session_state.chat_session.history.append({"role": "model", "content": gemini_response})
