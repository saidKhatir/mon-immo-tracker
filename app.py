import streamlit as st
import lbc
import pandas as pd
import re
import os
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="LBC Immo Tracker Pro", layout="wide")
DB_FILE = "suivi_immo_complet.csv"

# --- FONCTIONS TECHNIQUES ---

def extract_id(url_or_id):
    """Nettoie l'URL pour ne garder que l'ID numérique"""
    if url_or_id.isdigit(): return url_or_id
    match = re.search(r"(\d{9,11})", url_or_id)
    return match.group(1) if match else url_or_id

def force_float(value):
    """Extrait un nombre propre de n'importe quelle donnée"""
    if value is None: return 0.0
    if isinstance(value, list): value = value[0] if len(value) > 0 else "0"
    text = str(value).replace('\xa0', '').replace(' ', '')
    cleaned = "".join(c for c in text if c.isdigit() or c in ".,")
    cleaned = cleaned.replace(",", ".")
    try: return float(cleaned) if cleaned else 0.0
    except: return 0.0

def get_immo_data(raw_input):
    """Récupère les données depuis l'API Leboncoin"""
    ad_id = extract_id(raw_input)
    client = lbc.Client()
    ad = client.get_ad(ad_id)
    attrs = {attr.key: attr.value_label for attr in ad.attributes}
    
    # Extraction de la surface (Attribut -> Titre)
    surface = force_float(attrs.get('square', '0'))
    if surface == 0:
        match = re.search(r"(\d+(?:[.,]\d+)?)\s*m²", ad.subject)
        surface = force_float(match.group(1)) if match else 0.0
        
    prix = force_float(ad.price)
    
    # Retourne le dictionnaire dans l'ordre souhaité des colonnes
    return {
        "Date Ajout": datetime.now().strftime("%d/%m/%Y"),
        "Lien": ad.url,
        "Titre": ad.subject,
        "Prix (€)": prix,
        "Surface (m²)": surface,
        "Prix/m² (€)": int(prix / surface) if surface > 0 else 0,
        "DPE": attrs.get('energy_rate', 'N/A'),
        "Charges / mois": "",
        "Exposition": "",
        "Note/Avis": "",
        "Travaux": "À définir",
        "Offre": ""
    }

# --- GESTION DES DONNÉES ---

def load_data():
    """Charge le CSV et force le type texte pour les colonnes modifiables"""
    if os.path.exists(DB_FILE):
        df_loaded = pd.read_csv(DB_FILE)
        champs_texte = ["Date Ajout", "Note/Avis", "Travaux", "Offre", "Charges / mois", "Exposition"]
        for col in champs_texte:
            if col in df_loaded.columns:
                df_loaded[col] = df_loaded[col].fillna("").astype(str)
        return df_loaded
    return pd.DataFrame()

def save_data(df_to_save):
    """Sauvegarde le DataFrame en CSV"""
    df_to_save.to_csv(DB_FILE, index=False, encoding='utf-8-sig')

# --- INTERFACE ---

st.title("🏠 Mon Assistant Immobilier")
st.markdown("Collez une URL Leboncoin pour enrichir votre tableau de suivi.")

df = load_data()

# Bloc d'ajout
with st.expander("➕ Ajouter une nouvelle annonce", expanded=df.empty):
    url_input = st.text_input("URL de l'annonce :", placeholder="https://www.leboncoin.fr/ad/...")
    if st.button("Analyser et Ajouter"):
        if url_input:
            with st.spinner('Récupération des informations...'):
                try:
                    new_ad = get_immo_data(url_input)
                    if not df.empty and new_ad['Lien'] in df['Lien'].values:
                        st.warning("Cette annonce est déjà dans votre liste.")
                    else:
                        new_row = pd.DataFrame([new_ad])
                        df = pd.concat([df, new_row], ignore_index=True)
                        save_data(df)
                        st.success("Annonce ajoutée !")
                        st.rerun()
                except Exception as e:
                    st.error(f"Erreur : {e}")

st.divider()

# Bloc d'affichage et édition
if not df.empty:
    st.subheader("📋 Annonces sélectionnées")
    
    # Éditeur de données interactif
    edited_df = st.data_editor(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Date Ajout": st.column_config.TextColumn("Date Ajout", disabled=True),
            "Lien": st.column_config.LinkColumn("Annonce", display_text="Lien"),
            "Prix (€)": st.column_config.NumberColumn(format="%d €"),
            "Prix/m² (€)": st.column_config.NumberColumn(format="%d €/m²"),
            "Travaux": st.column_config.SelectboxColumn(
                "Travaux",
                options=["Aucun", "Rafraîchissement", "Gros œuvre", "À définir"]
            ),
        },
        # On protège les colonnes extraites automatiquement
        disabled=["Date Ajout", "Lien", "Titre", "Prix (€)", "Surface (m²)", "Prix/m² (€)", "DPE"]
    )

    col_save, col_opt = st.columns([1, 4])
    
    with col_save:
        if st.button("💾 Enregistrer les notes"):
            save_data(edited_df)
            st.success("Modifications sauvegardées !")
            st.rerun()

    with col_opt:
        with st.popover("⚙️ Options et Suppression"):
            st.write("---")
            # Suppression d'une ligne
            ad_to_del = st.selectbox("Supprimer une annonce :", options=[""] + df["Titre"].tolist())
            if st.button("❌ Supprimer la ligne"):
                if ad_to_del:
                    df = df[df["Titre"] != ad_to_del]
                    save_data(df)
                    st.rerun()
            
            st.write("---")
            # Reset total
            if st.button("🔥 Tout effacer (Réinitialisation)", type="primary"):
                if os.path.exists(DB_FILE): os.remove(DB_FILE)
                st.rerun()
            
            st.write("---")
            # Export CSV
            csv_data = edited_df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
            st.download_button("📥 Télécharger Excel (CSV)", csv_data, "mon_suivi_immo.csv", "text/csv")
else:
    st.info("Aucune annonce pour le moment. Utilisez le formulaire ci-dessus.")