import streamlit as st
from database import supabase
import qrcode
from io import BytesIO

st.title("📱 QR Code dos Jogadores")

jogadores = supabase.table("jogadores").select("*").execute()

if not jogadores.data:
    st.warning("Nenhum jogador encontrado.")
    st.stop()

base_url = "base_url = st.secrets["BASE_URL"] + "/Jogador?token=""

for j in jogadores.data:

    token = j.get("token")

    if not token:
        continue

    link = base_url + token

    qr = qrcode.make(link)

    buf = BytesIO()
    qr.save(buf)
    buf.seek(0)

    st.subheader(j["nome"])
    st.image(buf)
    st.code(link)
    st.divider()
