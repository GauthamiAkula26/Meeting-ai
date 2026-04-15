import os
from pathlib import Path
from typing import List, Dict

import streamlit as st
from dotenv import load_dotenv

from utils.extractors import (
    extract_action_items,
    extract_decisions,
    extract_risks,
    build_overview_summary,
)
from utils.llm import llm_answer
from utils.nlp import chunk_text, search_chunks

load_dotenv()

st.set_page_config(
    page_title="Meeting AI Copilot",
    page_icon="🧠",
    layout="wide",
)

APP_TITLE = "Meeting AI Copilot"
DATA_DIR = Path("data")
SAMPLE_FILE = DATA_DIR / "sample_meeting.txt"


def read_text_file(uploaded_file) -> str:
    return uploaded_file.read().decode("utf-8", errors="ignore")


def load_sample_text() -> str:
    if SAMPLE_FILE.exists():
        return SAMPLE_FILE.read_text(encoding="utf-8")
    return ""


def prepare_meeting(text: str) -> Dict:
    chunks = chunk_text(text, chunk_size=900, overlap=120)
    decisions = extract_decisions(text)
    actions = extract_action_items(text)
    risks = extract_risks(text)
    overview = build_overview_summary(text, decisions, actions, risks)

    return {
        "raw_text": text,
        "chunks": chunks,
        "decisions": decisions,
        "actions": actions,
        "risks": risks,
        "overview": overview,
    }


def render_bullet_block(title: str, items: List[str], empty_msg: str):
    st.subheader(title)
    if items:
        for item in items:
            st.markdown(f"- {item}")
    else:
        st.info(empty_msg)


def render_sidebar():
    with st.sidebar:
        st.header("Settings")
        st.caption("Fast cloud-safe version")
        use_openai = st.checkbox("Use OpenAI for enhanced answers", value=False)
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            value=os.getenv("OPENAI_API_KEY", ""),
            help="Optional. Leave blank to use local retrieval-only mode."
        )
        top_k = st.slider("Top matching transcript chunks", 3, 8, 5)
        st.markdown("---")
        st.info("This version uses lightweight transcript search for fast deployment.")
    return use_openai, api_key, top_k


def main():
    st.title(APP_TITLE)
    st.caption("Upload a meeting transcript, extract decisions/action items/risks, and ask questions.")

    use_openai, api_key, top_k = render_sidebar()

    if "meeting_data" not in st.session_state:
        st.session_state.meeting_data = None

    source_tab, insights_tab, ask_tab, transcript_tab = st.tabs(
        ["Source", "Insights", "Ask", "Transcript"]
    )

    with source_tab:
        st.subheader("Choose meeting source")
        use_sample = st.checkbox("Use included sample transcript", value=True)

        uploaded_file = st.file_uploader(
            "Upload transcript (.txt)",
            type=["txt"],
            help="Upload a plain text transcript file."
        )

        if st.button("Process Meeting", use_container_width=True):
            text = ""
            if uploaded_file is not None:
                text = read_text_file(uploaded_file)
            elif use_sample:
                text = load_sample_text()

            if not text.strip():
                st.error("No transcript text found. Upload a .txt file or use the included sample.")
            else:
                with st.spinner("Processing transcript..."):
                    st.session_state.meeting_data = prepare_meeting(text)
                st.success("Meeting processed successfully.")

        if st.session_state.meeting_data is not None:
            md = st.session_state.meeting_data
            c1, c2, c3 = st.columns(3)
            c1.metric("Transcript Chunks", len(md["chunks"]))
            c2.metric("Decisions Found", len(md["decisions"]))
            c3.metric("Action Items Found", len(md["actions"]))

    with insights_tab:
        if st.session_state.meeting_data is None:
            st.info("Process a meeting first.")
        else:
            md = st.session_state.meeting_data
            st.subheader("Overview")
            st.write(md["overview"])

            col1, col2 = st.columns(2)
            with col1:
                render_bullet_block(
                    "Decisions",
                    md["decisions"],
                    "No decisions were extracted."
                )
                render_bullet_block(
                    "Risks / Blockers",
                    md["risks"],
                    "No risks or blockers were extracted."
                )
            with col2:
                render_bullet_block(
                    "Action Items",
                    md["actions"],
                    "No action items were extracted."
                )

    with ask_tab:
        if st.session_state.meeting_data is None:
            st.info("Process a meeting first.")
        else:
            md = st.session_state.meeting_data

            question = st.text_input(
                "Ask a question about the meeting",
                placeholder="What are the key decisions?"
            )

            if st.button("Ask Question", use_container_width=True):
                if not question.strip():
                    st.error("Please enter a question.")
                else:
                    with st.spinner("Searching transcript..."):
                        results = search_chunks(
                            question=question,
                            chunks=md["chunks"],
                            top_k=top_k,
                        )

                    context = "\n\n---\n\n".join(
                        [f"Chunk {i+1}:\n{item['text']}" for i, item in enumerate(results)]
                    )

                    if use_openai and api_key.strip():
                        with st.spinner("Generating enhanced answer..."):
                            answer = llm_answer(
                                question=question,
                                context=context,
                                api_key=api_key.strip()
                            )
                    else:
                        answer = (
                            "Top matching transcript evidence found below.\n\n"
                            "Use the matching chunks to answer the question."
                        )

                    st.subheader("Answer")
                    st.write(answer)

                    st.subheader("Matching Transcript Chunks")
                    for idx, item in enumerate(results, start=1):
                        with st.expander(
                            f"{idx}. Score: {item['score']:.4f}",
                            expanded=(idx == 1)
                        ):
                            st.write(item["text"])

    with transcript_tab:
        if st.session_state.meeting_data is None:
            st.info("Process a meeting first.")
        else:
            st.subheader("Full Transcript")
            st.text_area(
                "Transcript text",
                value=st.session_state.meeting_data["raw_text"],
                height=500
            )


if __name__ == "__main__":
    main()
