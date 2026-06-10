from database import supabase
import streamlit as st


st.title("🎲 Partidas")

st.subheader("Criar Partida")

nome_partida = st.text_input("Nome da Partida")

if st.button("Criar Partida"):

    supabase.table("partidas").insert({
        "nome_partida": nome_partida
    }).execute()


    st.success("Partida Criada")


st.subheader("Adicionar Jogadores")

partidas = supabase.table(
        "partidas"
    ).select("*").execute()

partidas_dict = {
        p["nome_partida"]: p["id"]
        for p in partidas.data
    }

partida_escolhida = st.selectbox(
        "Partida",
        list(partidas_dict.keys()),
        key="partida_adicionar_jogadores"
)
jogadores = supabase.table(
    "jogadores"
).select("*").execute()

jogadores_dict = {
    j["nome"]: j["id"]
    for j in jogadores.data
}

selecionados = st.multiselect(
    "Jogadores",
    list(jogadores_dict.keys())
)

if st.button("Adicionar"):

    partida_id = partidas_dict[
        partida_escolhida
    ]

    for nome in selecionados:

        supabase.table(
            "partida_jogadores"
        ).insert({

            "partida_id": partida_id,
            "jogador_id": jogadores_dict[nome],
            "saldo": 25000
        }).execute()

    st.success("Jogadores adicionados!")



