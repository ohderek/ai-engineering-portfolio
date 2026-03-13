"""
Streamlit UI for the Support RAG Bot.

Usage:
  streamlit run app.py
"""

import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Support RAG Bot", page_icon="🤖", layout="centered")

st.title("🤖 Support RAG Bot")
st.caption("Ask questions about your documentation.")


# ── Sidebar: ingestion ────────────────────────────────────────────────────────
with st.sidebar:
    st.header("📂 Load Documents")
    doc_path = st.text_input(
        "File or folder path",
        placeholder="/path/to/docs/ or file.md",
    )
    if st.button("Ingest", use_container_width=True):
        path = Path(doc_path.strip())
        if not doc_path.strip():
            st.error("Enter a path first.")
        elif not path.exists():
            st.error(f"Path not found: {path}")
        else:
            with st.spinner("Loading and embedding documents…"):
                from src.ingest import ingest
                ingest(str(path))
            st.success("Ingestion complete!")
            st.session_state.vectorstore_ready = True

    st.divider()

    # Load existing vector store on startup
    if "vectorstore_ready" not in st.session_state:
        vector_db = Path("./vector_db")
        if vector_db.exists() and any(vector_db.iterdir()):
            st.session_state.vectorstore_ready = True
        else:
            st.session_state.vectorstore_ready = False

    if st.session_state.vectorstore_ready:
        st.success("Vector store loaded.")
    else:
        st.info("Ingest documents to get started.")

    show_sources = st.toggle("Show source chunks", value=False)


# ── Chat ──────────────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            with st.expander("Source chunks"):
                for i, chunk in enumerate(msg["sources"], 1):
                    st.caption(f"**[{i}]** {chunk}")

if prompt := st.chat_input("Ask a question…", disabled=not st.session_state.vectorstore_ready):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            from src.ingest import load_existing
            from src.chain import build_chain

            vectorstore = load_existing()
            chain, retriever = build_chain(vectorstore)
            answer = chain.invoke(prompt)

            sources = []
            if show_sources:
                docs = retriever.invoke(prompt)
                sources = [doc.page_content[:300] for doc in docs]

        st.markdown(answer)
        if sources:
            with st.expander("Source chunks"):
                for i, chunk in enumerate(sources, 1):
                    st.caption(f"**[{i}]** {chunk}")

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources,
    })
