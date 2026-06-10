import streamlit as st
from database import supabase

st.title("💰 Transações Banco")

st.header("🎲 Transações Banco")

# ==========================
# PARTIDA
# ==========================

partidas = supabase.table("partidas").select("*").execute()

if not partidas.data:
    st.warning("Nenhuma partida encontrada.")

partidas_dict = {
    p["nome_partida"]: p["id"]
    for p in partidas.data
}

partida_nome = st.selectbox(
    "Partida",
    list(partidas_dict.keys()),
    key="banco_partida"
)

partida_id = partidas_dict[partida_nome]

# ==========================
# JOGADORES
# ==========================

participantes = supabase.table(
    "partida_jogadores"
).select("*").eq(
    "partida_id",
    partida_id
).execute()

jogadores = {}

for p in participantes.data:

    jogador = supabase.table(
        "jogadores"
    ).select("*").eq(
        "id",
        p["jogador_id"]
    ).execute()

    if jogador.data:
        jogadores[jogador.data[0]["nome"]] = p

if not jogadores:
    st.warning("Nenhum jogador encontrado.")
    st.stop()

jogador_nome = st.selectbox(
    "Jogador",
    list(jogadores.keys()),
    key="banco_jogador"
)

registro = jogadores[jogador_nome]

jogador_id = registro["jogador_id"]

saldo_atual = registro["saldo"]

st.metric("💰 Saldo atual", f"R$ {saldo_atual:,.2f}")

st.divider()

# ==========================
# PAGAR PARA JOGADOR
# ==========================

st.subheader("💵 Banco paga jogador")

valor_credito = st.number_input(
    "Valor a pagar",
    min_value=0.0,
    step=10.0,
    key="credito"
)

if st.button("Pagar jogador"):

    novo_saldo = saldo_atual + valor_credito

    supabase.table("partida_jogadores").update({
        "saldo": novo_saldo
    }).eq(
        "id",
        registro["id"]
    ).execute()

    supabase.table("transacoes").insert({
        "partida_id": partida_id,
        "jogador_id": jogador_id,
        "tipo": "CREDITO_BANCO",
        "origem": "BANCO",
        "destino": jogador_nome,
        "valor": valor_credito,
        "descricao": "Pagamento do banco"
    }).execute()

    st.success(f"{jogador_nome} recebeu R$ {valor_credito:,.2f}")
    st.rerun()

st.divider()

# ==========================
# COBRAR DO JOGADOR
# ==========================

st.subheader("💸 Banco cobra jogador")

valor_debito = st.number_input(
    "Valor a cobrar",
    min_value=0.0,
    step=10.0,
    key="debito"
)

if st.button("Cobrar jogador"):

    if saldo_atual < valor_debito:
        st.error("Saldo insuficiente.")
        st.stop()

    novo_saldo = saldo_atual - valor_debito

    supabase.table("partida_jogadores").update({
        "saldo": novo_saldo
    }).eq(
        "id",
        registro["id"]
    ).execute()

    supabase.table("transacoes").insert({
        "partida_id": partida_id,
        "jogador_id": jogador_id,
        "tipo": "DEBITO_BANCO",
        "origem": jogador_nome,
        "destino": "BANCO",
        "valor": valor_debito,
        "descricao": "Cobrança do banco"
    }).execute()

    st.success(f"{jogador_nome} pagou R$ {valor_debito:,.2f}")
    st.rerun()
