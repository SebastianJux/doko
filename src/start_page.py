# Display the DataFrame
import streamlit as st
import pandas as pd

st.title("Ewige Liste")

st.write("Ewige Liste Aggregiert:")
spielernamen = [col for col in st.session_state.ewige_liste.columns if col not in ["Datum"]]
st.dataframe(st.session_state.ewige_liste[spielernamen].sum().to_frame().T, hide_index=True)

st.write("Jahres-Übersicht:")
spielernamen = [col for col in st.session_state.ewige_liste.columns if col not in ["Datum"]]
year_overview = st.session_state.ewige_liste.copy()
year_overview["Datum"] = pd.to_datetime(year_overview["Datum"]).dt.year
year_overview = year_overview.groupby("Datum").sum().reset_index()
year_overview["Datum"] = year_overview["Datum"].astype("str")
st.dataframe(year_overview, hide_index=True)

st.write("Tages-Übersicht:")
st.dataframe(st.session_state.ewige_liste) 
