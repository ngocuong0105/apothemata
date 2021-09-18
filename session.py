import streamlit as st
def st_session(key:str, curr:str, input:tuple):
    def decorator(func):
        def wrapper():
            st.session_state[key] = curr
        return wrapper
    return decorator