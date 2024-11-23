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

# Save users to the JSON file
def save_users(users):
    with open(USER_DATA_PATH, 'w') as file:
        json.dump(users, file)

# Register a new user
def register(username, password):
    users = load_users()
    if username in users:
        return "Username already exists."
    users[username] = password
    save_users(users)
    return "Registration successful."

# Registration page UI in Streamlit
def register_page():
    st.title("Register New User")
    username = st.text_input("Choose a username")
    password = st.text_input("Choose a password", type="password")
    
    if st.button("Register"):
        message = register(username, password)
        if message == "Registration successful.":
            st.success(message)
        else:
            st.error(message)
