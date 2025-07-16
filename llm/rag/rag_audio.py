"""
A simple RAG to extract information from audio files.
To run it, 
1-  instsall the required libraries (langchain_community, langchain_ollama, faiss, langchain-core, openai-whisper, streamlit)
2- instsall ollama and pull gemma3:4b  and all-minilm:l6-v2   
3- go to rag directory
4- in cmd run 
    streamlit run .\rag_audio.py 
"""


import streamlit as st
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_ollama.llms import OllamaLLM
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
import whisper
import os
import shutil
import re

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

st.set_page_config(page_title="RAG Audio", page_icon=":microphone:")
st.title("RAG Audio")

template = """
You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
Question: {question} 
Context: {context} 
Answer:
"""
audios_directory = "audio"
embeding = OllamaEmbeddings(model="all-minilm:l6-v2", base_url="http://localhost:11434")
model = OllamaLLM(model="Gemma3:4b")


def upload_audio(file):
    os.makedirs(audios_directory, exist_ok=True)
    try:  # if uploaded via streamlit UI
        with open(audios_directory + file.name, "wb") as f:
            f.write(file.getbuffer())
            print("successfully uploaded audio via streamlit UI")
            return audios_directory + file.name
    except:
        shutil.copy(file, os.path.join(audios_directory, os.path.basename(file)))
        print("successfully uploaded audio via file explorer")
        return os.path.join(audios_directory, os.path.basename(file))


def transcribe_audio(file_path, load_transcript=False):
    if os.path.exists("transcript.txt") and load_transcript:
        with open("transcript.txt", "r") as f:
            return f.read()
    elif os.path.exists("llm/rag/transcript.txt") and load_transcript:
        with open("llm/rag/transcript.txt", "r") as f:
            return f.read()
    else:
        whisper_model = whisper.load_model("medium.en")
        trans = whisper_model.transcribe(file_path)
        print("successfully transcribed audio")
        with open("transcript.txt", "w") as f:
            f.write(trans["text"])
        return trans["text"]

def split_text(text):
    txt_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200, add_start_index=True
    )
    print("successfully split text")
    return txt_splitter.split_text(text)


def store_vector(texts, load_index=False):
    if os.path.exists("faiss_index") and load_index:
        vs = FAISS.load_local(
            "faiss_index", embeding, allow_dangerous_deserialization=True
        )
        print("successfully loaded vector")
    elif  os.path.exists("llm/rag/faiss_index") and load_index:
        vs = FAISS.load_local(
            "llm/rag/faiss_index", embeding, allow_dangerous_deserialization=True
        )
        print("successfully loaded vector")
    else:
        vs = FAISS.from_texts(texts, embedding=embeding)
        print("successfully stored vector")
        vs.save_local("faiss_index")
    return vs.as_retriever(search_type="similarity", search_kwargs={"k": 4})


def clean_text(text):
    cleaned_text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    return cleaned_text.strip()


def llm_answer(related_docs, question):
    print(related_docs)

    context = "\n\n".join(doc.page_content  for doc in related_docs)
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model
    answer = chain.invoke({"question": question, "context": context})
    answer = clean_text(answer)
    # print(answer)
    print("successfully answered question")
    return answer


uploaded_file = st.file_uploader(
    "Upload Audio", type=["mp3", "wav"], accept_multiple_files=False
)

if uploaded_file:
    upload_audio(uploaded_file)
    text = transcribe_audio(audios_directory + uploaded_file.name, load_transcript=True)
    chunked_texts = split_text(text)
    retriever = store_vector(chunked_texts, load_index=True)

    question = st.chat_input()

    if question:
        st.chat_message("user").write(question)
        related_docs = retriever.invoke(question)
        # related_docs = llm_answer(question)
        answer = llm_answer(related_docs, question)
        st.chat_message("assistant").write(answer)
