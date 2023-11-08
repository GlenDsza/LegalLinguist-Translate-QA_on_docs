import streamlit as st
import fitz
import re

def normalize_text(text):
    text = re.sub(r"\s+", "", text)
    text.replace(" ", "")
    text = text.lower()
    return text


def search_and_highlight(chat, doc, text, isStream = False):
    pdf_doc = fitz.open(stream=doc.read(), filetype="pdf") if not isStream else fitz.open(stream=doc, filetype="pdf")
    found_something = False
    ogtext = text
    text = normalize_text(text)

    for page in pdf_doc:
        # quads = page.search_for(text, quads=True)
        # if quads:
        #     found_something = True
        #     page.add_highlight_annot(quads)
        #     chat.message_by_assistant(
        #         page.get_pixmap().tobytes('png'), type='image', label="Found" +
        #         " matches in page " + str(page.number + 1) + ".")
        pagetext = page.get_text("text")
        pagetext = normalize_text(pagetext)
        start = pagetext.find(text)
        if start != -1:
            word_arr_forward = ogtext.split(' ')
            word_arr_backward = ogtext.split(' ')
            cpyog = ogtext
            while len(word_arr_backward) > 0:
                quads = page.search_for(ogtext, quads=True)
                if quads:
                    page.add_highlight_annot(quads)
                    break
                else:
                    ogtext = ' '.join(word_arr_backward[1:])
                    word_arr_backward = word_arr_backward[1:]
            ogtext = cpyog
            while len(word_arr_forward) > 0:
                quads = page.search_for(ogtext, quads=True)
                if quads:
                    page.add_highlight_annot(quads)
                    break
                else:
                    ogtext = ' '.join(word_arr_forward[:-1])
                    word_arr_forward = word_arr_forward[:-1]
            chat.message_by_assistant(
                page.get_pixmap().tobytes('png'), type='image', label="Source:" +
                " Page " + str(page.number + 1) + ".")
            found_something = True

    
    
    if not found_something:
        chat.message_by_assistant("No matches found.")


def search_logic(chat, input):
    try:
        doc_index = int(input.split(' ')[1]) - 1
        if doc_index >= len(st.session_state['doc']):
            raise ValueError

        # search string
        search_string = ' '.join(input.split(' ')[2:])
        chat.message_by_assistant(
            "Searching for " + search_string + " in file " + str(doc_index + 1))
        search_and_highlight(chat,
                             st.session_state['doc'][doc_index], search_string)

    except ValueError:
        chat.message_by_assistant(
            f'You have uploaded only {len(st.session_state["doc"])} files. Please enter a valid index.')
        return
