import streamlit as st
import pandas as pd
import json
from src.helper import (
    read_csv_from_blob, 
    write_csv_to_blob, 
    finalise_tagesliste, 
    # player_structure, 
    determine_active_players,
    game_quality_check
)
import random

GAMETYPES: list = ["Normalspiel", "Pflichtsolo", "Lustsolo", "Hochzeit", "Armut", "Schmeißen"]

if "tagesliste" not in st.session_state:
    st.title("Configuriere Tagesliste")
    
    if st.button("Weiter von letzter Tagesliste"):
        try:
            tmp_df = read_csv_from_blob("tagesliste-tmp", "tmp.csv")
            tmp_df['Meta'] = tmp_df['Meta'].apply(lambda x: x.replace("'", '"'))
            tmp_df['Meta'] = tmp_df['Meta'].apply(json.loads)
    
            st.session_state["names"] = [
                col for col in tmp_df.columns if col not in ["Spiel Index", "Spiel", "Spiel Type", "Dealer", "Pflichtsolo Spieler", "Meta"]
            ]
            st.session_state["tagesliste"] = tmp_df
            st.session_state["n_players"] = len(st.session_state["names"])
            st.session_state["meta"] = tmp_df["Meta"].iloc[-1]
            
            game_type = tmp_df["Spiel Type"].iloc[-1]
            st.session_state["dealer"] = st.session_state.names.index(tmp_df["Dealer"].iloc[-1])
            if game_type not in ["Pflichtsolo", "Schmeißen"]:
                st.session_state.dealer = (st.session_state.dealer + 1) % st.session_state.n_players
            st.session_state["active_players"] = determine_active_players(st.session_state.names, st.session_state.dealer)
   
            st.rerun()
            
        except Exception:
            st.error("Tagesliste kann nicht weitergeführt werden.")
    
    # Input fields for the numbers
    n_normale_spiele = st.number_input("Anzahl normale Spiele", min_value=0, step=1, key="normale_spiele")
    n_pflichtspiele = st.number_input("Anzahl Pflichtspiele", min_value=0, step=1, key="pflichtspiele")
    
    # Define initial name options
    spielernamen = [col for col in st.session_state.ewige_liste.columns if col not in ["Datum"]]

    # Create dropdowns with option to enter a new name
    names = []
    if "n_players" not in st.session_state:
        st.session_state["n_players"] = 4
    # Option to add additional players
    st.write(f"Spieler*innen: {st.session_state.n_players}")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Zusätzliche Spieler*in"):
            st.session_state.n_players += 1
            st.rerun()
    with col2:
        if st.button("Spieler*in entfernen"):
            if st.session_state.n_players <= 4:
                st.error("Mit weniger als 4 Spieler*innen ist doof")
                st.rerun()
            else:
                st.session_state.n_players -= 1
                st.rerun()
    
    # names = player_structure(st.session_state["n_players"], spielernamen)
    st.write("Spieler müssen in der richtigen Reihenfolge eingetragen werden!")
    for i in range(1, st.session_state.n_players+1):
        options = [col for col in spielernamen if col not in names]
        selected_name = st.selectbox(
            "Wähle Spieler aus",
            options=options,
            key=f"name_{i}"
        )
        names.append(selected_name)

    # Button to generate DataFrame
    if st.button("Erstelle Tagesliste"):
        # Create DataFrame with selected names as columns
        df_cols = ["Spiel Index"] + names + ["Spiel", "Spiel Type", "Dealer", "Pflichtsolo Spieler", "Meta"]
        st.session_state["tagesliste"] = pd.DataFrame(columns=df_cols)
        st.session_state["names"] = names
        st.session_state["meta"] = {"n_normale_spiele": n_normale_spiele, "n_pflichtspiele": n_pflichtspiele}
        
        st.rerun()

else:
    st.title("Tagesliste")
    
    
    if "dealer" not in st.session_state:
        st.session_state["dealer"] = random.randrange(len(st.session_state.names))
        st.session_state["active_players"] = determine_active_players(st.session_state.names, st.session_state.dealer)
    
    st.write("Status")
    status_cols = st.columns(3)
    with status_cols[0]:
        st.write(f"{st.session_state.names[st.session_state.dealer]} muss geben")
    with status_cols[1]:
        
        st.write(f"""Normalspiele: 
                 {st.session_state.tagesliste.loc[~st.session_state.tagesliste['Spiel Type'].isin(['Pflichtsolo', 'Schmeißen']), :].shape[0]}
                 /{st.session_state.meta['n_normale_spiele']*st.session_state.n_players}""")
    with status_cols[2]:
                st.write(f"""Pflichtsoli: 
                 {st.session_state.tagesliste.loc[st.session_state.tagesliste['Spiel Type'].isin(['Pflichtsolo']), :].shape[0]}
                 /{st.session_state.meta['n_pflichtspiele']*st.session_state.n_players}""")
    if st.session_state.meta["n_pflichtspiele"] > 0:
        if "pflicht_open" not in st.session_state:
            st.session_state["pflicht_open"] = {
                n: (
                    st.session_state.meta["n_pflichtspiele"]
                    - st.session_state.tagesliste.loc[(st.session_state.tagesliste["Pflichtsolo Spieler"] == n) & (st.session_state.tagesliste["Spiel Type"] == "Pflichtsolo"), :].shape[0]
                ) for n in st.session_state.names
            }
        st.write("Pflichtsoli offen:")
        cols = st.columns(st.session_state.n_players)
        for i, n in enumerate(st.session_state.names):
            with cols[i]:
                st.write(f"{n}: {st.session_state['pflicht_open'][n]}")
    
    if "spielindex" not in st.session_state:
        st.session_state["spielindex"] = 1
            
    st.write("Neues Spiel:")
    
    # Input fields to add new data (points, winners, Spiel Type)
    points = st.number_input("Punkte", min_value=0, step=1, key="points")
    winners: list[str] = st.multiselect("Sieger", options=st.session_state.active_players, key="winners")
    game_type = st.selectbox("Spiel Type", options=GAMETYPES, key="game_type")

    # Button to add new row with the entered data
    if st.button("Bestätige"):
        winner_points = points
        loser_points = points
        player = None
        if game_type in ["Pflichtsolo", "Lustsolo"]:
            if len(winners) == 1:
                player = winners[0]
                winner_points *= 3
            elif len(winners) == 3:
                player = [name for name in st.session_state.active_players if name not in winners][0]
                loser_points *= 3
            else:
                st.error("Falsche Anzahl an Spielern für ein Solo.")
                st.stop()
            
        game_quality_check(game_type, player, winners, points)
        
        # Add new row to the DataFrame
        new_row = pd.DataFrame(
            {
                "Spiel Index": st.session_state.spielindex,
                **{name: winner_points for name in winners},
                **{name: loser_points*-1 for name in st.session_state.active_players if name not in winners},
                "Spiel": points,
                "Spiel Type": game_type,
                "Dealer": st.session_state.names[st.session_state.dealer],
                "Pflichtsolo Spieler": player,
                "Meta": [st.session_state.meta]
            }, index=[0]
        )
        
        st.session_state.spielindex += 1
        st.session_state.tagesliste = pd.concat([st.session_state.tagesliste, new_row], ignore_index=True)
        write_csv_to_blob(st.session_state.tagesliste, "tagesliste-tmp", "tmp.csv")
        
        if game_type not in ["Pflichtsolo", "Schmeißen"]:
            st.session_state.dealer = (st.session_state.dealer + 1) % st.session_state.n_players
            st.session_state["active_players"] = determine_active_players(st.session_state.names, st.session_state.dealer)
        st.rerun()
        
    # Display the DataFrame
    st.write("Tagesliste:")
    st.dataframe(st.session_state.tagesliste.drop(columns=["Meta"]), hide_index=True)
    
    st.write("Tagesliste Aggregiert:")
    st.dataframe(st.session_state.tagesliste[st.session_state.names].sum().to_frame().T, hide_index=True)

    # Button to clear the DataFrame from session state
    if st.button("Beende Tagesliste"):
        finalise_tagesliste()
