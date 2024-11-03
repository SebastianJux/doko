# Display the DataFrame
import streamlit as st
import pandas as pd

st.title("Ewige Liste")

st.write("Ewige Liste Aggregiert:")
spielernamen = [col for col in st.session_state.ewige_liste.columns if col not in ["Datum"]]
st.dataframe(st.session_state.ewige_liste[spielernamen].sum().to_frame().T, hide_index=True)

st.write("Tages-Übersicht:")
st.dataframe(st.session_state.ewige_liste) 
