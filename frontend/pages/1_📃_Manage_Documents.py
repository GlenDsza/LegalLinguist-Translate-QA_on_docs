import streamlit as st
import base64
from src.utils import page_init
from src.database import get_doc_names, get_db
import pandas as pd
import requests
from src.Chat import Chat
# st.set_page_config(initial_sidebar_state='collapsed')
st.session_state['verif_email'] = 'kenneth@mail.com'

page_init()
chat = Chat()

st.markdown("# Manage Documents")
conn = get_db()
filesUrls = get_doc_names(conn, st.session_state['verif_email'])
name_len = len(st.session_state['verif_email'])
for i in filesUrls:
    with st.expander(i.split('/')[-1].replace(st.session_state['verif_email'], '')):
        pdf = requests.get(i).content
        pdf_base64 = base64.b64encode(pdf).decode('utf-8')
        st.markdown(
    F'<iframe src="data:application/pdf;base64,{pdf_base64}" width="100%" height="1000" type="application/pdf"></iframe>', unsafe_allow_html=True)

if len(filesUrls) == 0:
    st.write("No documents uploaded yet.")

if len(filesUrls) > 0:
    clearbtn= st.button("Clear All")
    if clearbtn:
        chat.clear_chat()