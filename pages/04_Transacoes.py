import streamlit as st
from database import supabase

st.title("💰 Transações")

st.header("💸 Transferência entre Jogadores")

jogadores = supabase.table(
    "jogadores"
).select("*").execute()

nomes = [
    j["nome"]
    for j in jogadores.data
]

origem = st.selectbox(
    "Pagador",
    nomes,
    key="transferencia_origem"
)

destino = st.selectbox(
    "Recebedor",
    nomes,
    key="transferencia_destino"
)

valor = st.number_input(
    "Valor"
)

if st.button("Transferir"):

    supabase.table(
        "transacoes"
    ).insert({

        "tipo": "TRANSFERENCIA",
        "origem": origem,
        "destino": destino,
        "valor": valor,
        "descricao":
        "Pagamento entre jogadores"

    }).execute()

    st.success("Trasferência registrada!")

st.divider()



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


st.header("🏠 Compra de Propriedades")


partidas = (
        supabase.table("partidas").select("*").execute()
    )

partidas_dict = {
        p["nome_partida"]: p["id"]
        for p in partidas.data
    }

partida_nome = st.selectbox(
        "Partida",
        list(partidas_dict.keys()),
        key="partida_comprar_propriedade"
    )

partida_id = partidas_dict[partida_nome]

participantes = (
        supabase.table("partida_jogadores").select("*").eq("partida_id", partida_id).execute()
    )

jogadores_lista={}

for p in participantes.data:

        jogador = (
            supabase.table("jogadores").select("*").eq("id", p["jogador_id"]).execute()
        )

        jogadores_lista[
            jogador.data[0]["nome"]
        ] = p

jogador_nome = st.selectbox(
     "Jogador",
     list(jogadores_lista.keys())
)

registro_jogador = jogadores_lista[
     jogador_nome
]


propriedades = (
     supabase.table(
          "propriedades"
     ).select("*").eq("disponivel", True)
     .execute()
)

props_dict = {
     p["nome"]: p
     for p in propriedades.data
}

if not props_dict:
    st.warning("Nenhuma propriedade disponível")
    st.stop()

prop_nome = st.selectbox(
     "Propriedade", list(props_dict.keys()), key="compra_propriedade"
)

propriedade = props_dict[prop_nome]




if st.button("Comprar Propriedade"):
     
    saldo = registro_jogador["saldo"]

    valor = propriedade["valor_compra"]

    if saldo < valor:
        st.error(
            "Saldo insuficiente"
        )
        
    else:
        
        novo_saldo = saldo - valor
        supabase.table(
            "partida_jogadores"
        ).update({
            "saldo": novo_saldo
        }).eq("id", registro_jogador["id"]).execute()

        supabase.table(
                "propriedades_jogadores"
            ).insert({
                "partida_id": partida_id,
                "jogador_id": registro_jogador["jogador_id"],
                "propriedade_id": propriedade["id"]
            }).execute()

        supabase.table(
                "propriedades"    ).update({
                    "disponivel": False
                }).eq("id", propriedade["id"]).execute()

        supabase.table("transacoes").insert({
            "partida_id": partida_id,
            "jogador_id": registro_jogador["jogador_id"],
            "propriedade_id": propriedade["id"],
            "tipo": "COMPRA",
            "origem": "BANCO",
            "destino": jogador_nome,
            "valor": valor,
            "descricao": f"Compra da propriedade {prop_nome}"
        }).execute()

        st.success("Propriedade comprada!")
        st.rerun()

st.subheader("Saldo Atual")

dados_saldo = []    
for nome, registro in jogadores_lista.items():

        dados_saldo.append({
            "Jogador": nome,
            "Saldo": f"R$ {registro['saldo']:,.2f}"
        })
st.dataframe(dados_saldo)

st.divider()