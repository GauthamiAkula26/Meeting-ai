# Meeting AI Copilot

A fast, cloud-safe Streamlit app for meeting transcript analysis.

## Features

- Upload a `.txt` meeting transcript
- Extract decisions
- Extract action items
- Extract risks / blockers
- Ask questions over the transcript
- Optional OpenAI-enhanced answers

## Why this version deploys faster

This version uses lightweight BM25-based transcript retrieval instead of heavy embedding models. That makes it much easier to deploy on Streamlit Community Cloud.

## Repo structure

```bash
.
├── app.py
├── requirements.txt
├── runtime.txt
├── data/
│   └── sample_meeting.txt
└── utils/
    ├── extractors.py
    ├── llm.py
    └── nlp.py
