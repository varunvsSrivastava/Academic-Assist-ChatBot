# Legacy Streamlit UI (preserved for reference)

import time
from pathlib import Path
import sys

import streamlit as st

# Allow running this file directly (e.g., `streamlit run app/streamlit_app.py`).
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.routes import handle_query
from backend.app.routes import ingest_document
from backend.memory.session_memory import session_memory
from backend.evaluation.metrics import metrics_tracker

# PAGE CONFIG
st.set_page_config(
    page_title="Academic Assistant",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Context-Aware Academic Assistant")
st.caption("Multi-Agent RAG + Self-Improving AI System")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "show_debug" not in st.session_state:
    st.session_state.show_debug = False

if "last_upload_status" not in st.session_state:
    st.session_state.last_upload_status = "No PDFs uploaded yet."

with st.sidebar:
    st.header("⚙️ Settings")

    st.session_state.show_debug = st.toggle(
        "Show Debug Info",
        value=False
    )

    if st.button("🧹 Clear Chat"):
        st.session_state.chat_history = []
        session_memory.clear()
        st.rerun()

    st.divider()
    st.subheader("📄 Knowledge Base")
    uploaded_files = st.file_uploader(
        "Upload academic PDFs",
        type=["pdf"],
        accept_multiple_files=True,
    )

    if st.button("⬆️ Upload and index"):
        if not uploaded_files:
            st.warning("Upload at least one PDF first.")
        else:
            with st.spinner("Indexing documents..."):
                indexed_files = []
                for uploaded_file in uploaded_files:
                    saved_path = ingest_document(uploaded_file.name, uploaded_file.getvalue())
                    indexed_files.append(str(saved_path))

                st.success(f"Indexed {len(indexed_files)} document(s).")
                st.caption("The assistant will now use the uploaded PDFs as retrieval context.")
                st.session_state.last_upload_status = f"Indexed {len(indexed_files)} PDF(s)."

    st.divider()
    st.subheader("📈 Document Status")
    st.caption(st.session_state.last_upload_status)

# USER INPUT
query = st.chat_input("Ask your academic question...")

# PROCESS QUERY
if query:
    with st.spinner("Thinking... 🤖"):
        start_time = time.time()

        result = handle_query(query)

        end_time = time.time()
        latency = round(end_time - start_time, 3)

        answer = result.get("answer", "No answer generated")
        score = result.get("score", 0.0)
        sources = result.get("sources", [])
        route_source = result.get("route_source", "unknown")
        retrieval_mode = result.get("retrieval_mode", "unknown")
        validation_passed = result.get("validation_passed", False)
        validation_score = result.get("validation_score", 0.0)
        validation_reason = result.get("validation_reason", "")

        # Save chat
        st.session_state.chat_history.append({
            "query": query,
            "answer": answer,
            "score": score,
            "sources": sources,
            "latency": latency,
            "route_source": route_source,
            "retrieval_mode": retrieval_mode,
            "validation_passed": validation_passed,
            "validation_score": validation_score,
            "validation_reason": validation_reason,
        })

# DISPLAY CHAT
for chat in st.session_state.chat_history:
    with st.chat_message("user"):
        st.write(chat["query"])

    with st.chat_message("assistant"):
        st.write(chat["answer"])

        col1, col2 = st.columns(2)

        with col1:
            st.caption(f"📊 Score: {round(chat['score'], 2)}")

        with col2:
            st.caption(f"⏱ Latency: {chat['latency']} sec")

        if chat["sources"]:
            st.caption(f"📄 Sources: {', '.join(chat['sources'])}")

        st.caption(f"🧭 Route: {chat.get('route_source', 'unknown')} | Retrieval: {chat.get('retrieval_mode', 'unknown')}")
        st.caption(
            f"✅ Grounded: {'yes' if chat.get('validation_passed') else 'no'} | "
            f"Validation score: {round(chat.get('validation_score', 0.0), 2)}"
        )

        if chat.get("validation_reason"):
            st.caption(f"🔎 {chat['validation_reason']}")

        if st.session_state.show_debug:
            st.code(chat, language="json")

# METRICS DASHBOARD
st.divider()
st.subheader("📊 System Metrics")

col1, col2 = st.columns(2)

with col1:
    st.metric(
        label="Average Score",
        value=round(metrics_tracker.get_average_score(), 3)
    )

with col2:
    st.metric(
        label="Average Latency (sec)",
        value=round(metrics_tracker.get_average_latency(), 3)
    )

# FOOTER
st.divider()
st.caption("🚀 Built with Multi-Agent RAG + LangGraph + Self-Improvement")
