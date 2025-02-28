import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster

st.set_page_config(page_title="Carte des Expéditeurs de Casablanca", layout="wide")

# Authentication
USER_CREDENTIALS = {"admin": "password123"}  # Change this as needed

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def login():
    st.title("🔐 Connexion requise")
    username = st.text_input("Identifiant")
    password = st.text_input("Mot de passe", type="password")
    if st.button("Se connecter"):
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Identifiant ou mot de passe incorrect")

def logout():
    st.session_state.authenticated = False
    st.rerun()

if not st.session_state.authenticated:
    login()
    st.stop()

# Hide sidebar
st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        .stButton button { width: 100%; }
    </style>
""", unsafe_allow_html=True)

# Load Data
@st.cache_data
def charger_donnees():
    return pd.read_csv("customers_enriched_casa_google.csv")

df = charger_donnees()
df_valide = df.dropna(subset=['Latitude', 'Longitude'])
df_valide['Latitude'] = df_valide['Latitude'].astype(float)
df_valide['Longitude'] = df_valide['Longitude'].astype(float)

hub_location = [33.60681000262012, -7.555809154987765]

# Create Map
m = folium.Map(location=hub_location, zoom_start=11, tiles="cartodbpositron")
marker_cluster = MarkerCluster().add_to(m)

zones_collecte = [
    {"lat": hub_location[0], "lon": hub_location[1], "radius": 5000, "color": "green", "cutoff": "16h00"},
    {"lat": hub_location[0], "lon": hub_location[1], "radius": 9000, "color": "yellow", "cutoff": "15h30"},
    {"lat": hub_location[0], "lon": hub_location[1], "radius": 13500, "color": "red", "cutoff": "15h00"},
]

for zone in zones_collecte:
    folium.Circle(
        location=[zone["lat"], zone["lon"]],
        radius=zone["radius"],
        color=zone["color"],
        fill=True,
        fill_opacity=0.15,
        popup=f"Heure limite de collecte : {zone['cutoff']}",
        weight=2,
    ).add_to(m)

folium.Marker(
    hub_location,
    popup="🚛 Chrono Diali - HUB CASABLANCA - WH",
    icon=folium.Icon(color="black", icon="home", prefix="fa"),
).add_to(m)

pins_sur_carte = 0
for _, row in df_valide.iterrows():
    folium.Marker(
        [row["Latitude"], row["Longitude"]],
        popup=folium.Popup(
            f"""
            <b>📍 {row['Name']}</b><br>
            Adresse : {row['Address Line 1 (Building No / Appartment / Suite Name)']}<br>
            Ville : {row['City']}<br>
            Code : {row['Customer Code']}
            """,
            max_width=300
        ),
        icon=folium.Icon(color="blue", icon="info-sign"),
    ).add_to(marker_cluster)
    pins_sur_carte += 1

folium.LayerControl().add_to(m)

# Display Map
st.title("Expéditeurs & Zones de Collecte à Casablanca")
folium_static(m, width=1200, height=600)  



# Instructions & Stats
st.subheader("📊 Statistiques de la Carte")
st.write(f"Total des expéditeurs : {len(df)}")

st.subheader("ℹ️ Info sur le Regroupement")
st.info("""
1️⃣ Cliquez sur les groupes pour zoomer  
2️⃣ Zoomez manuellement pour voir plus de détails  
3️⃣ Au zoom maximum, les points groupés s'étaleront
""")

st.subheader("📍 Zones de Collecte")
st.markdown("""
🟢 Vert :limite 16h00
🟡 Jaune : limite 15h30  
🔴 Rouge : limite 15h00
""")

st.subheader("📋 Données des Expéditeurs")
st.dataframe(
    df_valide[['Customer Code', 'Name', 'Address Line 1 (Building No / Appartment / Suite Name)', 'City', 'Latitude', 'Longitude']],
    use_container_width=True
)

# Logout Button
st.button("🚪 Se déconnecter", on_click=logout)
