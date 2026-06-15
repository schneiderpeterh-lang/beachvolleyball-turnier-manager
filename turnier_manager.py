import streamlit as st
from fpdf import FPDF
import random

# --- 1. KERNLOGIK ---
def generiere_kotb_spiele(gruppe):
    return [
        {
            "Team 1 Text": f"{gruppe[0]} & {gruppe[1]}", "Team 1 Spieler": [gruppe[0], gruppe[1]],
            "Team 2 Text": f"{gruppe[2]} & {gruppe[3]}", "Team 2 Spieler": [gruppe[2], gruppe[3]]
        },
        {
            "Team 1 Text": f"{gruppe[0]} & {gruppe[2]}", "Team 1 Spieler": [gruppe[0], gruppe[2]],
            "Team 2 Text": f"{gruppe[1]} & {gruppe[3]}", "Team 2 Spieler": [gruppe[1], gruppe[3]]
        },
        {
            "Team 1 Text": f"{gruppe[0]} & {gruppe[3]}", "Team 1 Spieler": [gruppe[0], gruppe[3]],
            "Team 2 Text": f"{gruppe[1]} & {gruppe[2]}", "Team 2 Spieler": [gruppe[1], gruppe[2]]
        }
    ]

def erstelle_runden_spielplan_r1(spieler_liste):
    felder = [[], [], [], [], []]
    for i in range(20):
        spieler = spieler_liste[i]
        durchgang = i // 5 
        if durchgang % 2 == 0:
            feld_index = i % 5
        else:
            feld_index = 4 - (i % 5)
        felder[feld_index].append(spieler)
        
    runden_plan = {}
    for index, gruppe in enumerate(felder):
        runden_plan[f"Feld {index + 1}"] = generiere_kotb_spiele(gruppe)
    return runden_plan

def erstelle_runde_2_spielplan(spieler_liste):
    top_16 = spieler_liste[:16]   
    bottom_4 = spieler_liste[16:] 
    
    felder = [[], [], [], []]
    for i in range(16):
        spieler = top_16[i]
        durchgang = i // 4 
        if durchgang % 2 == 0: feld_index = i % 4       
        else: feld_index = 3 - (i % 4) 
        felder[feld_index].append(spieler)
        
    felder.append(bottom_4)
    
    runden_plan = {}
    for index, gruppe in enumerate(felder):
        runden_plan[f"Feld {index + 1}"] = generiere_kotb_spiele(gruppe)
    return runden_plan

def erstelle_runde_3_spielplan(r2_tabellen_pro_feld):
    felder = [[], [], [], []]
    for court_idx in range(4):
        feld_key = f"Feld {court_idx + 1}"
        ranking = r2_tabellen_pro_feld[feld_key] 
        felder[0].append(ranking[0]) 
        felder[1].append(ranking[1]) 
        felder[2].append(ranking[2]) 
        felder[3].append(ranking[3]) 
    
    runden_plan = {}
    for index, gruppe in enumerate(felder):
        runden_plan[f"Feld {index + 1}"] = generiere_kotb_spiele(gruppe)
    return runden_plan

def erstelle_laufzettel_pdf(spielplan, runden_name):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    for feld_name, spiele in spielplan.items():
        pdf.add_page() 
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt=f"Laufzettel - {runden_name} - {feld_name}", ln=True, align='C')
        pdf.ln(10)
        
        for i, spiel in enumerate(spiele):
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(200, 8, txt=f"Spiel {i+1}", ln=True, align='L')
            pdf.set_font("Arial", '', 11)
            pdf.cell(200, 8, txt=f"{spiel['Team 1 Text']}  VS  {spiel['Team 2 Text']}", ln=True, align='L')
            pdf.cell(200, 8, txt="Satz 1:  ____ : ____", ln=True, align='L')
            pdf.cell(200, 8, txt="Satz 2:  ____ : ____", ln=True, align='L')
            pdf.ln(10)
    return pdf.output(dest='S').encode('latin-1')

# --- 2. DATENBANK & GEDAECHTNIS ---
if 'teilnehmer' not in st.session_state: st.session_state.teilnehmer = [f"Spieler {i} ({i})" for i in range(1, 21)]
if 'spielplan_r1' not in st.session_state: st.session_state.spielplan_r1 = None
if 'spielplan_r2' not in st.session_state: st.session_state.spielplan_r2 = None
if 'spielplan_r3' not in st.session_state: st.session_state.spielplan_r3 = None
if 'ergebnisse_r1' not in st.session_state: st.session_state.ergebnisse_r1 = {}
if 'ergebnisse_r2' not in st.session_state: st.session_state.ergebnisse_r2 = {}
if 'ergebnisse_r3' not in st.session_state: st.session_state.ergebnisse_r3 = {}
if 'endstand_tabelle' not in st.session_state: st.session_state.endstand_tabelle = None
if 'platz_17_bis_20' not in st.session_state: st.session_state.platz_17_bis_20 = []

# --- 3. BENUTZEROBERFLAECHE (UI) ---
st.set_page_config(layout="wide")
st.title("🏐 King of the Beach - Turnier Manager")

# -- SIDEBAR --
st.sidebar.header("Turniersteuerung")
uploaded_file = st.sidebar.file_uploader("Setzliste (CSV) hochladen", type=["csv"])

if uploaded_file is not None:
    try:
        bytes_data = uploaded_file.read()
        importierte_namen = []
        for line in bytes_data.decode("utf-8").splitlines()[1:]:
            line = line.strip()
            if not line: continue 
            teile = line.split(";") if ";" in line else line.split(",") if "," in line else [line]
            if len(teile) >= 3: anzeige_name = f"{teile[2].replace('\"', '').strip()} ({teile[1].replace('\"', '').strip()})"
            elif len(teile) == 2: anzeige_name = f"{teile[1].replace('\"', '').strip()} ({teile[0].replace('\"', '').strip()})"
            else: anzeige_name = teile[0].replace('"', '').strip()
            importierte_namen.append(anzeige_name)
        if len(importierte_namen) == 20: st.session_state.teilnehmer = importierte_namen
    except Exception as e: st.sidebar.error(f"Fehler: {e}")

if st.sidebar.button("📋 Turnier neu starten"):
    st.session_state.spielplan_r1 = erstelle_runden_spielplan_r1(st.session_state.teilnehmer)
    st.session_state.spielplan_r2 = None
    st.session_state.spielplan_r3 = None
    st.session_state.endstand_tabelle = None
    st.session_state.platz_17_bis_20 = []
    st.session_state.ergebnisse_r1 = {}
    st.session_state.ergebnisse_r2 = {}
    st.session_state.ergebnisse_r3 = {}

# ================= RUNDE 1 =================
if st.session_state.spielplan_r1:
    st.header("Spielplan: Runde 1")
    st.download_button("📄 Laufzettel R1 (PDF)", data=erstelle_laufzettel_pdf(st.session_state.spielplan_r1, "Runde 1"), file_name="Runde_1.pdf", mime="application/pdf", key="dl_r1")
    
    with st.expander("📝 Ergebnisse Runde 1 eintragen", expanded=(st.session_state.spielplan_r2 is None)):
        with st.form("ergebnisse_r1_form"):
            tabs = st.tabs(list(st.session_state.spielplan_r1.keys()))
            for idx, (feld_name, spiele) in enumerate(st.session_state.spielplan_r1.items()):
                with tabs[idx]:
                    for i, spiel in enumerate(spiele):
                        st.markdown(f"**Spiel {i+1}: {spiel['Team 1 Text']} vs {spiel['Team 2 Text']}**")
                        col1, col2, col3, col4 = st.columns(4)
                        key_pfx = f"r1_{feld_name}_spiel{i}"
                        with col1: st.session_state.ergebnisse_r1[f"{key_pfx}_s1_t1"] = st.number_input("Satz 1 Team 1", min_value=0, max_value=30, value=0, key=f"{key_pfx}_s1_t1")
                        with col2: st.session_state.ergebnisse_r1[f"{key_pfx}_s1_t2"] = st.number_input("Satz 1 Team 2", min_value=0, max_value=30, value=0, key=f"{key_pfx}_s1_t2")
                        with col3: st.session_state.ergebnisse_r1[f"{key_pfx}_s2_t1"] = st.number_input("Satz 2 Team 1", min_value=0, max_value=30, value=0, key=f"{key_pfx}_s2_t1")
                        with col4: st.session_state.ergebnisse_r1[f"{key_pfx}_s2_t2"] = st.number_input("Satz 2 Team 2", min_value=0, max_value=30, value=0, key=f"{key_pfx}_s2_t2")
                        st.divider()
            
            if st.form_submit_button("💾 Ergebnisse R1 speichern & Runde 2 auslosen"):
                stats = {p: {"saetze": 0, "diff": 0, "punkte": 0} for p in st.session_state.teilnehmer}
                for feld_name, spiele in st.session_state.spielplan_r1.items():
                    for i, spiel in enumerate(spiele):
                        key_pfx = f"r1_{feld_name}_spiel{i}"
                        s1_t1 = st.session_state.ergebnisse_r1[f"{key_pfx}_s1_t1"]
                        s1_t2 = st.session_state.ergebnisse_r1[f"{key_pfx}_s1_t2"]
                        s2_t1 = st.session_state.ergebnisse_r1[f"{key_pfx}_s2_t1"]
                        s2_t2 = st.session_state.ergebnisse_r1[f"{key_pfx}_s2_t2"]
                        
                        if s1_t1 > s1_t2: 
                            for p in spiel["Team 1 Spieler"]: stats[p]["saetze"] += 1
                        elif s1_t2 > s1_t1: 
                            for p in spiel["Team 2 Spieler"]: stats[p]["saetze"] += 1
                        if s2_t1 > s2_t2: 
                            for p in spiel["Team 1 Spieler"]: stats[p]["saetze"] += 1
                        elif s2_t2 > s2_t1: 
                            for p in spiel["Team 2 Spieler"]: stats[p]["saetze"] += 1
                        
                        for p in spiel["Team 1 Spieler"]:
                            stats[p]["punkte"] += (s1_t1 + s2_t1)
                            stats[p]["diff"] += ((s1_t1 + s2_t1) - (s1_t2 + s2_t2))
                        for p in spiel["Team 2 Spieler"]:
                            stats[p]["punkte"] += (s1_t2 + s2_t2)
                            stats[p]["diff"] += ((s1_t2 + s2_t2) - (s1_t1 + s2_t1))
                            
                sortierte_spieler = sorted(stats.items(), key=lambda x: (x[1]["saetze"], x[1]["diff"], x[1]["punkte"]), reverse=True)
                st.session_state.spielplan_r2 = erstelle_runde_2_spielplan([s[0] for s in sortierte_spieler])
                st.rerun()

# ================= RUNDE 2 =================
if st.session_state.spielplan_r2:
    st.divider()
    st.header("Spielplan: Runde 2 (Power Pools)")
    st.download_button("📄 Laufzettel R2 (PDF)", data=erstelle_laufzettel_pdf(st.session_state.spielplan_r2, "Runde 2"), file_name="Runde_2.pdf", mime="application/pdf", key="dl_r2")
    
    with st.expander("📝 Ergebnisse Runde 2 eintragen", expanded=(st.session_state.spielplan_r3 is None)):
        with st.form("ergebnisse_r2_form"):
            tabs_r2 = st.tabs(list(st.session_state.spielplan_r2.keys()))
            for idx, (feld_name, spiele) in enumerate(st.session_state.spielplan_r2.items()):
                with tabs_r2[idx]:
                    for i, spiel in enumerate(spiele):
                        st.markdown(f"**Spiel {i+1}: {spiel['Team 1 Text']} vs {spiel['Team 2 Text']}**")
                        col1, col2, col3, col4 = st.columns(4)
                        key_pfx = f"r2_{feld_name}_spiel{i}"
                        
                        with col1: st.session_state.ergebnisse_r2[f"{key_pfx}_s1_t1"] = st.number_input("Satz 1 Team 1", min_value=0, max_value=30, value=0, key=f"{key_pfx}_s1_t1")
                        with col2: st.session_state.ergebnisse_r2[f"{key_pfx}_s1_t2"] = st.number_input("Satz 1 Team 2", min_value=0, max_value=30, value=0, key=f"{key_pfx}_s1_t2")
                        with col3: st.session_state.ergebnisse_r2[f"{key_pfx}_s2_t1"] = st.number_input("Satz 2 Team 1", min_value=0, max_value=30, value=0, key=f"{key_pfx}_s2_t1")
                        with col4: st.session_state.ergebnisse_r2[f"{key_pfx}_s2_t2"] = st.number_input("Satz 2 Team 2", min_value=0, max_value=30, value=0, key=f"{key_pfx}_s2_t2")
                        st.divider()
            
            if st.form_submit_button("💾 Ergebnisse R2 speichern & Runde 3 berechnen"):
                r2_tabellen_pro_feld = {}
                for feld_name, spiele in st.session_state.spielplan_r2.items():
                    feld_spieler = set()
                    for spiel in spiele:
                        for p in spiel["Team 1 Spieler"]: feld_spieler.add(p)
                        for p in spiel["Team 2 Spieler"]: feld_spieler.add(p)
                        
                    stats = {p: {"saetze": 0, "diff": 0, "punkte": 0} for p in feld_spieler}
                    for i, spiel in enumerate(spiele):
                        key_pfx = f"r2_{feld_name}_spiel{i}"
                        s1_t1 = st.session_state.ergebnisse_r2[f"{key_pfx}_s1_t1"]
                        s1_t2 = st.session_state.ergebnisse_r2[f"{key_pfx}_s1_t2"]
                        s2_t1 = st.session_state.ergebnisse_r2[f"{key_pfx}_s2_t1"]
                        s2_t2 = st.session_state.ergebnisse_r2[f"{key_pfx}_s2_t2"]
                        
                        if s1_t1 > s1_t2: 
                            for p in spiel["Team 1 Spieler"]: stats[p]["saetze"] += 1
                        elif s1_t2 > s1_t1: 
                            for p in spiel["Team 2 Spieler"]: stats[p]["saetze"] += 1
                        if s2_t1 > s2_t2: 
                            for p in spiel["Team 1 Spieler"]: stats[p]["saetze"] += 1
                        elif s2_t2 > s2_t1: 
                            for p in spiel["Team 2 Spieler"]: stats[p]["saetze"] += 1
                        
                        for p in spiel["Team 1 Spieler"]:
                            stats[p]["punkte"] += (s1_t1 + s2_t1)
                            stats[p]["diff"] += ((s1_t1 + s2_t1) - (s1_t2 + s2_t2))
                        for p in spiel["Team 2 Spieler"]:
                            stats[p]["punkte"] += (s1_t2 + s2_t2)
                            stats[p]["diff"] += ((s1_t2 + s2_t2) - (s1_t1 + s2_t1))
                            
                    sortiert = sorted(stats.items(), key=lambda x: (x[1]["saetze"], x[1]["diff"], x[1]["punkte"]), reverse=True)
                    r2_tabellen_pro_
