import streamlit as st
import lbc
import pandas as pd
import re
import os

# --- CONFIGURATION ---
st.set_page_config(page_title="LBC Tracker - No Surface", layout="wide")
DB_FILE = "suivi_immo_simple.csv"

def clean_price(value):
    """Extrait le prix numérique uniquement"""
    if value is None: return 0.0
    if isinstance(value, (int, float)): return float(value)
    # Nettoyage des caractères non numériques pour le prix
    text = str(value).replace('\xa0', '').replace(' ', '')
    numeric_part = "".join(c for c in text if c.isdigit() or c in ".,")
    numeric_part = numeric_part.replace(",", ".")
    try:
        return float(numeric_part)
    except:
        return 0.0

def get_immo_data(url_or_id):
    client = lbc.Client()
    ad = client.get_ad(url_or_id)
    
    # Dictionnaire des attributs pour le DPE et autres
    attrs = {attr.key: attr.value_label for attr in ad.attributes}
    
    # Extraction simplifiée (Sans aucune mesure de surface)
    prix = clean_price(ad.price)
    dpe = attrs.get('energy_rate', 'Non spécifié')
    
    # Recherche des charges dans la description
    charges = "Non spécifié"
    if ad.body:
        match = re.search(r"(\d+(?:[.,]\d+)?)\s*€?\s*(?:de\s*)?charges", ad.body, re.IGNORECASE)
        if match:
            charges = f"{match.group(1)} €"

    # Nom du vendeur ou ID
    vendeur = attrs.get('contact_name', f"ID: {ad._user_id[:8]}")

    return {
        "Lien": ad.url,
        "Titre": ad.subject,
        "Localisation": f"{ad.location.city} ({ad.location.zipcode})",
        "Prix (€)": prix,
        "Vendeur": vendeur,
        "Charges": charges,
        "DPE": dpe,
        "Type": attrs.get('real_estate_type', 'Non précisé')
    }

# --- INTERFACE STREAMLIT ---
st.title("🏠 Suivi Immo (Version Simplifiée)")
st.info("Cette version n'extrait pas la surface pour éviter les erreurs de conversion.")

if 'db_simple' not in st.session_state:
    if os.path.exists(DB_FILE):
        st.session_state.db_simple = pd.read_csv(DB_FILE).to_dict(orient="records")
    else:
        st.session_state.db_simple = []

url_input = st.text_input("URL ou ID de l'annonce :")

c1, c2 = st.columns([1, 4])
with c1:
    if st.button("➕ Ajouter"):
        if url_input:
            with st.spinner("Analyse en cours..."):
                try:
                    data = get_immo_data(url_input)
                    st.session_state.db_simple.append(data)
                    pd.DataFrame(st.session_state.db_simple).to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                    st.success("Ajouté !")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur : {e}")

with c2:
    if st.button("🗑️ Reset"):
        if os.path.exists(DB_FILE): os.remove(DB_FILE)
        st.session_state.db_simple = []
        st.rerun()

st.divider()

if st.session_state.db_simple:
    df = pd.DataFrame(st.session_state.db_simple)
    st.dataframe(df, use_container_width=True, column_config={
        "Lien": st.column_config.LinkColumn("Lien"),
        "Prix (€)": st.column_config.NumberColumn(format="%d €")
    })
    
    csv = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
    st.download_button("📥 Exporter CSV", csv, "suivi_immo_simple.csv", "text/csv")