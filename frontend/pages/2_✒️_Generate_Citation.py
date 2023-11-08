import streamlit as st
import base64
from src.utils import page_init
import requests

# st.set_page_config(initial_sidebar_state='collapsed')
page_init()
st.markdown("# Generate Citations")

st.markdown("## Upload PDF")
uploaded =  st.file_uploader("Upload", accept_multiple_files=True)


st.markdown("## Text to cite")
the_text = st.text_input("Case Title") 
if uploaded and the_text:
    clicked = st.button("Search For Citation")
    if clicked:
        files = []
        # for file in uploaded:
        #     files.append(('files', (file.name, file.read())))
        # response = requests.post('https://api.jugalbandi.ai/upload-files', files=files).json()
        # print(response)

        # if 'uuid_number' in response.keys():
        #     uid = response['uuid_number']
        input = "Find the statement that relates to the following statement the most if there is nothing similar inform me, the statement: "+ the_text
        #     response = requests.get(f"https://api.jugalbandi.ai/query-with-langchain-gpt3-5?query_string={input}&uuid_number={uid}").json()
        uid = '777c92f6-7617-11ee-b88c-42004e494300'
        response = requests.get(f"https://550c-35-247-99-72.ngrok-free.app/?query_string={input}&uuid_number={uid}").json()
        input = "Return only one word, the year of the case"
        response2 = requests.get(f"https://550c-35-247-99-72.ngrok-free.app/?query_string={input}&uuid_number={uid}").json()
        st.write(response['answer'])
        st.write(f"Citation Format: {response['source_text'][0]['source_text_name'][:-5] }({response2['answer']})")
            
        
