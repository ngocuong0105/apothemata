import streamlit as st
from utils import click_button
def st_session(key:str, curr:str, next:str):
    def decorator(func):
        if key not in st.session_state:
            st.session_state[key] = (curr,None)
        if st.session_state[key][0] == curr:
            def wrapper(*args,**kwargs):
                data = func(*args,**kwargs)
                st.session_state[key] == (next,data)
            return wrapper
    return decorator

