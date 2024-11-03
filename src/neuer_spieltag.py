import streamlit as st
import pandas as pd
from src.helper import write_csv_to_blob

GAMETYPES: list = ["Normalspiel", "Pflichtsolo", "Lustsolo", "Hochzeit", "Armut", "Schmeißen"]

if not "tagesliste" in st.session_state:
    st.title("Configuriere Tagesliste")
    # Define initial name options
    spielernamen = [col for col in st.session_state.ewige_liste.columns if col not in ["Datum", "Spiel Index", "Spiel", "Spiel Type"]]

    # Create dropdowns with option to enter a new name
    names = []
    for i in range(1, 5):
        selected_name = st.selectbox(
            "Wähle Spieler aus",
            options=spielernamen + ["Neuer Spieler..."],
            key=f"name_{i}"
        )
        if selected_name == "Neuer Spieler...":
            new_name = st.text_input(f"Spielername {i}", key=f"new_name_{i}")
            names.append(new_name)
        else:
            names.append(selected_name)

    # Input fields for the numbers
    n_normale_spiele = st.number_input("Anzahl normale Spiele", min_value=0, step=1, key="normale_spiele")
    n_pflichtspiele = st.number_input("Anzahl Pflichtspiele", min_value=0, step=1, key="pflichtspiele")

    # Button to generate DataFrame
    if st.button("Erstelle Tagesliste"):
        # Create DataFrame with selected names as columns
        df_cols = ["Spiel Index"] + names + ["Spiel", "Spiel Type"]
        st.session_state["tagesliste"] = pd.DataFrame(columns=df_cols)
        st.session_state["names"] = names
        st.rerun()

else:
    st.title("Tagesliste")
    
    if "spielindex" not in st.session_state:
        st.session_state["spielindex"] = 1
            
    st.write("Neues Spiel:")
    
    # Input fields to add new data (points, winners, Spiel Type)
    points = st.number_input("Punkte", min_value=0, step=1, key="points")
    winners: list[str] = st.multiselect("Sieger", options=st.session_state.names, key="winners")
    game_type = st.selectbox("Spiel Type", options=GAMETYPES, key="game_type")

    # Button to add new row with the entered data
    if st.button("Bestätige"):
        winner_points = points
        loser_points = points
        if game_type in ["Pflichtsolo", "Lustsolo"]:
            if len(winners) == 1:
                winner_points *= 3
            elif len(winners) == 3:
                loser_points *= 3
            else:
                st.error("Falsche Anzahl an Spielern für ein Solo")
                st.stop()
        
        # Add new row to the DataFrame
        new_row = pd.DataFrame(
            {
                "Spiel Index": st.session_state.spielindex,
                **{name: winner_points for name in winners},
                **{name: loser_points*-1 for name in st.session_state.names if name not in winners},
                "Spiel": points,
                "Spiel Type": game_type
            }, index=[0]
        )
        
        st.session_state.spielindex += 1
        st.session_state.tagesliste = pd.concat([st.session_state.tagesliste, new_row], ignore_index=True)
        
    # Display the DataFrame
    st.write("Tagesliste:")
    st.dataframe(st.session_state.tagesliste, hide_index=True)
    
    st.write("Tagesliste Aggregiert:")
    st.dataframe(st.session_state.tagesliste[st.session_state.names].sum().to_frame().T, hide_index=True)

    # Button to clear the DataFrame from session state
    if st.button("Beende Tagesliste"):
        today = pd.to_datetime('today')
        tagesliste = st.session_state.tagesliste[st.session_state.names].sum().to_frame().T
        tagesliste["Datum"] = today
        
        st.session_state.ewige_liste = pd.concat([st.session_state.ewige_liste, tagesliste], ignore_index=True)
        st.session_state.ewige_liste.fillna(0, inplace=True)
        write_csv_to_blob(st.session_state.tagesliste, "tageslisten" ,f"tagesliste_{today}.csv")
        write_csv_to_blob(st.session_state.ewige_liste, "ewige-liste" ,"ewige_liste.csv")
        del st.session_state.tagesliste, st.session_state.spielindex, st.session_state.names
        st.write("Tagesliste wurde geschlossen")
        st.rerun()
