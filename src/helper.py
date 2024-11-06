import streamlit as st
from azure.storage.blob import BlobServiceClient
from io import BytesIO
import pandas as pd

def read_csv_from_blob(container_name: str, blob_name: str) -> pd.DataFrame:
    blob_service_client = BlobServiceClient.from_connection_string(st.secrets["blob_connection_string"])
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    blob_data = blob_client.download_blob().readall()
    return pd.read_csv(BytesIO(blob_data))


def write_csv_to_blob(df: pd.DataFrame, container_name: str, blob_name: str):
    blob_service_client = BlobServiceClient.from_connection_string(st.secrets["blob_connection_string"])
    csv_buffer = BytesIO()
    df.to_csv(csv_buffer, index=False)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    blob_client.upload_blob(csv_buffer.getvalue(), overwrite=True)

@st.dialog("Spieler*in entfernen")
def remove_player(name):
    yes_button = st.button("Entfernen")
    no_button = st.button("Abbrechen", type="primary")
    
    if yes_button:
        st.session_state["ewige_liste"].drop(columns=name, inplace=True)
        write_csv_to_blob(st.session_state["ewige_liste"], "ewige-liste", "ewige_liste.csv")
        st.rerun()
        
    if no_button:
        st.rerun()
        
@st.dialog("Spieler*in hinzufügen")
def add_player(name):
    yes_button = st.button("Hinzufügen")
    no_button = st.button("Abbrechen", type="primary")
    
    if yes_button:
        st.session_state["ewige_liste"][name] = 0
        write_csv_to_blob(st.session_state["ewige_liste"], "ewige-liste", "ewige_liste.csv")
        st.rerun()
        
    if no_button:
        st.rerun()
        
@st.dialog("Tagesliste beenden")
def finalise_tagesliste():    
    yes_button = st.button("Beenden")
    no_button = st.button("Abbrechen", type="primary")
    
    if yes_button:
        today = pd.to_datetime('today')
        tagesliste = st.session_state.tagesliste[st.session_state.names].sum().to_frame().T
        tagesliste["Datum"] = today
        
        st.session_state.ewige_liste = pd.concat([st.session_state.ewige_liste, tagesliste], ignore_index=True)
        st.session_state.ewige_liste.fillna(0, inplace=True)
        write_csv_to_blob(st.session_state.tagesliste, "tageslisten" ,f"tagesliste_{today}.csv")
        write_csv_to_blob(st.session_state.ewige_liste, "ewige-liste" ,"ewige_liste.csv")
        del st.session_state.tagesliste, st.session_state.spielindex, st.session_state.names
        st.rerun()
        
    if no_button:
        st.rerun()
        
def player_structure(n_players, spielernamen):
    names = []
    _, _, col13, _, _ = st.columns(5)
    with col13:
        options = [col for col in spielernamen if col not in names]
        selected_name = st.selectbox("Wähle Spieler aus", options=options, key="name_1")
        names.append(selected_name)
    _, col22, _, col24, _ = st.columns(5)
    with col22:
        options = [col for col in spielernamen if col not in names]
        disable5 = True if n_players < 5 else False
        selected_name = st.selectbox(
            "Wähle Spieler aus", options=options, key="name_5}", disabled=disable5
        )
        if not disable5:
            names.append(selected_name)
    with col24:
        options = [col for col in spielernamen if col not in names]
        disable6 = True if n_players < 6 else False
        selected_name = st.selectbox(
            "Wähle Spieler aus", options=options, key="name_6", disabled=disable6
        )
        if not disable6:
            names.append(selected_name)
    col31, _, _, _, col35 = st.columns(5)
    with col31:
        options = [col for col in spielernamen if col not in names]
        selected_name = st.selectbox("Wähle Spieler aus", options=options, key="name_4")
        names.append(selected_name)
    with col35:
        options = [col for col in spielernamen if col not in names]
        selected_name = st.selectbox("Wähle Spieler aus", options=options, key="name_2")
        names.append(selected_name)
    _, col42, _, col44, _ = st.columns(5)
    with col42:
        options = [col for col in spielernamen if col not in names]
        disable8 = True if n_players < 8 else False
        selected_name = st.selectbox(
            "Wähle Spieler aus", options=options, key="name_8", disabled=disable8
        )
        if not disable8:
            names.append(selected_name)
    with col44:
        options = [col for col in spielernamen if col not in names]
        disable7 = True if n_players < 7 else False
        selected_name = st.selectbox(
            "Wähle Spieler aus", options=options, key="name_7", disabled=disable7
        )
        if not disable7:
            names.append(selected_name)
    _, _, col53, _, _ = st.columns(5)
    with col53:
        options = [col for col in spielernamen if col not in names]
        selected_name = st.selectbox("Wähle Spieler aus", options=options, key="name_3")
        names.append(selected_name)
    return names

def determine_active_players(names, dealer):
    n_player = len(names)
    if n_player == 4:
        active_players = names
    elif n_player == 5:
        active_players = [player for i, player in enumerate(names) if i not in [dealer]]
    elif n_player == 6:
        dealer2 = (dealer + 3) % n_player
        active_players = [player for i, player in enumerate(names) if i not in [dealer, dealer2]]
    elif n_player == 7:
        dealer2 = (dealer + 3) % n_player
        dealer3 = (dealer + 6) % n_player
        active_players = [player for i, player in enumerate(names) if i not in [dealer, dealer2, dealer3]]
    return active_players

def game_quality_check(game_type, player, winners, points):
    if game_type == "Pflichtsolo":
        if st.session_state["pflicht_open"][player] == 0:
            st.error(f"{player} hat kein Pflichtsolo mehr offen.")
            st.stop()
        else: 
            st.session_state["pflicht_open"][player] -= 1
    
    if game_type not in ["Pflichtsolo", "Lustsolo"] and len(winners) != 2:
        st.error(f"Ein Spiel des Types {game_type} braucht immer 2 Gewinner.")
        st.stop()
        
    if game_type == "Schmeißen" and points != 0:
        st.error("Ein Schmeißen muss immer 0 Punkte haben")
        st.stop()

def display_extrapunkte(players, game_type):
    extra_points = {}
    if game_type not in ["Pflichtsolo", "Lustsolo"]:
        with st.expander("Extrapunkte:"):
            extra_points["gegen_alte"] = st.selectbox("Gegen die Alten?", options=["Nein", "Ja"], key="gegen_alte")
            extra_points["w_fuchs"] = st.selectbox("Fuchs gefangen bei Gewinner?", options=[0, 1, 2], key="w_fuchs")
            extra_points["l_fuchs"] = st.selectbox("Fuchs gefangen bei Verlierer?", options=[0, 1, 2], key="l_fuchs")
            extra_points["w_doko"] = st.selectbox("Doppelkopf von Gewinner?", options=[0, 1, 2, 3], key="w_doko")
            extra_points["l_doko"] = st.selectbox("Doppelkopf von Verlierer?", options=[0, 1, 2, 3], key="l_doko")
            extra_points["charlie"] = st.selectbox("Letzten Stich mit Kalle?", options=[None]+players, key="charlie")
            extra_points["charlie_g"] = st.selectbox("Wessen Kalle wurde gefangen?", options=[None]+players, key="charlie_g")
    else:
        extra_points["gegen_alte"] = "Nein"
        extra_points["w_fuchs"] = 0
        extra_points["l_fuchs"] = 0
        extra_points["w_doko"] = 0
        extra_points["l_doko"] = 0
        extra_points["charlie"] = None
        extra_points["charlie_g"] = None

    re_cols = st.columns(5)
    ansagen_dict = {}
    with re_cols[0]:
        ansagen_dict["Re"] = st.selectbox("Re:", options=[None]+players, key="Re")
        if ansagen_dict["Re"] is not None:
            with re_cols[1]:
                ansagen_dict["Re_Keine90"] = st.selectbox("Re keine 90:", options=[None]+players, key="Re_Keine90")
                if ansagen_dict["Re_Keine90"] is not None:
                    with re_cols[2]:
                        ansagen_dict["Re_Keine60"] = st.selectbox("Re keine 60:", options=[None]+players, key="Re_Keine60")
                        if ansagen_dict["Re_Keine60"] is not None:
                            with re_cols[3]:
                                ansagen_dict["Re_Keine30"] = st.selectbox("Re keine 30:", options=[None]+players, key="Re_Keine30")
                                if ansagen_dict["Re_Keine30"] is not None:
                                    with re_cols[4]:
                                        ansagen_dict["ReSchwarz"] = st.selectbox("Re Schwarz:", options=[None]+players, key="ReSchwarz")
    contra_cols = st.columns(5)
    with contra_cols[0]:
        ansagen_dict["Contra"] = st.selectbox("Contra:", options=[None]+players, key="Contra")
        if ansagen_dict["Contra"] is not None:
            with contra_cols[1]:
                ansagen_dict["Contra_Keine90"] = st.selectbox("Contra keine 90:", options=[None]+players, key="Contra_Keine90")
                if ansagen_dict["Contra_Keine90"] is not None:
                    with contra_cols[2]:
                        ansagen_dict["Contra_Keine60"] = st.selectbox("Contra keine 60:", options=[None]+players, key="Contra_Keine60")
                        if ansagen_dict["Contra_Keine60"] is not None:
                            with contra_cols[3]:
                                ansagen_dict["Contra_Keine30"] = st.selectbox("Contra keine 30:", options=[None]+players, key="Contra_Keine30")
                                if ansagen_dict["Contra_Keine30"] is not None:
                                    with contra_cols[4]:
                                        ansagen_dict["ContraSchwarz"] = st.selectbox("Contra Schwarz:", options=[None]+players, key="ContraSchwarz")
                
    return extra_points, ansagen_dict

def compute_points(winners, game_points, ansagen_dict, extra_points):
    points = 1
    
    # Punkte für Spielpunkte
    points += max((game_points - 121) // 30, 0)
    if game_points == 240:
        points += 1
    
    # Extrapunkte
    if extra_points["gegen_alte"] == "Ja":
        points += 1
    if extra_points["w_fuchs"] > 0:
        points += extra_points["w_fuchs"]
    if extra_points["l_fuchs"] > 0:
        points -= extra_points["l_fuchs"]
    if extra_points["w_doko"] > 0:
        points += extra_points["w_doko"]
    if extra_points["l_doko"] > 0:
        points -= extra_points["l_doko"]
    if extra_points["charlie"] is not None:
        if extra_points["charlie"] in winners:
            points += 1
        else:
            points -= 1
    if extra_points["charlie_g"] is not None:
        if extra_points["charlie_g"] in winners:
            points -= 1
        else:
            points += 1
        
    # Punkte für Ansagen
    for key, value in ansagen_dict.items():
        if value is not None:
            points += 1
            if key in ["Re", "Contra"]:
                points += 1
                
    if extra_points["gegen_alte"] == "Ja":
        if "Re_Keine90" in ansagen_dict.keys() and game_points > 120:
            points += 1
            if "Re_Keine60" in ansagen_dict.keys() and game_points > 90:
                points += 1
                if "Re_Keine30" in ansagen_dict.keys() and game_points > 60:
                    points += 1
                    if "ReSchwarz" in ansagen_dict.keys() and game_points > 30:
                        points += 1
    else:
        if "Contra_Keine90" in ansagen_dict.keys() and game_points > 120:
            points += 1
            if "Contra_Keine60" in ansagen_dict.keys() and game_points > 90:
                points += 1
                if "Contra_Keine30" in ansagen_dict.keys() and game_points > 60:
                    points += 1
                    if "ContraSchwarz" in ansagen_dict.keys() and game_points > 30:
                        points += 1  
    
    return points
