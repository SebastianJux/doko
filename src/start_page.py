# Display the DataFrame
import streamlit as st
import pandas as pd


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

st.title("Ewige Liste")

st.write("Ewige Liste Aggregiert:")
spielernamen = [col for col in st.session_state.ewige_liste.columns if col not in ["Datum"]]
st.dataframe(st.session_state.ewige_liste[spielernamen].sum().to_frame().T, hide_index=True)

st.write("Tages-Übersicht:")
st.dataframe(st.session_state.ewige_liste) 
