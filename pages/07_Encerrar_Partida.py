import streamlit as st
from database import supabase

st.title("🏆 Encerrar Partida")

# Buscar partidas
partidas = (
    supabase.table("partidas")
    .select("*")
    .execute()
)

if not partidas.data:
    st.warning("Nenhuma partida cadastrada.")
    st.stop()

# Lista de partidas
partidas_dict = {
    p["nome_partida"]: p["id"]
    for p in partidas.data
}

partida_nome = st.selectbox(
    "Selecione a Partida",
    list(partidas_dict.keys())
)

partida_id = partidas_dict[partida_nome]

# Buscar participantes da partida
participantes = (
    supabase.table("partida_jogadores")
    .select("*")
    .eq("partida_id", partida_id)
    .execute()
)

if not participantes.data:
    st.warning("Esta partida não possui jogadores.")
    st.stop()

ranking = []

for p in participantes.data:

    jogador = (
        supabase.table("jogadores")
        .select("*")
        .eq("id", p["jogador_id"])
        .execute()
    )

    ranking.append({
        "Jogador": jogador.data[0]["nome"],
        "JogadorID": p["jogador_id"],
        "Patrimonio": p["saldo"]
    })

# Ordenar por patrimônio
ranking = sorted(
    ranking,
    key=lambda x: x["Patrimonio"],
    reverse=True
)

st.subheader("📊 Ranking Final")

ranking_exibicao = []

for posicao, item in enumerate(ranking, start=1):

    ranking_exibicao.append({
        "Posição": posicao,
        "Jogador": item["Jogador"],
        "Patrimônio": f"R$ {item['Patrimonio']:,.2f}"
    })

st.dataframe(
    ranking_exibicao,
    use_container_width=True
)

# Vencedor
vencedor = ranking[0]

st.success(
    f"🏆 Líder Atual: {vencedor['Jogador']} "
    f"com patrimônio de R$ {vencedor['Patrimonio']:,.2f}"
)

# Encerrar partida
if st.button("🏁 Encerrar Partida"):

    supabase.table("partidas").update({
        "status": "ENCERRADA",
        "vencedor_id": vencedor["JogadorID"]
    }).eq(
        "id",
        partida_id
    ).execute()

    st.success(
        f"Partida encerrada! "
        f"Vencedor: {vencedor['Jogador']}"
    )

    st.rerun()