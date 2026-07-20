import streamlit as st


def apply_custom_css():
    st.markdown(
        """
        <style>
        /* Sidebar navigation text */
        [data-testid="stSidebarNav"] span {
            font-size: 18px !important;
        }

        /* Sidebar navigation item spacing */
        [data-testid="stSidebarNav"] li {
            margin-bottom: 8px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )