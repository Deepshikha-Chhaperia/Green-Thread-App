import streamlit as st
import hashlib
import sqlite3
from fabric_analyzer import display_fabric_analysis
from design_studio import display_design_studio, load_models
from main import sidebar_menu, display_home, display_design_studio_wrapper, display_fabric_analysis
from sustainability_dashboard import display_sustainability_dashboard
from PIL import Image
from urllib.parse import urlparse, parse_qs
from queue import Queue
from contextlib import contextmanager
# Initialize AI models
image_generator = load_models()
# Database connection pool
DB_NAME = 'ecochic.db'
connection_pool = Queue(maxsize=5)
@contextmanager
def get_db_connection():
    try:
        connection = connection_pool.get(block=False)
    except:
        connection = sqlite3.connect(DB_NAME)
    try:
        yield connection
    finally:
        connection_pool.put(connection)
# Initialize database
def init_db():
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS designs
                     (id INTEGER PRIMARY KEY, user_id INTEGER, 
                      style TEXT, materials TEXT, clothing_type TEXT, 
                      production_method TEXT, custom_design TEXT)''')
        conn.commit()
# User authentication functions
def create_user(username, password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    with get_db_connection() as conn:
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
def authenticate_user(username, password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hashed_password))
        user = c.fetchone()
    return user
def sidebar_menu():
    with st.sidebar:
        st.title("Menu")
        if 'user' in st.session_state and st.session_state['user']:
            st.write(f"Welcome, {st.session_state['user'][1]}!")
            if st.button("Logout"):
                st.session_state['user'] = None
                st.rerun()
        else:
            choice = st.radio("Navigation", ["Home", "Login", "Register"])
            if choice == "Login":
                st.subheader("Login Section")
                username = st.text_input("User Name")
                password = st.text_input("Password", type='password')
                if st.button("Login"):
                    user = authenticate_user(username, password)
                    if user:
                        st.session_state['user'] = user
                        st.success("Logged In Successfully")
                        st.rerun()
                    else:
                        st.error("Incorrect Username/Password")
            elif choice == "Register":
                st.subheader("Create New Account")
                new_user = st.text_input("Username")
                new_password = st.text_input("Password", type='password')
                if st.button("Sign Up"):
                    if create_user(new_user, new_password):
                        st.success("You have successfully created an account")
                        st.info("Please Login to proceed")
                    else:
                        st.error("Username already exists")
        st.subheader("Features")
        if st.button("AI Design Studio"):
            st.query_params["page"] = "design_studio"
            st.rerun()
        if st.button("Fabric Analysis"):
            st.query_params["page"] = "fabric_analysis"
            st.rerun()
        if st.button("Sustainability Dashboard"):
            st.query_params["page"] = "sustainability_dashboard"
            st.rerun()
def display_design_studio_wrapper():
    display_design_studio(get_db_connection, image_generator)
# User authentication and navigation functions are unchanged
#def get_query_params():
#    """Parse query parameters from the URL."""
#    query_params = st.experimental_get_query_params()
#    return query_params.get("page", ["home"])[0]
def get_query_params():
    """
    Get query parameters in a way that's compatible with both older and newer Streamlit versions.
    """
    # Try the new method first
    if hasattr(st, 'query_params'):
        return st.query_params.get("page", "home")
    
    # Fall back to the old method if the new one isn't available
    params = st.experimental_get_query_params()
    return params.get("page", ["home"])[0]
def main():
    init_db()
    sidebar_menu()
    # Get the 'page' parameter from the URL
    page = get_query_params()
    if page == "home":
        display_home()
    elif page == "design_studio":
        display_design_studio_wrapper()
    elif page == "fabric_analysis":
        display_fabric_analysis()
    elif page == "sustainability_dashboard":
        display_sustainability_dashboard(get_db_connection)
if __name__ == '__main__':
    main()
