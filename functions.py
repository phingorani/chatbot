import streamlit as st
import json
import time
import re
import os
from typing import Optional, List, Dict
import tempfile


def map_role(role):
    if role == "model":
        return "assistant"
    else:
        return role


def fetch_gemini_response(user_query):
    response = st.session_state.chat_session.send_message(user_query)
    return getattr(response, "text", "")


async def fetch_gemini_response_stream(user_query):
    response = st.session_state.chat_session.send_message(user_query, stream=True)
    return response


def save_chat_history(chat_history, filename=None):
    if filename is None:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"chat_history_{timestamp}.json"

    history_data = {"timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "messages": []}

    for msg in chat_history:
        role = (
            getattr(msg, "role", None) if not isinstance(msg, dict) else msg.get("role")
        )
        parts = (
            getattr(msg, "parts", None)
            if not isinstance(msg, dict)
            else msg.get("parts")
        )
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
            content = (
                getattr(msg, "content", None)
                if not isinstance(msg, dict)
                else msg.get("content")
            )
            if content:
                text = str(content)

        history_data["messages"].append({"role": map_role(role), "content": text or ""})

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(history_data, f, ensure_ascii=False, indent=2)

    return filename


def load_chat_history(filename):
    with open(filename, "r", encoding="utf-8") as f:
        history_data = json.load(f)

    return history_data


def format_response_with_code(text):
    import re

    code_blocks = re.findall(r"```(\w*)\n(.*?)\n```", text, re.DOTALL)
    for lang, code in code_blocks:
        text = text.replace(f"```{lang}\n{code}\n```", f"```{lang}\n{code}\n```")

    return text


def extract_code_blocks(text):
    pattern = r"```(\w*)\n(.*?)\n```"
    matches = re.findall(pattern, text, re.DOTALL)
    return matches


def get_saved_chats(directory: str = "saved_chats") -> Dict[str, Dict]:
    """Get list of all saved chat sessions."""
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    chats = {}
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            filepath = os.path.join(directory, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    chat_id = filename.replace(".json", "")
                    chats[chat_id] = {
                        "filename": filename,
                        "data": data,
                        "title": data.get("title", f"Chat {chat_id}"),
                        "timestamp": data.get("timestamp", ""),
                    }
            except Exception:
                continue
    return chats


def save_chat_session(
    messages: List[Dict],
    title: str,
    chat_id: str = None,
    directory: str = "saved_chats",
) -> str:
    """Save a chat session to file."""
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    if chat_id is None:
        chat_id = f"chat_{int(time.time())}"

    chat_data = {
        "title": title,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "messages": messages,
    }

    filepath = os.path.join(directory, f"{chat_id}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(chat_data, f, ensure_ascii=False, indent=2)

    return chat_id


def load_chat_session(chat_id: str, directory: str = "saved_chats") -> Dict:
    """Load a chat session from file."""
    filepath = os.path.join(directory, f"{chat_id}.json")
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"title": "Chat", "timestamp": "", "messages": []}


def delete_chat_session(chat_id: str, directory: str = "saved_chats") -> bool:
    """Delete a chat session."""
    filepath = os.path.join(directory, f"{chat_id}.json")
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False


def update_chat_title(
    chat_id: str, new_title: str, directory: str = "saved_chats"
) -> bool:
    """Update the title of a saved chat."""
    chat_data = load_chat_session(chat_id, directory)
    if chat_data:
        chat_data["title"] = new_title
        chat_data["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
        filepath = os.path.join(directory, f"{chat_id}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(chat_data, f, ensure_ascii=False, indent=2)
        return True
    return False


def retry_api_call(func, max_retries: int = 3, delay: float = 1.0):
    """Retry API call with exponential backoff."""
    import random

    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(delay * (2**attempt) + random.uniform(0, 0.5))
    return None
