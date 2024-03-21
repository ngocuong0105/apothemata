import streamlit as st
class Page(object):
    '''
    Page object which is part of the MultiPage framework of the app
    Every Page need a constructor method __init__ and a load_page function
    '''
    def __init__(self, title:str) -> None:
        self.title = title

    def load_page(self) -> None:
        '''
        Note objects which inherit from Page should implement a load_page method!
        '''
        raise NotImplementedError

    def show_title(self) -> None:
        '''
        Display title of page on the top
        '''
        st.title(self.title)
        
    def read_css(self, file_path: str) -> None:
        '''
        Method for wrapping streamlit text with 
        css style file located in file_path
        '''
        with open(file_path) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)