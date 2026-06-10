import streamlit as st
from database import supabase

st.title("👤 Área do Jogador")

# ==========================
# JOGADORES
# ==========================

jogadores = (
    supabase.table("jogadores")
    .select("*")
    .execute()
)

if not jogadores.data:
    st.warning("Nenhum jogador cadastrado.")
    st.stop()

jogadores_dict = {
    j["nome"]: j["id"]
    for j in jogadores.data
}

jogador_nome = st.selectbox(
    "Jogador",
    list(jogadores_dict.keys())
)

jogador_id = jogadores_dict[
    jogador_nome
]

# ==========================
# PARTICIPAÇÃO
# ==========================

participacao = (
    supabase.table("partida_jogadores")
    .select("*")
    .eq("jogador_id", jogador_id)
    .execute()
)

if not participacao.data:
    st.warning(
        "Jogador não participa de nenhuma partida."
    )
    st.stop()

registro_jogador = participacao.data[-1]

saldo = registro_jogador["saldo"]

# ==========================
# SALDO
# ==========================

col1, col2 = st.columns(2)

with col1:

    st.metric(
        "💰 Saldo Atual",
        f"R$ {saldo:,.2f}"
    )

# ==========================
# PROPRIEDADES
# ==========================

props = (
    supabase.table(
        "propriedades_jogadores"
    )
    .select("*")
    .eq(
        "jogador_id",
        jogador_id
    )
    .execute()
)

# ==========================
# PATRIMÔNIO
# ==========================

patrimonio = saldo

total_hipotecas = 0

dados_props = []

for p in props.data:

    propriedade = (
        supabase.table(
            "propriedades"
        )
        .select("*")
        .eq(
            "id",
            p["propriedade_id"]
        )
        .execute()
    )

    if not propriedade.data:
        continue

    prop = propriedade.data[0]

    valor_prop = prop["valor_compra"]

    patrimonio += valor_prop

    if not p["hipotecada"]:
        total_hipotecas += (
            prop["valor_hipoteca"]
        )

    dados_props.append({

        "Propriedade":
        prop["nome"],

        "Casas":
        p["casas"],

        "Hotel":
        "Sim"
        if p["hotel"]
        else "Não",

        "Hipotecada":
        "Sim"
        if p["hipotecada"]
        else "Não"

    })

with col2:

    st.metric(
        "🏆 Patrimônio",
        f"R$ {patrimonio:,.2f}"
    )

# ==========================
# ESTOU FALIDO
# ==========================

st.divider()

st.subheader(
    "🚨 Estou Falido"
)

st.warning(
    f"Você pode levantar "
    f"R$ {total_hipotecas:,.2f} "
    f"em hipotecas."
)

# ==========================
# PROPRIEDADES
# ==========================

st.divider()

st.subheader(
    "🏠 Minhas Propriedades"
)

if dados_props:

    st.dataframe(
        dados_props,
        use_container_width=True
    )

else:

    st.info(
        "Nenhuma propriedade."
    )

# ==========================
# HISTÓRICO
# ==========================

st.divider()

st.subheader(
    "📜 Histórico"
)

historico = (
    supabase.table(
        "transacoes"
    )
    .select("*")
    .eq(
        "jogador_id",
        jogador_id
    )
    .order(
        "id",
        desc=True
    )
    .execute()
)

dados_historico = []

for t in historico.data:

    dados_historico.append({

        "Tipo":
        t["tipo"],

        "Origem":
        t["origem"],

        "Destino":
        t["destino"],

        "Valor":
        f"R$ {t['valor']:,.2f}",

        "Descrição":
        t["descricao"]

    })

if dados_historico:

    st.dataframe(
        dados_historico,
        use_container_width=True
    )

else:

    st.info(
        "Nenhuma transação encontrada."
    )

# ==========================
# RESUMO
# ==========================

st.divider()

qtd_props = len(props.data)

qtd_casas = sum(
    p["casas"] or 0
    for p in props.data
)

qtd_hoteis = sum(
    1
    for p in props.data
    if p["hotel"]
)

qtd_hipotecas = sum(
    1
    for p in props.data
    if p["hipotecada"]
)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "🏠 Propriedades",
        qtd_props
    )

with c2:
    st.metric(
        "🏡 Casas",
        qtd_casas
    )

with c3:
    st.metric(
        "🏨 Hotéis",
        qtd_hoteis
    )

with c4:
    st.metric(
        "🏦 Hipotecas",
        qtd_hipotecas
    )