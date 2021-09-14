import streamlit as st
from PIL import Image

from page import Page


class home(Page):
    def __init__(self, title: str) -> None:
        super().__init__(title)

    @staticmethod
    def load(title):
        # Open and display an image
        # image = Image.open('./context/ml_pic.webp')
        # st.image(image, use_column_width = True)
        # st.write('Hello')
        import base64

        @st.cache(allow_output_mutation=True)
        def get_base64_of_bin_file(bin_file):
            with open(bin_file, 'rb') as f:
                data = f.read()
            return base64.b64encode(data).decode()

        def set_png_as_page_bg(png_file):
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

        set_png_as_page_bg('/home/ncuong/Programming/ts_webapp/context/blocks.gif')

