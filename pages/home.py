import streamlit as st
from PIL import Image

import base64
from page import Page


class home(Page):
    def __init__(self, title: str) -> None:
        super().__init__(title)

    def load_page(self):

        @st.cache(allow_output_mutation=True)
        def get_base64_of_bin_file(bin_file):
            with open(bin_file, 'rb') as f:
                data = f.read()
            return base64.b64encode(data).decode()

        def set_background(png_file):
            bin_str = get_base64_of_bin_file(png_file)
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

        def set_title(title):
            title_html = """
                <style>
                    .title h1{
                    line-height: 650px;
                    text-align: center;
                    color = transparent;
                    user-select: none;
                    font-size: 80px;
                    font-family: sans-serifed;
                    color: white;
                    background: repeating-linear-gradient(45deg, #faff8a 0%, #b6f5f0 25%, #d3ddff 50%, white 70%);
                    background-size: 700vw 700vw;
                    -webkit-text-fill-color: transparent;
                    -webkit-background-clip: text;
                    animation: slide 10s linear infinite forwards;
                    }
                    @keyframes slide {
                    0%{
                        background-position-x: 0%;
                    }
                    100%{
                        background-position-x: 600vw;
                    }
                }
                    .subtitle h2 {
                    line-height: 15px;
                    text-align: center;
                    font-size: 25px;
                    font-family: sans-serifed;
                    background: repeating-linear-gradient(45deg, #faff8a 0%, #b6f5f0 25%, #d3ddff 50%, white 70%);
                    background-size: 600vw 600vw;
                    -webkit-text-fill-color: transparent;
                    -webkit-background-clip: text;
                    animation: slide 10s linear infinite forwards;
                    }
                </style> 
                <div class="title">
                    <h1>APOTHEMATA</h1>
                </div>
                <div class="subtitle">
                    <h2>All stock data into one place</h2>
                </div>
                """
            st.markdown(title_html,unsafe_allow_html=True)
            return

        set_title(self.title)
        set_background('./context/blocks.gif')

