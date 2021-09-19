import streamlit as st
import time

def markdown_css(txt:str, font_size:int, color:str, height:int = 17, position:str = 'left',col:int = 1) -> None:
    css_txt = f'<p style="font-family:sans-serif;color:{color};font-size: {font_size}px;text-align:{position};line-height: {height}px;"> {txt} </p>'
    if col==1:
        st.markdown(css_txt, unsafe_allow_html=True)
    else:
        col.markdown(css_txt, unsafe_allow_html=True)
        
def click_button(txt:str, on_click = None, args = None, override_pressed:bool = False):
    if not override_pressed:
        back_color = st.get_option('theme.primaryColor')
        st.markdown(f"<style>div.stButton > button:first-child {{background-color:{back_color};color:white;font-size:16px;text-align:center;}} </style>", unsafe_allow_html=True)
        pressed = st.button(f'{txt}', on_click = on_click, args = args)
        if pressed:
            back_color = st.get_option('theme.backgroundColor')
            st.markdown(f"<style>div.stButton > button:first-child {{background-color:{back_color};color:white;font-size:16px;text-align:center;}} </style>", unsafe_allow_html=True)
        return pressed
    return click_button(txt)

def wait_message(txt:str, seconds:int):
    placeholder = st.empty()
    placeholder.text(f'{txt}')
    bar = st.progress(0)
    for i in range(seconds):
        bar.progress((i+1)/seconds)
        time.sleep(1)
    bar.empty()
    placeholder.empty()

    