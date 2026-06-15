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
if 'rangliste_r1' not in st.session_state: st.session_state.rangliste_r1 = None
if 'rangliste_r2' not in st.session_state: st.session_state.rangliste_r2 = None

# --- 3. BENUTZEROBERFLAECHE (UI) ---
st.set_page_config(layout="wide")
st.title("🏐 TuB - King of the Beach - Turnier Manager")

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
    st.session_state.rangliste_r1 = None
    st.session_state.rangliste_r2 = None
    st.rerun()

# ================= RUNDE 1 =================
if st.session_state.spielplan_r1:
    st.header("Spielplan: Runde 1")
    st.download_button("📄 Laufzettel R1 (PDF)", data=erstelle_laufzettel_pdf(st.session_state.spielplan_r1, "Runde 1"), file_name="Runde_1.pdf", mime="application/pdf", key="dl_r1")
    
    # NEU: Sofort sichtbare Auswertungstabelle für Runde 1
    if st.session_state.rangliste_r1:
        st.success("✅ Ergebnisse für Runde 1 sind gespeichert!")
        st.subheader("📊 Auswertungstabelle: Stand nach Runde 1")
        data_r1 = []
        for idx, (spieler, s_stats) in enumerate(st.session_state.rangliste_r1, 1):
            data_r1.append({
                "Platz": idx,
                "Spieler": spieler.split('(')[0].strip(),
                "Gewonnene Sätze": s_stats["saetze"],
                "Ball-Differenz": s_stats["diff"],
                "Eigene Punkte": s_stats["punkte"]
            })
        st.dataframe(data_r1, use_container_width=True)
        st.write("---")

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
                st.session_state.rangliste_r1 = sortierte_spieler
                st.session_state.spielplan_r2 = erstelle_runde_2_spielplan([s[0] for s in sortierte_spieler])
                st.rerun()

# ================= RUNDE 2 =================
if st.session_state.spielplan_r2:
    st.divider()
    st.header("Spielplan: Runde 2 (Power Pools)")
    st.download_button("📄 Laufzettel R2 (PDF)", data=erstelle_laufzettel_pdf(st.session_state.spielplan_r2, "Runde 2"), file_name="Runde_2.pdf", mime="application/pdf", key="dl_r2")
    
    # NEU: Sofort sichtbare Pool-Tabellen für Runde 2
    if st.session_state.rangliste_r2:
        st.success("✅ Ergebnisse für Runde 2 sind gespeichert!")
        st.subheader("📊 Auswertungstabelle: Pools nach Runde 2")
        
        spalten_r2 = st.columns(5)
        for idx, (feld_name, sortierte_liste) in enumerate(st.session_state.rangliste_r2.items()):
            with spalten_r2[idx]:
                st.markdown(f"**{feld_name}**")
                data_r2 = []
                for p_idx, (spieler, s_stats) in enumerate(sortierte_liste, 1):
                    data_r2.append({
                        "Rang": p_idx,
                        "Spieler": spieler.split('(')[0].strip(),
                        "Sätze": s_stats["saetze"],
                        "Diff": s_stats["diff"]
                    })
                st.dataframe(data_r2, use_container_width=True)
        st.write("---")

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
                st.session_state.rangliste_r2 = {}
                
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
                    r2_tabellen_pro_feld[feld_name] = [s[0] for s in sortiert]
                    st.session_state.rangliste_r2[feld_name] = sortiert
                
                st.session_state.platz_17_bis_20 = r2_tabellen_pro_feld["Feld 5"]
                st.session_state.spielplan_r3 = erstelle_runde_3_spielplan(r2_tabellen_pro_feld)
                st.rerun()

# ================= RUNDE 3 =================
if st.session_state.spielplan_r3:
    st.divider()
    st.header("Spielplan: Runde 3 (Platzierungen)")
    st.download_button("📄 Laufzettel R3 (PDF)", data=erstelle_laufzettel_pdf(st.session_state.spielplan_r3, "Runde 3"), file_name="Runde_3.pdf", mime="application/pdf", key="dl_r3")
    
    with st.expander("📝 Ergebnisse Runde 3 eintragen", expanded=(st.session_state.endstand_tabelle is None)):
        with st.form("ergebnisse_r3_form"):
            tabs_r3 = st.tabs(list(st.session_state.spielplan_r3.keys()))
            for idx, (feld_name, spiele) in enumerate(st.session_state.spielplan_r3.items()):
                with tabs_r3[idx]:
                    for i, spiel in enumerate(spiele):
                        st.markdown(f"**Spiel {i+1}: {spiel['Team 1 Text']} vs {spiel['Team 2 Text']}**")
                        col1, col2, col3, col4 = st.columns(4)
                        key_pfx = f"r3_{feld_name}_spiel{i}"
                        
                        with col1: st.session_state.ergebnisse_r3[f"{key_pfx}_s1_t1"] = st.number_input("Satz 1 Team 1", min_value=0, max_value=30, value=0, key=f"{key_pfx}_s1_t1")
                        with col2: st.session_state.ergebnisse_r3[f"{key_pfx}_s1_t2"] = st.number_input("Satz 1 Team 2", min_value=0, max_value=30, value=0, key=f"{key_pfx}_s1_t2")
                        with col3: st.session_state.ergebnisse_r3[f"{key_pfx}_s2_t1"] = st.number_input("Satz 2 Team 1", min_value=0, max_value=30, value=0, key=f"{key_pfx}_s2_t1")
                        with col4: st.session_state.ergebnisse_r3[f"{key_pfx}_s2_t2"] = st.number_input("Satz 2 Team 2", min_value=0, max_value=30, value=0, key=f"{key_pfx}_s2_t2")
                        st.divider()

            if st.form_submit_button("🏆 Ergebnisse R3 speichern & Endstand berechnen"):
                finale_platzierungen = []
                
                for f_idx in range(1, 5):
                    feld_name = f"Feld {f_idx}"
                    spiele = st.session_state.spielplan_r3[feld_name]
                    
                    feld_spieler = set()
                    for spiel in spiele:
                        for p in spiel["Team 1 Spieler"]: feld_spieler.add(p)
                        for p in spiel["Team 2 Spieler"]: feld_spieler.add(p)
                        
                    stats = {p: {"saetze": 0, "diff": 0, "punkte": 0} for p in feld_spieler}
                    for i, spiel in enumerate(spiele):
                        key_pfx = f"r3_{feld_name}_spiel{i}"
                        s1_t1 = st.session_state.ergebnisse_r3[f"{key_pfx}_s1_t1"]
                        s1_t2 = st.session_state.ergebnisse_r3[f"{key_pfx}_s1_t2"]
                        s2_t1 = st.session_state.ergebnisse_r3[f"{key_pfx}_s2_t1"]
                        s2_t2 = st.session_state.ergebnisse_r3[f"{key_pfx}_s2_t2"]
                        
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
                    finale_platzierungen.extend([s[0] for s in sortiert])
                
                finale_platzierungen.extend(st.session_state.platz_17_bis_20)
                st.session_state.endstand_tabelle = finale_platzierungen
                st.rerun()

# ================= ENDSTAND / SIEGEREHRUNG =================
if st.session_state.endstand_tabelle:
    st.balloons()
    st.divider()
    st.header("🏆 Offizieller Endstand des Turniers 🏆")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    for i in range(20):
        platz = i + 1
        voller_name = st.session_state.endstand_tabelle[i]
        name_ohne_klammer = voller_name.split('(')[0].strip()
        
        if platz == 1: text = f"🥇 **1. Platz:** {name_ohne_klammer}"
        elif platz == 2: text = f"🥈 **2. Platz:** {name_ohne_klammer}"
        elif platz == 3: text = f"🥉 **3. Platz:** {name_ohne_klammer}"
        else: text = f"**{platz}. Platz:** {name_ohne_klammer}"
        
        if i < 4: col1.success(text)
        elif i < 8: col2.info(text)
        elif i < 12: col3.warning(text)
        elif i < 16: col4.error(text)
        else:
            html_text = f"{platz}. Platz: {name_ohne_klammer}"
            col5.markdown(
                f"<div style='background-color: #4a148c; color: #ffffff; padding: 10px; margin-bottom: 8px; border-radius: 5px; border-left: 5px solid #ab47bc; font-weight: bold;'>{html_text}</div>", 
                unsafe_allow_html=True
            )
            
    st.write("---")
    st.subheader("📊 Offizielle Gesamt-Rangliste")
    data_final = []
    for i, voller_name in enumerate(st.session_state.endstand_tabelle, 1):
        data_final.append({
            "Endplatzierung": f"{i}. Platz",
            "Spieler": voller_name.split('(')[0].strip()
        })
    st.dataframe(data_final, use_container_width=True)
