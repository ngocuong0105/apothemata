import streamlit as st
import base64

from framework.page import Page
import os

class home(Page):
    def __init__(self, title: str) -> None:
        super().__init__(title)

    def load_page(self):
        self.set_title('Stock Data Crawler')
        self.set_background('./context/blocks.gif')


    @st.cache(allow_output_mutation=True)
    def _get_base64_of_bin_file(self, bin_file):
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()

    def set_background(self, png_file):
        bin_str = self._get_base64_of_bin_file(png_file)
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
        return

    def set_title(self, title):
        curr_dir = os.getcwd()
        path = os.path.join(curr_dir,'styles/home_title.css')
        with open(path) as f:
            title_html = f'<style>{f.read()}</style> <h1 class="title">{title}</h1> <h2 class="subtitle">Scraping the web has never been easier</h2>'
        st.markdown(title_html,unsafe_allow_html=True)


