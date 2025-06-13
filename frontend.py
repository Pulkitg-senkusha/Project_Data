import streamlit as st
import requests
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()
API = os.getenv("API_URL")

st.set_page_config(page_title="Data AI Chatbot", layout="wide")

# Styling
st.markdown("""
<style>
    .stApp { background-color: #1E1E1E; color: white; }
    .chat-container { max-width: 800px; margin: 0 auto; padding: 20px; }
    .chat-message {
        padding: 10px; border-radius: 10px; margin-bottom: 10px;
        max-width: 70%; word-wrap: break-word;
    }
    .user-message { background-color: #2D2D2D; color: white; margin-left: auto; text-align: right; }
    .bot-message { background-color: #3A3A3A; color: white; margin-right: auto; text-align: left; }
    .timestamp { font-size: 12px; color: #888; margin-top: 5px; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{
        "role": "bot",
        "content": "What's on your mind today?",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }]

if "file_uploaded" not in st.session_state:
    st.session_state.file_uploaded = False


# File upload
uploaded_file = st.file_uploader("Upload CSV or PDF", type=["csv", "pdf"])

if uploaded_file:
    st.session_state.file_uploaded = True
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Display file upload event in chat
    st.session_state.chat_history.append({
        "role": "user",
        "content": f"Uploaded file: {uploaded_file.name}",
        "timestamp": timestamp
    })

    files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}

    try:
        with st.spinner("Processing file..."):
            response = requests.post(f"{API}/upload", files=files)
            response.raise_for_status()
            result = response.json()

        # Append processed file content to chat
        if uploaded_file.name.endswith(".csv") and "data" in result:
            headers = result["data"]
            content = "I've processed your CSV file. Here are the headers:\n\n```text\n" + "\n".join(headers) + "\n```"

        elif uploaded_file.name.endswith(".pdf") and "text" in result:
            text = result["text"][:1000]  
            content = "I've processed your PDF file. Here's the extracted text:\n\n" + text

        else:
            content = "Sorry, I couldn't process the file. Unexpected response."

        st.session_state.chat_history.append({
            "role": "bot",
            "content": content,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    except requests.exceptions.RequestException as e:
        st.session_state.chat_history.append({
            "role": "bot",
            "content": f" Error uploading file: {str(e)}",
            "timestamp": timestamp
        })

# Chat display area
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for msg in st.session_state.chat_history:
    role_class = "user-message" if msg["role"] == "user" else "bot-message"
    st.markdown(
        f'<div class="chat-message {role_class}">{msg["content"]}<div class="timestamp">{msg["timestamp"]}</div></div>',
        unsafe_allow_html=True
    )
st.markdown('</div>', unsafe_allow_html=True)

# Chat input
user_input = st.text_input(
    label="Type your message here",
    placeholder="Ask anything about your uploaded file...",
    label_visibility="collapsed"
)

if user_input:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Add user message
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input,
        "timestamp": timestamp
    })

    # Format history for API
    history = [
        {"role": "assistant" if m["role"] == "bot" else m["role"], "content": m["content"]}
        for m in st.session_state.chat_history
        if m["role"] in ["user", "bot"]
    ]

    MAX_HISTORY = 10
    history = history[-MAX_HISTORY:]

    try:
        with st.spinner("Thinking..."):
            response = requests.post(f"{API}/chat", json={"history": history})
            response.raise_for_status()
            result = response.json()
            st.write(result['response'])


        reply = result.get("response", "Sorry, I couldn't understand that.")

        st.session_state.chat_history.append({
            "role": "bot",
            "content": reply,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    except requests.exceptions.RequestException as e:
        st.session_state.chat_history.append({
            "role": "bot",
            "content": f" Error communicating with backend: {str(e)}",
            "timestamp": timestamp
        })
