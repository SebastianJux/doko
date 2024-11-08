import streamlit as st
from streamlit_extras.stylable_container import stylable_container
import pandas as pd
import json
from src.helper import (
    read_parquet_from_blob, 
    write_parquet_to_blob, 
    finalise_tagesliste, 
    # player_structure, 
    determine_active_players,
    game_quality_check,
    display_extrapunkte,
    compute_points,
    continue_tagesliste
)
import random

GAMETYPES = ["Normalspiel", "Pflichtsolo", "Lustsolo", "Hochzeit", "Armut", "Schmeißen"]
DF_COLS = [
    "Spiel Index", 
    "Spielpunkte",
    "Spiel", 
    "Spiel Type", 
    "Dealer", 
    "Pflichtsolo Spieler",
    "Hochzeit Spieler", 
    "Hochzeit Partner", 
    "Armut Spieler",
    "Armut Partner",
    "Welches Solo", 
    "Extra Punkte", 
    "Ansagen",
    "Meta"
]
SOlI = ["Trumpfsolo", "Bubensolo", "Damensolo", "Stille Hochzeit", "Fleischlos"]

if "tagesliste" not in st.session_state:
    st.title("Configuriere Tagesliste")
    
    if st.button("Weiter von letzter Tagesliste"):
        try:
            continue_tagesliste(DF_COLS)
            
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
        df_cols = DF_COLS[0:1] + names + DF_COLS[1:]
        st.session_state["names"] = names
        st.session_state["dealer"] = random.randrange(len(st.session_state.names))
        st.session_state["tagesliste"] = pd.DataFrame({
            "Meta": [{
                "n_normale_spiele": n_normale_spiele, 
                "n_pflichtspiele": n_pflichtspiele
            }],
            "Dealer": st.session_state.names[st.session_state.dealer],
            "Spiel Index": 0,
            }, columns=df_cols
        )
        st.session_state["meta"] = st.session_state["tagesliste"]["Meta"].iloc[0]
        write_parquet_to_blob(st.session_state.tagesliste, "tagesliste-tmp", "tmp.parquet")
        st.rerun()

else:
    st.title("Tagesliste")
    
    if "active_players" not in st.session_state:
        st.session_state["active_players"] = determine_active_players(st.session_state.names, st.session_state.dealer)
    
    with st.container(border=True):        
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
        with st.container(border=True):
            st.write("Pflichtsoli offen:")
            cols = st.columns(st.session_state.n_players)
            for i, n in enumerate(st.session_state.names):
                with cols[i]:
                    st.write(f"{n}: {st.session_state['pflicht_open'][n]}")
    
    if "spielindex" not in st.session_state:
        st.session_state["spielindex"] = 1
            
    # Input fields to add new data (points, winners, Spiel Type)
    with st.container(border=True):
        st.write("Neues Spiel:")
        status_cols = st.columns(3)
        with status_cols[0]:
            game_type = st.selectbox("Spiel Type", options=GAMETYPES, key="selectbox_game_type")
        with status_cols[1]:
            game_points = st.number_input("Erzielte Punkte", min_value=0, step=1, key="selectbox_game_points")
        with status_cols[2]:
            winners: list[str] = st.multiselect("Sieger", options=st.session_state.active_players, key="selectbox_winners")
        
        who_hochzeit = None
        who_armut = None
        which_solo = None
        if game_type == "Hochzeit":
            who_hochzeit = st.selectbox("Wer hatte Hochzeit?", options=st.session_state.active_players, key="selectbox_who_hochzeit")
        elif game_type == "Armut":
            who_armut = st.selectbox("Wer hatte Armut?", options=st.session_state.active_players, key="selectbox_who_armut")
        elif game_type in ["Pflichtsolo", "Lustsolo"]:
            which_solo = st.selectbox("Welches Solo?", options=SOlI, key="selectbox_which_solo")
        
        extra_points, ansagen_dict = display_extrapunkte(st.session_state.active_players, game_type)
        points = compute_points(winners, game_points, ansagen_dict, extra_points)
        st.write(f"Punkte: {points}")

        # Button to add new row with the entered data
        if st.button("Bestätige"):
            
            re_players = winners if extra_points["gegen_alte"] == "Nein" else [p for p in st.session_state.active_players if p not in winners]

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
            
            armut_partner = None
            hochzeit_partner = None
            if game_type == "Hochzeit":
                if who_hochzeit in winners:
                    hochzeit_partner = [p for p in winners if p != who_hochzeit][0]
                else:
                    hochzeit_partner = [p for p in st.session_state.active_players if p not in [who_hochzeit] + winners][0]
            elif game_type == "Armut":
                if who_armut in winners:
                    armut_partner = [p for p in winners if p != who_armut][0]
                else:
                    armut_partner = [p for p in st.session_state.active_players if p not in [who_armut] + winners][0]
        
            # Add new row to the DataFrame
            new_row = pd.DataFrame(
                {
                    "Spiel Index": st.session_state.spielindex,
                    **{name: winner_points for name in winners},
                    **{name: loser_points*-1 for name in st.session_state.active_players if name not in winners},
                    "Spielpunkte": game_points,
                    "Spiel": points,
                    "Spiel Type": game_type,
                    "Dealer": st.session_state.names[st.session_state.dealer],
                    "Pflichtsolo Spieler": player,
                    "Hochzeit Spieler": who_hochzeit,
                    "Hochzeit Partner": hochzeit_partner,
                    "Armut Spieler": who_armut,
                    "Armut Partner": armut_partner,
                    "Welches Solo": which_solo,
                    "Extra Punkte": [extra_points], 
                    "Ansagen": [ansagen_dict],
                    "Meta": [st.session_state.meta]
                }, index=[0]
            )
            
            st.session_state.spielindex += 1
            st.session_state.tagesliste = pd.concat([st.session_state.tagesliste, new_row], ignore_index=True)
            write_parquet_to_blob(st.session_state.tagesliste, "tagesliste-tmp", "tmp.parquet")
        
            if game_type not in ["Pflichtsolo", "Schmeißen"]:
                st.session_state.dealer = (st.session_state.dealer + 1) % st.session_state.n_players
                st.session_state["active_players"] = determine_active_players(st.session_state.names, st.session_state.dealer)
                
            st.rerun()
        
    # Display the DataFrame
    st.write("Tagesliste:")
    st.dataframe(st.session_state.tagesliste.iloc[-1:0:-1, :].drop(columns=["Meta"]), hide_index=True)
    
    st.write("Tagesliste Aggregiert:")
    st.dataframe(st.session_state.tagesliste[st.session_state.names].iloc[1:, :].sum().to_frame().T, hide_index=True)

    # Button to clear the DataFrame from session state
    if st.button("Beende Tagesliste"):
        finalise_tagesliste()
