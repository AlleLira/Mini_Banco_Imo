import streamlit as st
from database import supabase

st.title("🏠 Casas e Hotéis")

# ==========================
# PARTIDA
# ==========================

partidas = supabase.table(
    "partidas"
).select("*").execute()

if not partidas.data:
    st.warning("Nenhuma partida cadastrada.")
    st.stop()

partidas_dict = {
    p["nome_partida"]: p["id"]
    for p in partidas.data
}

partida_nome = st.selectbox(
    "Partida",
    list(partidas_dict.keys())
)

partida_id = partidas_dict[partida_nome]

# ==========================
# JOGADORES DA PARTIDA
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

    jogadores[
        jogador.data[0]["nome"]
    ] = p

if not jogadores:
    st.warning("Nenhum jogador na partida.")
    st.stop()

jogador_nome = st.selectbox(
    "Jogador",
    list(jogadores.keys())
)

registro_jogador = jogadores[jogador_nome]

jogador_id = registro_jogador["jogador_id"]

# ==========================
# PROPRIEDADES DO JOGADOR
# ==========================

props_jogador = (
    supabase.table(
        "propriedades_jogadores"
    )
    .select("*")
    .eq("jogador_id", jogador_id)
    .execute()
)

propriedades = {}

for p in props_jogador.data:

    prop = supabase.table(
        "propriedades"
    ).select("*").eq(
        "id",
        p["propriedade_id"]
    ).execute()

    propriedades[
        prop.data[0]["nome"]
    ] = {
        "registro": p,
        "propriedade": prop.data[0]
    }

if not propriedades:
    st.warning("Jogador não possui propriedades.")
    st.stop()

propriedade_nome = st.selectbox(
    "Propriedade",
    list(propriedades.keys())
)

dados = propriedades[propriedade_nome]

registro_prop = dados["registro"]

registro_prop = (
    supabase.table(
        "propriedades_jogadores"
    )
    .select("*")
    .eq(
        "id",
        registro_prop["id"]
    )
    .execute()
    .data[0]
)

# ==========================
# INFORMAÇÕES
# ==========================

st.subheader("Informações")

st.write(
    f"Casas atuais: {registro_prop['casas']}"
)

st.write(
    f"Hotel: {'Sim' if registro_prop['hotel'] else 'Não'}"
)

st.write(
    f"Saldo: R$ {registro_jogador['saldo']:.2f}"
)

# ==========================
# DADOS DO BANCO
# ==========================

banco = supabase.table(
    "banco"
).select("*").limit(1).execute()

dados_banco = banco.data[0]

st.write(
    f"Casas disponíveis no banco: {dados_banco['casas_disponiveis']}"
)

st.write(
    f"Hotéis disponíveis no banco: {dados_banco['hoteis_disponiveis']}"
)

st.divider()

# ==========================
# COMPRA DE CASA
# ==========================

st.subheader("Comprar Casa")

valor_casa = st.number_input(
    "Valor da Casa",
    value=50.0,
    key="valor_casa"
)

if st.button("Comprar Casa"):

    saldo = registro_jogador["saldo"]

    if saldo < valor_casa:

        st.error("Saldo insuficiente.")

    elif dados_banco["casas_disponiveis"] <= 0:

        st.error("Banco sem casas.")

    elif registro_prop["hotel"]:

        st.error(
            "Esta propriedade já possui hotel."
        )

    else:

        novo_saldo = saldo - valor_casa

        supabase.table(
            "partida_jogadores"
        ).update({

            "saldo": novo_saldo

        }).eq(
            "id",
            registro_jogador["id"]
        ).execute()

        casas_atuais = registro_prop.get("casas")

        if casas_atuais is None:
            casas_atuais = 0

        novo_total = casas_atuais + 1

        supabase.table(
            "propriedades_jogadores"
        ).update({
            "casas": novo_total
        }).eq(
            "id",
            registro_prop["id"]
        ).execute()

        supabase.table(
            "banco"
        ).update({

            "casas_disponiveis":
            dados_banco["casas_disponiveis"] - 1

        }).eq(
            "id",
            dados_banco["id"]
        ).execute()

        supabase.table(
            "transacoes"
        ).insert({

            "partida_id": partida_id,
            "jogador_id": jogador_id,
            "tipo": "COMPRA_CASA",
            "origem": "BANCO",
            "destino": jogador_nome,
            "valor": valor_casa,
            "descricao":
            f"Compra de casa em {propriedade_nome}"

        }).execute()

        st.success(
    f"Casa comprada. Total de casas: {novo_total}"
)

        st.rerun()

# ==========================
# COMPRA DE HOTEL
# ==========================

st.subheader("Comprar Hotel")

valor_hotel = st.number_input(
    "Valor do Hotel",
    value=200.0,
    key="valor_hotel"
)

if st.button("Comprar Hotel"):

    saldo = registro_jogador["saldo"]

    if registro_prop["hotel"]:

        st.error(
            "A propriedade já possui hotel."
        )

    elif registro_prop["casas"] < 4:

        st.error(
            "Necessário possuir 4 casas."
        )

    elif saldo < valor_hotel:

        st.error(
            "Saldo insuficiente."
        )

    elif dados_banco["hoteis_disponiveis"] <= 0:

        st.error(
            "Banco sem hotéis."
        )

    else:

        novo_saldo = saldo - valor_hotel

        supabase.table(
            "partida_jogadores"
        ).update({

            "saldo": novo_saldo

        }).eq(
            "id",
            registro_jogador["id"]
        ).execute()

        supabase.table(
            "propriedades_jogadores"
        ).update({

            "hotel": True,
            "casas": 0

        }).eq(
            "id",
            registro_prop["id"]
        ).execute()

        supabase.table(
            "banco"
        ).update({

            "hoteis_disponiveis":
            dados_banco["hoteis_disponiveis"] - 1,

            "casas_disponiveis":
            dados_banco["casas_disponiveis"] + 4

        }).eq(
            "id",
            dados_banco["id"]
        ).execute()

        supabase.table(
            "transacoes"
        ).insert({

            "partida_id": partida_id,
            "jogador_id": jogador_id,
            "tipo": "COMPRA_HOTEL",
            "origem": "BANCO",
            "destino": jogador_nome,
            "valor": valor_hotel,
            "descricao":
            f"Compra de hotel em {propriedade_nome}"

        }).execute()

        st.success("Hotel comprado!")

        st.rerun()