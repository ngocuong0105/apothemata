import streamlit as st
import base64

from framework.page import Page
import os

class home(Page):
    '''
    Home page with app title and custom background.
    '''
    def __init__(self, title: str) -> None:
        super().__init__(title)

    def load_page(self):
        '''
        Load page is mandatory method for every Page object.
        Here we set title and background.
        '''
        title = 'Stock Data Crawler'
        subtitle = 'Scraping the web has never been easier'
        self.set_title(title, subtitle)
        self.set_background('./context/blocks.gif')

    @st.cache(allow_output_mutation = True)
    def _get_base64_of_bin_file(self, path_to_bin_file: str) -> base64:
        '''
        Image data type converter to binary.
        '''
        with open(path_to_bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()

    def set_background(self, path_to_png: str) -> None:
        '''
        Display background of home page.
        '''
        bin_str = self._get_base64_of_bin_file(path_to_png)
        page_bg_img = '''
        <style>
        .stApp  {
        background-image: url("data:image/png;base64,%s");
        background-size:cover;
        background-repeat: no-repeat;
        }
        </style>
        ''' % bin_str
        
        st.markdown(page_bg_img, unsafe_allow_html=True)

    def set_title(self, title:str, subtitle:str) -> None:
        '''
        Display title and subtitle on home page.
        '''
        curr_dir = os.getcwd()
        path = os.path.join(curr_dir,'styles/home_title.css')
        with open(path) as f:
            title_html = f'<style>{f.read()}</style> <h1 class="title">{title}</h1> <h2 class="subtitle">{subtitle}</h2>'
        st.markdown(title_html,unsafe_allow_html=True)


