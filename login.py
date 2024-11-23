import streamlit as st
import json
import os

USER_DATA_PATH = 'users.json'

# Load users from the JSON file
def load_users():
    if not os.path.exists(USER_DATA_PATH):
        return {}
    with open(USER_DATA_PATH, 'r') as file:
        return json.load(file)

# Verify user login credentials
def login(username, password):
    users = load_users()
    if username not in users:
        return "Username not found."
    if users[username] != password:
        return "Incorrect password."
    return "Login successful."

# Login page UI in Streamlit
def login_page():
    st.title("Login to Chat")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        message = login(username, password)
        if message == "Login successful.":
            st.session_state["username"] = username
            st.success(message)
        else:
            st.error(message)
