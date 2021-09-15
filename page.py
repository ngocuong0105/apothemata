import streamlit as st
class Page(object):
    def __init__(self, title:str) -> None:
        self.title = title

    def load_page(self) -> None:
        raise NotImplementedError

    def show_title(self) -> None:
        # Add a title
        st.title(self.title)
        
    def read_css(file_path: str) -> None:
        with open(file_path) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
