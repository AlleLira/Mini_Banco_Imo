import streamlit as st
from database import supabase

st.title("🏠 Propriedades")

nome = st.text_input(
    "Nome da Propriedade"
)

valor_compra = st.number_input(
    "Valor de Compra"
)

valor_hipoteca = st.number_input(
    "Valor Hipoteca"
)


if st.button("Cadastrar"):

    supabase.table(
        "propriedades"
    ).insert({

        "nome": nome,
        "valor_compra": valor_compra,
        "valor_hipoteca": valor_hipoteca
    }).execute()

    st.success("Propriedade Cadastrada!")

    propriedades = supabase.table(
        "propriedades"
    ).select("*").execute()

    st.dataframe(propriedades.data)