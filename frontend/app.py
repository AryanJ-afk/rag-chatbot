import streamlit as st
import requests
import uuid

import os
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Doc Chat", page_icon="📄")
st.title("Technical Documentation Chatbot")

if "user_id" not in st.session_state:
    st.session_state.user_id = "aryan_jha"
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []
    
with st.sidebar:
    st.header("Documents")
    uploaded = st.file_uploader("Upload a PDF", type=["pdf"])
    if uploaded is not None and uploaded.name not in st.session_state.uploaded_files:
        # POST to /upload
        files = {"file": (uploaded.name, uploaded.getvalue(), "application/pdf")}
        data = {"user_id": st.session_state.user_id}
        with st.spinner("Uploading and ingesting..."):
            response = requests.post(f"{BACKEND_URL}/upload", files=files, data=data)
        if response.status_code == 200:
            st.session_state.uploaded_files.append(uploaded.name)
            st.success(f"Uploaded {uploaded.name}")
        else:
            st.error(f"Upload failed: {response.text}")
    
    st.subheader("Uploaded")
    for f in st.session_state.uploaded_files:
        st.write(f"• {f}")

user_id_input = st.sidebar.text_input("Your User ID", value=st.session_state.user_id)
if user_id_input != st.session_state.user_id:
    st.session_state.user_id = user_id_input
    st.session_state.messages = []  # clear chat when switching users
    st.session_state.uploaded_files = []
    st.session_state.thread_id = str(uuid.uuid4())  # fresh thread
    st.rerun()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            with st.expander("Sources"):
                for s in msg["sources"]:
                    st.write(f"• {s['source']}, page {s['page']}")

if prompt := st.chat_input("Ask a question about your documents"):
    # display user message immediately
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # call backend
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            payload = {
                "query": prompt,
                "user_id": st.session_state.user_id,
                "thread_id": st.session_state.thread_id,
            }
            response = requests.post(f"{BACKEND_URL}/query", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            answer = data["answer"]
            sources = data["sources"]
            st.markdown(answer)
            if sources:
                with st.expander("Sources"):
                    for s in sources:
                        st.write(f"• {s['source']}, page {s['page']}")
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "sources": sources,
            })
        else:
            st.error(f"Query failed: {response.text}")
            
if st.sidebar.button("New Chat"):
    st.session_state.thread_id = str(uuid.uuid4())
    st.session_state.messages = []
    st.rerun()