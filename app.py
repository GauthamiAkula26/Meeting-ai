import streamlit as st
from utils.nlp import *
from utils.extractors import *

st.title('Meeting AI Copilot')
file=st.file_uploader('Upload transcript',type=['txt'])
text=file.read().decode() if file else open('data/sample_meeting.txt').read()
if st.button('Process'):
 chunks=chunk_text(text)
 emb=build_embeddings(chunks)
 st.session_state.data={'chunks':chunks,'emb':emb,'text':text}
 st.success('Processed')
if 'data' in st.session_state:
 st.write('Decisions:',extract_decisions(text))
 st.write('Actions:',extract_action_items(text))
 st.write('Risks:',extract_risks(text))
 q=st.text_input('Ask')
 if st.button('Search'):
  res=search_chunks(q,st.session_state.data['chunks'],st.session_state.data['emb'])
  st.write(res)