import streamlit as st

# Function to translate roles between Gemini and Streamlit terminology
def map_role(role):
    if role == "model":
        return "assistant"
    else:
        return role

def fetch_gemini_response(user_query):
    # Send a message via the chat session so history is maintained
    response = st.session_state.chat_session.send_message(user_query)
    print(f"Tony's Response: {getattr(response, 'text', str(response))}")
    return getattr(response, 'text', '')