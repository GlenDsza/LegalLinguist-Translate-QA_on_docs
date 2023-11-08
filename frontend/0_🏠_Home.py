import streamlit as st
from src.Chat import Chat
from src.utils import page_init
import src.pdfops as pdfops
from streamlit_lottie import st_lottie
import requests
import io
import json
import spacy

# st.set_page_config(initial_sidebar_state='collapsed')

page_init()
st.session_state['verif_email'] = 'kenneth@mail.com'


chat = Chat()


def processinput(input: str):
   if input and 'id' in st.session_state.keys():
    uid = st.session_state['id']
    response = requests.get(f"https://550c-35-247-99-72.ngrok-free.app/?query_string={input}&uuid_number={uid}").json()
    
    sample_text =  response['answer']
    with open('glossary.json', 'r') as f:
        glossary = f.read()
    glossary = json.loads(glossary)
    
    nlp = spacy.load("en_core_web_lg") 

    def preprocess(text):
        # remove stop words and lemmatize the text
        excluded_tags = {"NOUN", "PROPN"}
        doc = nlp(text)
        filtered_tokens = []
        for token in doc:
            if token.is_stop or token.is_punct or token.pos_ not in excluded_tags:
                continue
            filtered_tokens.append(token.lemma_)
        
        return (filtered_tokens)
    helper = ''
    pp = set(preprocess(sample_text))
    for i in pp:
        for j in glossary.keys():
            if i in j:
                helper +="<b>" +j + " : " + "</b>" + glossary[j] + "<br/> " 
    
   
    
    if len(response['source_text']) == 0:
        chat.message_by_assistant(sample_text, type='glossary', help=helper)
        return
    
    
    
    sauce = response['source_text'][0]
    # st.write(response)
    toFind = sauce['chunks'][0]
    # toFind = 'The subject patent claims the use of Bacillus thuringiensisstrain and development of two genes designated Cry2Aa and Cry2Ab'
    
    fileUrl = f'https://railrakshak.s3.ap-south-1.amazonaws.com/{sauce["source_text_name"]}'
    pdfResp = requests.get(fileUrl)
    stream = io.BytesIO(pdfResp.content)
    chat.message_by_assistant(sample_text, type='glossary', help=helper)
    pdfops.search_and_highlight(chat, stream, toFind.split('.')[0], True)
    
   



chat.set_processinput(processinput)
if 'show_anim' not in st.session_state:
    st.session_state['show_anim'] = True
    st_lottie("https://lottie.host/4168a67a-474d-4939-a94f-cc090b508bea/gzny9gII5b.json",
              speed=0.8, height=300, key="initial", loop=False)

clearbtn = st.sidebar.button(':broom: Clear Chat')
if clearbtn:
    chat.clear_chat()


uploadbtn = st.sidebar.button(':heavy_plus_sign: Create Embeddings')
if uploadbtn:
    chat.upload_create_embeding()

chat.render_ui()


# * Notes
# doc can be accessed using st.session_state['doc']
# doc is array of uploaded docs
# to add messages use the method 'message_by_assistant(text)'
