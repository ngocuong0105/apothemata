import streamlit as st
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

def _click_button(txt:str, on_click = None, args = None, override_pressed:bool = False):
    if not override_pressed:
        back_color = st.get_option('theme.primaryColor')
        st.markdown(f"<style>div.stButton > button:first-child {{background-color:{back_color};color:white;font-size:16px;text-align:center;}} </style>", unsafe_allow_html=True)
        pressed = st.button(f'{txt}', on_click = on_click, args = args)
        if pressed:
            back_color = st.get_option('theme.backgroundColor')
            st.markdown(f"<style>div.stButton > button:first-child {{background-color:{back_color};color:white;font-size:16px;text-align:center;}} </style>", unsafe_allow_html=True)
        return pressed
    return _click_button(txt)