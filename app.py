import streamlit as st
# --- IMPORTS UPDATED FOR STANDARD PROJECT STRUCTURE ---
from src.config.config import GeminiConfig, AppConfig
from src.models.llm import GeminiClient
from src.utils.file_processor import FileProcessor
from src.utils.retrieval import VectorRetriever, DocumentProcessor
from src.utils.websearch import WebSearcher
from src.utils.tts import autoplay_audio
from src.config.modes import CHAT_MODES
from src.config.personas import PERSONAS
from src.config.response_modes import RESPONSE_MODES, DEFAULT_RESPONSE_MODE
# --- Standard Library Imports ---
from datetime import datetime
import logging
from typing import Optional
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Helper Functions ---

def init_session():
    """Initialize all required session state variables."""
    default_state = {
        "chats": {}, "active_chat": None, "uploaded_files": [],
        "file_processor": FileProcessor(), "model_initialized": False, "gemini_client": None,
        "retriever": VectorRetriever(), "rag_index_ready": False,
        "web_searcher": WebSearcher()
    }
    for key, value in default_state.items():
        if key not in st.session_state:
            st.session_state[key] = value

def build_rag_index():
    """Builds the RAG index from ALL uploaded documents."""
    if st.session_state.uploaded_files:
        with st.spinner("Analyzing and indexing documents..."):
            try:
                all_chunks = []
                doc_processor = DocumentProcessor()
                for file_info in st.session_state.uploaded_files:
                    text = file_info['data'].get('text', '')
                    if text:
                        chunks = doc_processor.process(text, {"name": file_info['file'].name})
                        all_chunks.extend(chunks)
                
                if all_chunks:
                    st.session_state.retriever.build_index(all_chunks)
                    st.session_state.rag_index_ready = True
                else:
                    st.session_state.rag_index_ready = False
            except Exception as e:
                st.error(f"Failed to build document index: {e}")
                st.session_state.rag_index_ready = False
    else:
        st.session_state.rag_index_ready = False

def handle_time_query(prompt: str) -> Optional[str]:
    """Checks for and handles time-related queries directly."""
    if re.search(r'\b(what is|what\'s|current) time\b', prompt, re.IGNORECASE):
        return f"The current time is {datetime.now().strftime('%I:%M %p')}."
    return None

# --- Main Application Logic ---

init_session()

st.set_page_config(page_title="BusinAI", page_icon="💼", layout="wide")

# --- Sidebar UI ---
with st.sidebar:
    st.title("💼 BusinAI")
    st.info(f"Model: `{GeminiConfig.MODEL_NAME}`")

    uploaded_files = st.file_uploader(
        "Upload Documents", type=AppConfig.ALLOWED_FILE_TYPES,
        accept_multiple_files=True, help=f"Max size: {AppConfig.MAX_FILE_SIZE_MB}MB"
    )
    
    if uploaded_files:
        new_files_uploaded = False
        existing_files = {f"{f['file'].name}-{f['file'].size}" for f in st.session_state.uploaded_files}
        for file in uploaded_files:
            file_id = f"{file.name}-{file.size}"
            if file_id not in existing_files:
                st.session_state.uploaded_files.append({"file": file, "data": {}})
                new_files_uploaded = True
        
        if new_files_uploaded:
            with st.spinner("Processing files..."):
                for file_info in st.session_state.uploaded_files:
                    if not file_info["data"]:
                        file_info["data"] = st.session_state.file_processor.process_uploaded_file(file_info["file"])
            build_rag_index()
            st.rerun()

    st.subheader("Chat History")
    sorted_chats = sorted(st.session_state.chats.items(), key=lambda i: i[1].get('starred', False), reverse=True)
    for chat_id, chat_data in sorted_chats:
        icon = "⭐" if chat_data.get('starred') else "💬"
        if st.button(f"{icon} {chat_id}", key=f"load_{chat_id}"):
            st.session_state.active_chat = chat_id
            st.rerun()

# --- Main Chat Area UI ---
col1, col2 = st.columns([0.8, 0.2])
with col1:
    st.title("BusinAI")
with col2:
    if st.button("➕ New Chat", use_container_width=True):
        new_id = f"Chat-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        st.session_state.chats[new_id] = {"messages": [], "starred": False, "created_at": datetime.now().isoformat()}
        st.session_state.active_chat = new_id
        st.rerun()

if not st.session_state.get("model_initialized"):
    with st.spinner("Initializing AI model..."):
        try:
            st.session_state.gemini_client = GeminiClient()
            st.session_state.model_initialized = True
        except Exception as e:
            st.error(f"Fatal Error: Failed to initialize AI model: {e}")
            st.stop()

if not st.session_state.active_chat:
    st.info("Start a new chat or select one from the history in the sidebar.")
else:
    current_chat = st.session_state.chats[st.session_state.active_chat]
    
    header_cols = st.columns([0.6, 0.2, 0.2])
    with header_cols[0]: st.subheader(f"Active Chat: {st.session_state.active_chat}")
    with header_cols[1]:
        if st.button("⭐ Star" if not current_chat.get('starred') else "🌟 Unstar", use_container_width=True):
            current_chat['starred'] = not current_chat.get('starred', False)
            st.rerun()
    with header_cols[2]:
        if st.button("🗑️ Delete Chat", use_container_width=True):
            del st.session_state.chats[st.session_state.active_chat]
            st.session_state.active_chat = None
            st.rerun()
            
    # --- ADDED UI ELEMENT: Response Mode ---
    response_mode = st.radio(
        "Response Mode:",
        options=list(RESPONSE_MODES.keys()),
        key="response_mode",
        horizontal=True,
        index=list(RESPONSE_MODES.keys()).index(DEFAULT_RESPONSE_MODE)
    )
    
    st.divider()

    for msg in current_chat["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant": autoplay_audio(msg["content"])

    if prompt := st.chat_input("Ask a question..."):
        current_chat["messages"].append({"role": "user", "content": prompt})
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = handle_time_query(prompt)
                if not response:
                    # --- PASS NEW CONTEXT TO AI ---
                    context = {
                        "response_mode_instruction": RESPONSE_MODES[response_mode]["instruction"]
                    }
                    
                    if st.session_state.rag_index_ready:
                        retrieved_docs = st.session_state.retriever.retrieve(prompt)
                        if retrieved_docs:
                            context["retrieved_context"] = "\n\n".join([r[0] for r in retrieved_docs])
                    
                    search_results = st.session_state.web_searcher.search(prompt)
                    if search_results:
                        web_context = "Based on a web search:\n" + "\n".join([f"- {res['snippet']}" for res in search_results])
                        if "retrieved_context" in context:
                            context["retrieved_context"] += "\n\n" + web_context
                        else:
                            context["retrieved_context"] = web_context
                    
                    history = [{"role": "model" if m["role"] == "assistant" else "user", "parts": [{"text": m["content"]}]} for m in current_chat["messages"][:-1]]
                    response = st.session_state.gemini_client.generate(prompt=prompt, history=history, context=context)
                
                st.markdown(response)
                current_chat["messages"].append({"role": "assistant", "content": response})
        st.rerun()