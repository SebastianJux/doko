from streamlit_extras.stylable_container import stylable_container
import streamlit as st

# Add CSS to set a background image
st.markdown(
    """
    <style>
    .stApp {
        background-image: url("https://spiele-palast.de/app/uploads/sites/6/2021/09/DE_doko_in-game_v3-1110x694.jpg");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    </style>
    """,
    unsafe_allow_html=True
)

with stylable_container(
    key="green_button",
    css_styles="""
        button {
            background-color: green;
            color: white;
            border-radius: 20px;
        }
        """,
):
    st.button("Green button")
    st.button("2. green button")

st.button("Normal button")

with stylable_container(
    key="container_with_border",
    css_styles="""
        {
            border: 1px solid rgba(49, 51, 63, 0.2);
            border-radius: 0.5rem;
            padding: calc(1em - 1px);
            background-color: #22369e;
        }
        """,
):
    st.markdown("This is a container with a border.")
    st.button("Normal button")