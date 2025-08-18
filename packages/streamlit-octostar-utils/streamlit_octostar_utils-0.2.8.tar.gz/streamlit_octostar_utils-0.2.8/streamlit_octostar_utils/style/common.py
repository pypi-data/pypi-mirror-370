import streamlit as st


def hide_streamlit_header():
    hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        </style>
    """
    st.markdown(hide_menu_style, unsafe_allow_html=True)
    hide_streamlit_top = """
    <style>
        #root > div:nth-child(1) > div > div > div > div > section > div {padding-top: 0rem;}
    </style>
    """
    st.markdown(hide_streamlit_top, unsafe_allow_html=True)
    hide_decoration_bar_style = """
    <style>
        header {visibility: hidden;}
    </style>
    """
    st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)


def style_streamlit_sidebar():
    code = """
    <style>
        ul[data-testid="stSidebarNavItems"] {
            padding-top: 3rem !important;
        }
    </style>
    """
    st.html(code)


class st_hidden_top_container:
    def __init__(self, spacing_lines=3):
        self.st_container = st.container
        self.spacing_lines = spacing_lines

    def __enter__(self):
        self.st_container().__enter__()
        return self.st_container

    def __exit__(self, exc_type, exc_value, traceback):
        hide_top_style = """
        <style>
            .main > div > div > div > div > div:nth-child(1){
                display: none
            }
        </style>
        """
        st.markdown(hide_top_style, unsafe_allow_html=True)
        self.st_container().__exit__(exc_type, exc_value, traceback)
        for _ in range(self.spacing_lines):
            st.write("")
