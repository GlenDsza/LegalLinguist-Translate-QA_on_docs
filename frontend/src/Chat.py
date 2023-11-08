import streamlit as st
import requests
import base64
import time
from src.database import upload_file_details, get_db, delete_all_records
from src.utils import db

conn = get_db()
language_codes = {
    'Arabic': 'ar_AR',
    'Czech': 'cs_CZ',
    'German': 'de_DE',
    'English': 'en_XX',
    'Spanish': 'es_XX',
    'Estonian': 'et_EE',
    'Finnish': 'fi_FI',
    'French': 'fr_XX',
    'Gujarati': 'gu_IN',
    'Hindi': 'hi_IN',
    'Italian': 'it_IT',
    'Japanese': 'ja_XX',
    'Kazakh': 'kk_KZ',
    'Korean': 'ko_KR',
    'Lithuanian': 'lt_LT',
    'Latvian': 'lv_LV',
    'Burmese': 'my_MM',
    'Nepali': 'ne_NP',
    'Dutch': 'nl_XX',
    'Romanian': 'ro_RO',
    'Russian': 'ru_RU',
    'Sinhala': 'si_LK',
    'Turkish': 'tr_TR',
    'Vietnamese': 'vi_VN',
    'Chinese': 'zh_CN',
    'Afrikaans': 'af_ZA',
    'Azerbaijani': 'az_AZ',
    'Bengali': 'bn_IN',
    'Persian': 'fa_IR',
    'Hebrew': 'he_IL',
    'Croatian': 'hr_HR',
    'Indonesian': 'id_ID',
    'Georgian': 'ka_GE',
    'Khmer': 'km_KH',
    'Macedonian': 'mk_MK',
    'Malayalam': 'ml_IN',
    'Mongolian': 'mn_MN',
    'Marathi': 'mr_IN',
    'Polish': 'pl_PL',
    'Pashto': 'ps_AF',
    'Portuguese': 'pt_XX',
    'Swedish': 'sv_SE',
    'Swahili': 'sw_KE',
    'Tamil': 'ta_IN',
    'Telugu': 'te_IN',
    'Thai': 'th_TH',
    'Tagalog': 'tl_XX',
    'Ukrainian': 'uk_UA',
    'Urdu': 'ur_PK',
    'Xhosa': 'xh_ZA',
    'Galician': 'gl_ES',
    'Slovene': 'sl_SI'
}


class Chat():
    def __init__(self, processinput=lambda x: print(x)) -> None:

        self.processinput = processinput
        self.input = None
        self.URL = 'https://6952-34-83-51-35.ngrok-free.app'

        if 'doc' not in st.session_state:
            st.session_state['doc'] = None

        if 'messages' not in st.session_state:
            st.session_state['messages'] = []
            self.message_by_assistant(
                'Hello there! I am your personal assistant. How can I help you?')
            self.message_by_assistant('Upload your file here:', type='file')

    def set_processinput(self, processinput):
        self.processinput = processinput

    
    def create_embeddings(self, urls):
        # send pdf files to the api
        # https://api.jugalbandi.ai/upload-files
        files = []
        for url in urls:
            response = requests.get(url)
            filename = url.split('/')[-1]
            files.append(('files', (filename, response.content)))
        response = requests.post('https://api.jugalbandi.ai/upload-files', files=files).json()
        if 'uuid_number' in response.keys():
            return response['uuid_number']
        return "Error"
    
    uploaded_files = []
    def render_ui(self):
        self.handle_input()

        for message in st.session_state['messages']:
            with st.chat_message(message['role']):
                if message['type'] == 'text':
                    st.write(message['text'])

                elif message['type'] == 'file':
                    temp_file = st.file_uploader(
                        message['text'], accept_multiple_files=True)
                    if temp_file is not None:
                        self.uploaded_files.append(temp_file)
                        st.session_state['language']  = st.selectbox('Enter the language', language_codes.keys())


                elif message['type'] == 'image':
                    if message['label'] != '':
                        with st.expander(message['label']):
                            st.image(message['image'])
                    else:
                        st.image(message['image'])

                elif message['type'] == 'glossary':
                    st.write(message['text'])
                    if help != '':
                        with st.expander("Glossary"):
                            st.markdown( message['help'],unsafe_allow_html=True)
                        


    def upload_file(self, uploaded_files):
        # single_file = st.session_state['doc'][index]
        if uploaded_files is None or len(uploaded_files) == 0:
            st.write("File not selected")
            return
        files=[]

        for file in uploaded_files:
            files.append(('files', (file.name, file.read())))
        response = requests.post(
            f'{self.URL}/uploadfiles',
            files= files,
            data={
                'email': st.session_state['verif_email'],
                'lang': language_codes[st.session_state['language']],
            }
        )
        print(response.text)
        result = response.json()
        
        to_insert = []
        links = []
        for file in uploaded_files:
            to_insert.append({
        'email': st.session_state['verif_email'],
        'fileUrl': f'https://railrakshak.s3.ap-south-1.amazonaws.com/{st.session_state["verif_email"]}{file.name}'
    })
            links.append(f'https://railrakshak.s3.ap-south-1.amazonaws.com/{st.session_state["verif_email"]}{file.name}')
        if result['SUCCESS'] == 'PDF CREATED':
            st.success("File uploaded successfully!")
            

        upload_file_details(
            db,  to_insert
        )
        id = self.create_embeddings(links)
        return(id)



        # # print(response.json())
        # if response.status_code == 200:
        #     st.write("You've successfully uploaded a file!")
        # else:
        #     st.write("Failed to upload file.")

        

    def handle_input(self):
        self.input = st.chat_input('Type a message...')
        if self.input and 'id' not in st.session_state.keys():
            st.session_state['messages'].append({
                'type': 'text',
                'text': self.input,
                'role': 'user',
            })
            st.session_state['messages'].append({
                'type': 'text',
                'text': 'Please upload your file first.',
                'role': 'assistant',
            })
        elif self.input:
            st.session_state['messages'].append({
                'type': 'text',
                'text': self.input,
                'role': 'user',
            })
        self.processinput(self.input)

    def message_by_user(self, message):
        st.session_state['messages'].append({
            'type': 'text',
            'text': message,
            'role': 'user',
        })

    def message_by_assistant(self, message, type='text', label='', help=''):
        if type == 'file':
            st.session_state['messages'].append({
                'type': 'file',
                'text': message,
                'role': 'assistant',
            })
        elif type == 'text':
            st.session_state['messages'].append({
                'type': 'text',
                'text': message,
                'role': 'assistant',
            })
        elif type == 'image':
            st.session_state['messages'].append({
                'type': 'image',
                'image': message,
                'role': 'assistant',
                'label': label
            })
        elif type=='glossary':
            st.session_state['messages'].append({
                'type': 'glossary',
                'text': message,
                'role': 'assistant',
                'help': help
            })

    def clear_chat(self):
        st.session_state['messages'] = []
        st.session_state['doc'] = None
        del st.session_state['show_anim']
        self.message_by_assistant(
            'Hello there! I am your personal assistant. How can I help you?')
        self.message_by_assistant('Upload your file here:', type='file')
        delete_all_records(conn, st.session_state['verif_email'])

    def upload_create_embeding(self):
        if self.uploaded_files is not None and len(self.uploaded_files) > 0:
            with st.spinner("Uploading and processing the file..."):
                st.session_state['id'] =self.upload_file(self.uploaded_files[-1])
        # st.session_state['id'] ='fe11f67c-75e4-11ee-b88c-42004e494300'
        i = 0



        while i < len(st.session_state['messages']):
            if st.session_state['messages'][i]['type'] ==  'file':
                del st.session_state['messages'][i]
            else:
                i += 1

# pdf = requests.get(
#     'https://railrakshak.s3.ap-south-1.amazonaws.com/AFFAIRE+C.P.+ET+M.N.+c.+FRANCE.pdf').content
# pdf_base64 = base64.b64encode(pdf).decode('utf-8')
# st.markdown(
#     F'<iframe src="data:application/pdf;base64,{pdf_base64}" width="700" height="1000" type="application/pdf"></iframe>', unsafe_allow_html=True)

