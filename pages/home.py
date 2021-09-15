import streamlit as st
from PIL import Image

import base64
from page import Page


class home(Page):
    def __init__(self, title: str) -> None:
        super().__init__(title)

    @staticmethod
    def load(title):

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
                    font-size: 70px;
                    font-family: sans-serifed;
                    color: white;
                    background: repeating-linear-gradient(45deg, green 0%, blue 15%, purple 25%, white 50%);
                    background-size: 600vw 600vw;
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
                    line-height: 5px;
                    text-align: center;
                    color = white;
                    font-size: 20px;
                    font-family: sans-serifed;
                    color: white;
                    background: repeating-linear-gradient(45deg, green 0%, blue 15%, purple 25%, white 50%);
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

        set_title(title)
        set_background('./context/blocks.gif')

