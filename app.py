import os
import warnings
import torch
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationalRetrievalChain
import streamlit as st
import time
from langchain_ollama import OllamaLLM 

st.set_page_config(page_title="Book Recommendation Chatbot", page_icon="📚")

st.markdown("""<style>         
    img {
        width: 300px; 
        height: 300px; 
        border-radius: 50%; 
        object-fit: cover; 
        border: 5px solid #3B3B98; 
        margin: 20px 0; 
        margin-left: 70px;
    }
    .book-description {
        font-size: 24px; 
        font-weight: bold; 
        color: #3B3B98; 
        margin: 20px 0; 
        font-family: 'Arial', sans-serif; 
        margin-left: 150px;
    }     
</style>""", unsafe_allow_html=True)

st.markdown('<div class="book-description">Book Recommendation Chatbot</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 4, 1])
with col2:
    st.image("data/booklogoimg.jpg")

# checking if the session is empty or not 
if "messages" not in st.session_state:
    st.session_state.messages = []

if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferWindowMemory(k=3, memory_key="chat_history", return_messages=True)

def reset_conversation():
    st.session_state.messages = []
    st.session_state.memory.clear()

prompt_template = """
Chat History: {chat_history}
Question: {question}
Context: {context}  
"""

embeddings = HuggingFaceEmbeddings(
    model_name="nomic-ai/nomic-embed-text-v1",
    model_kwargs={"trust_remote_code": True}
)

db = FAISS.load_local("book_vector_db", embeddings, allow_dangerous_deserialization=True)
db_retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 4})

prompt = PromptTemplate(template=prompt_template, input_variables=['context', 'question', 'chat_history'])

llm = OllamaLLM(model="llama3.2")

qa = ConversationalRetrievalChain.from_llm(
    llm=llm,
    memory=st.session_state.memory,
    retriever=db_retriever,
    combine_docs_chain_kwargs={'prompt': prompt}
)

for message in st.session_state.messages:
    with st.chat_message(message.get("role")):
        st.write(message.get("content"))

# chat box 
input_prompt = st.chat_input("Say something")

if input_prompt:
    with st.chat_message("user"):
        st.write(input_prompt)  

    st.session_state.messages.append({"role": "user", "content": input_prompt})

    ipc_keywords = ['books', 'reads', 'fictional', 'non-fictional', 'author', 'genre' , 'ratings']
    if any(keyword in input_prompt.lower() for keyword in ipc_keywords):
        with st.chat_message("assistant"):
            message_placeholder = st.empty()  

            with st.spinner("Thinking..."):
                result = qa.invoke(input=input_prompt)  
            full_response = "\n\n\n"
            for chunk in result["answer"]:
                full_response += chunk
                time.sleep(0.02)
                message_placeholder.markdown(full_response + " ▌")

        st.session_state.messages.append({"role": "assistant", "content": result["answer"]})
    else:
        fallback_message = "Sorry, I don't have any recommendations for that. Try asking for books in a specific genre like 'thriller', 'romance', 'science fiction', etc."
        with st.chat_message("assistant"):
            st.write(fallback_message)
        
        st.session_state.messages.append({"role": "assistant", "content": fallback_message})

    st.button('Reset All Chat ', on_click=reset_conversation)
