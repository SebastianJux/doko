import streamlit as st
import pandas as pd
from src.helper import read_csv_from_blob, write_csv_to_blob, add_player, remove_player
   
st.title("Spieler*innen Konfiguration")
    
if "ewige_liste" not in st.session_state:
    st.session_state["ewige_liste"] = read_csv_from_blob("ewige-liste", "ewige_liste.csv")

st.write("Eingetragene Spieler*innen")
spielernamen = [col for col in st.session_state.ewige_liste.columns if col not in ["Datum", "Spiel Index", "Spiel", "Spiel Type"]]
st.dataframe(pd.DataFrame({"Namen": spielernamen})) 

new_name = st.text_input("Trage Spielernamen ein:", key="new_name")
    
# Button to generate DataFrame
if st.button("Spieler*innen hinzufügen"):
    add_player(new_name)
    
remove_name = st.text_input("Trage Spielernamen ein:", key="remove_name")
# Button to generate DataFrame
if st.button("Spieler*innen entfernen"):
    remove_player(remove_name)
