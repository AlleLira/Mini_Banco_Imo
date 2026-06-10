import streamlit as st
from database import supabase

st.title("🤝 Negociações")



# Buscar partidas
partidas = (
    supabase.table("partidas")
    .select("*")
    .execute()
)


if not partidas.data:
    st.warning("Nenhuma partida encontrada.")
    st.stop()

partidas_dict = {
    p["nome_partida"]: p["id"]
    for p in partidas.data
}

partida_nome = st.selectbox(
    "Partida",
    list(partidas_dict.keys()),
    key="negociacao_partida"
)

partida_id = partidas_dict[partida_nome]

# Buscar jogadores da partida
participantes = (
    supabase.table("partida_jogadores")
    .select("*")
    .eq("partida_id", partida_id)
    .execute()
)

jogadores = {}

for participante in participantes.data:

    jogador = (
        supabase.table("jogadores")
        .select("*")
        .eq("id", participante["jogador_id"])
        .execute()
    )

    jogadores[jogador.data[0]["nome"]] = participante

if len(jogadores) < 2:
    st.warning("A partida precisa ter pelo menos 2 jogadores.")
    st.stop()

# Seleção dos jogadores
vendedor = st.selectbox(
    "Vendedor",
    list(jogadores.keys()),
    key="vendedor"
)

compradores_disponiveis = [
    nome for nome in jogadores.keys()
    if nome != vendedor
]

comprador = st.selectbox(
    "Comprador",
    compradores_disponiveis,
    key="comprador"
)

vendedor_id = jogadores[vendedor]["jogador_id"]

# Buscar propriedades do vendedor
props = (
    supabase.table("propriedades_jogadores")
    .select("*")
    .eq("jogador_id", vendedor_id)
    .execute()
)

propriedades_dict = {}

for registro in props.data:

    prop = (
        supabase.table("propriedades")
        .select("*")
        .eq("id", registro["propriedade_id"])
        .execute()
    )

    if prop.data:
        propriedades_dict[prop.data[0]["nome"]] = registro

if not propriedades_dict:
    st.warning("Este jogador não possui propriedades.")
    st.stop()

propriedade_nome = st.selectbox(
    "Propriedade",
    list(propriedades_dict.keys()),
    key="propriedade_negociacao"
)

valor = st.number_input(
    "Valor da negociação",
    min_value=1.0,
    step=1.0
)


if st.button("Negociar"):


    try:

        saldo_comprador = jogadores[comprador]["saldo"]

        st.write("Saldo comprador:", saldo_comprador)

        if saldo_comprador < valor:

            st.error(
                "Comprador não possui saldo suficiente."
            )

        else:

            saldo_vendedor = jogadores[vendedor]["saldo"]

            # Debita comprador
            supabase.table("partida_jogadores").update({
                "saldo": saldo_comprador - valor
            }).eq(
                "id",
                jogadores[comprador]["id"]
            ).execute()

            # Credita vendedor
            supabase.table("partida_jogadores").update({
                "saldo": saldo_vendedor + valor
            }).eq(
                "id",
                jogadores[vendedor]["id"]
            ).execute()

            # Transfere propriedade
            supabase.table(
                "propriedades_jogadores"
            ).update({
                "jogador_id": jogadores[comprador]["jogador_id"]
            }).eq(
                "id",
                propriedades_dict[propriedade_nome]["id"]
            ).execute()

            # Registrar transação
            supabase.table("transacoes").insert({
                "partida_id": partida_id,
                "jogador_id": jogadores[comprador]["jogador_id"],
                "tipo": "NEGOCIACAO",
                "origem": vendedor,
                "destino": comprador,
                "valor": valor,
                "descricao": f"Negociação da propriedade {propriedade_nome}"
            }).execute()

            st.success(
                f"{comprador} comprou {propriedade_nome} de {vendedor} por R$ {valor:,.2f}"
            )
    except Exception as e:

        st.rerun(f'ERRO: {e}')