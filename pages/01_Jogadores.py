from database import supabase
import streamlit as st

st.title("👤 Jogadores")

nome = st.text_input("Nome do jogador")

if st.button("Cadastrar"):

    supabase.table("jogadores").insert({
        "nome": nome
    }).execute()

    st.success("Jogador cadastrado!")

jogadores = supabase.table(
    "jogadores"
).select("*").execute()

st.subheader("Jogadores Cadastrados")

st.dataframe(jogadores.data)
