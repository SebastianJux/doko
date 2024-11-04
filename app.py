import streamlit as st
from src.helper import read_csv_from_blob

# Read the CSV file
st.session_state["ewige_liste"] = read_csv_from_blob("ewige-liste", "ewige_liste.csv")

start_page = st.Page("src/start_page.py", title="Sartseite", icon="🔮", default=True)
new_day = st.Page("src/neuer_spieltag.py", title="Neuer Spieltag", icon="🆕")
players = st.Page("src/players.py", title="Spieler*innen", icon="👋")
regeln = st.Page("src/regeln.py", title="Regeln", icon="ℹ️")

pg = st.navigation([start_page, new_day, players, regeln])

pg.run()