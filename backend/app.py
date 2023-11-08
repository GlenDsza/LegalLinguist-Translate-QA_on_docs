# MAIN CODE

from transformers import (
    GenerationConfig,
    pipeline,
)
from langchain.vectorstores import Chroma
import os
import logging
import click
import torch
from langchain.chains import RetrievalQA
from langchain.embeddings import HuggingFaceInstructEmbeddings
from langchain.llms import HuggingFacePipeline
# for streaming response
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.callbacks.manager import CallbackManager

from constants import EMBEDDING_MODEL_NAME, PERSIST_DIRECTORY, CHROMA_SETTINGS, MODEL_ID, MODEL_BASENAME, MODELS_PATH
from load_model import load_quantized_model_gguf_ggml
from constants import get_prompt_template

callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])


def retrieval_qa_pipline(device_type="cuda", use_history=True, promptTemplate_type="mistral"):

    embeddings = HuggingFaceInstructEmbeddings(
        model_name=EMBEDDING_MODEL_NAME, model_kwargs={"device": "cuda"})
    db = Chroma(
        persist_directory=PERSIST_DIRECTORY,
        embedding_function=embeddings,
        client_settings=CHROMA_SETTINGS
    )
    retriever = db.as_retriever()

    prompt, memory = get_prompt_template(
        promptTemplate_type, history=use_history)

    llm = load_quantized_model_gguf_ggml(
        MODEL_ID, MODEL_BASENAME, "cuda", logging)

    if use_history:
        qa = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",  # try other chains types as well. refine, map_reduce, map_rerank
            retriever=retriever,
            return_source_documents=True,  # verbose=True,
            callbacks=callback_manager,
            chain_type_kwargs={"prompt": prompt, "memory": memory},
        )
    else:
        qa = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",  # try other chains types as well. refine, map_reduce, map_rerank
            retriever=retriever,
            return_source_documents=True,  # verbose=True,
            callbacks=callback_manager,
            chain_type_kwargs={
                "prompt": prompt,
            },
        )

    return qa


def main(device_type="cuda", show_sources=True, use_history=True, model_type="mistral"):
    if not os.path.exists(MODELS_PATH):
        os.mkdir(MODELS_PATH)

    qa = retrieval_qa_pipline()
    # Interactive questions and answers
    while True:
        query = input("\nEnter a query: ")
        if query == "exit":
            break
        # Get the answer from the chain
        res = qa(query)
        answer, docs = res["result"], res["source_documents"]

        # Print the result
        print("\n\n> Question:")
        print(query)
        print("\n> Answer:")
        print(answer)

        if show_sources:  # this is a flag that you can set to disable showing answers.
            # # Print the relevant sources used for the answer
            print(
                "----------------------------------SOURCE DOCUMENTS---------------------------")
            for document in docs:
                print("\n> " + document.metadata["source"] + ":")
                print(document.page_content)
            print(
                "----------------------------------SOURCE DOCUMENTS---------------------------")
