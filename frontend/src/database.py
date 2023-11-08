import streamlit as st
import hmac
import hashlib
from pymongo import MongoClient
import pandas as pd

@st.cache_resource
def get_db():
    return MongoClient(st.secrets['dbkey'])


def hash(msg):
    return hmac.new(str.encode(st.secrets['hashkey']), str.encode(msg), hashlib.sha256).hexdigest()


def compare_hash(msg, hashed):
    return hmac.compare_digest(hash(msg), hashed)


def register_user(conn, name, email, password):
    db = conn['test']
    users = db['users']
    if users.find_one({'email': email}):
        return False
    users.insert_one({
        'name': name,
        'email': email,
        'password': hash(password)
    })
    return True


def login_user(conn, email, password):
    db = conn['test']
    users = db['users']

    user = users.find_one({'email': email})
    print(user)
    if not user:
        return False
    if compare_hash(password, user['password']):
        return True
    return False


def upload_file_details(conn, links):
    db = conn['test']
    files = db['files']

    files.insert_many(links)


def get_doc_names(conn, email):
    db = conn['test']
    files = db['files']
    list_of_files = files.find({'email': email})
    l = list(list_of_files)
    if len(l) >0:
        return(list(pd.DataFrame(l)['fileUrl']))
    else:
        return([])

def delete_all_records(conn, email):
    db = conn['test']
    files = db['files']
    files.delete_many({'email': email})