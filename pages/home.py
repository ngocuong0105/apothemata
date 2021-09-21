import streamlit as st
import base64
from page import Page


class home(Page):
    def __init__(self, title: str) -> None:
        super().__init__(title)

    def load_page(self):
        self.set_title(self.title)
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

    def set_title(self, title: str):
        title_html = """
            <style>
                .title h1{
                line-height: 700px;
                text-align: center;
                color = transparent;
                user-select: none;
                font-size: 80px;
                font-family: sans-serifed;
                color: white;
                background: repeating-linear-gradient(45deg, #faff8a 0%, #b6f5f0 20%, #d3ddff 40%,#F63366 60%, white 80%);
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
                line-height: 100px;
                text-align: center;
                font-size: 25px;
                font-family: sans-serifed;
                background: repeating-linear-gradient(45deg, #faff8a 0%, #b6f5f0 20%, #d3ddff 40%,#F63366 60%, white 80%);
                background-size: 700vw 700vw;
                -webkit-text-fill-color: transparent;
                -webkit-background-clip: text;
                animation: slide 10s linear infinite forwards;
                }
            </style> 
            <div class="title">
                <h1>APOTHEMATA</h1>
            </div>
            <div class="subtitle">
                <h2>The YOLO trade app</h2>
            </div>
            """
        st.markdown(title_html,unsafe_allow_html=True)
        return



