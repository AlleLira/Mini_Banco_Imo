import streamlit as st
from database import supabase

st.title("🏦 Hipotecas")

# ==========================
# PARTIDAS
# ==========================

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
    list(partidas_dict.keys())
)

partida_id = partidas_dict[partida_nome]

# ==========================
# JOGADORES DA PARTIDA
# ==========================

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

    if jogador.data:
        jogadores[
            jogador.data[0]["nome"]
        ] = participante

if not jogadores:
    st.warning(
        "Nenhum jogador encontrado."
    )
    st.stop()

jogador_nome = st.selectbox(
    "Jogador",
    list(jogadores.keys())
)

registro_jogador = jogadores[
    jogador_nome
]

jogador_id = registro_jogador[
    "jogador_id"
]

st.metric(
    "Saldo Atual",
    f"R$ {registro_jogador['saldo']:,.2f}"
)

st.divider()

# ==========================
# PROPRIEDADES DO JOGADOR
# ==========================

props = (
    supabase.table(
        "propriedades_jogadores"
    )
    .select("*")
    .eq("jogador_id", jogador_id)
    .eq("partida_id", partida_id)
    .execute()
)

ativas = []
hipotecadas = []

for p in props.data:

    propriedade = (
        supabase.table("propriedades")
        .select("*")
        .eq(
            "id",
            p["propriedade_id"]
        )
        .execute()
    )

    if not propriedade.data:
        continue

    nome = propriedade.data[0]["nome"]

    registro = {
        "dados": p,
        "propriedade": propriedade.data[0]
    }

    if p["hipotecada"]:
        hipotecadas.append(
            (nome, registro)
        )
    else:
        ativas.append(
            (nome, registro)
        )

# ==========================
# HIPOTECAR
# ==========================

st.subheader("💰 Hipotecar")

if ativas:

    opcoes_ativas = {
        nome: dados
        for nome, dados in ativas
    }

    prop_ativa = st.selectbox(
        "Propriedade para hipotecar",
        list(opcoes_ativas.keys()),
        key="hipotecar_prop"
    )

    if st.button("Hipotecar"):

        registro = opcoes_ativas[
            prop_ativa
        ]

        valor_hipoteca = registro[
            "propriedade"
        ]["valor_hipoteca"]

        novo_saldo = (
            registro_jogador["saldo"]
            + valor_hipoteca
        )

        # Atualiza saldo jogador
        supabase.table(
            "partida_jogadores"
        ).update({

            "saldo": novo_saldo

        }).eq(

            "id",
            registro_jogador["id"]

        ).execute()

        # Atualiza propriedade
        supabase.table(
            "propriedades_jogadores"
        ).update({

            "hipotecada": True

        }).eq(

            "id",
            registro["dados"]["id"]

        ).execute()

        # Transação
        supabase.table(
            "transacoes"
        ).insert({

            "partida_id": partida_id,
            "jogador_id": jogador_id,
            "tipo": "HIPOTECA",
            "origem": "BANCO",
            "destino": jogador_nome,
            "valor": valor_hipoteca,
            "descricao":
            f"Hipoteca da propriedade {prop_ativa}"

        }).execute()

        st.success(
            f"Hipoteca realizada! +R$ {valor_hipoteca:,.2f}"
        )

        st.rerun()

else:

    st.info(
        "Nenhuma propriedade disponível para hipotecar."
    )

st.divider()

# ==========================
# RESGATAR HIPOTECA
# ==========================

st.subheader("🏦 Resgatar Hipoteca")

if hipotecadas:

    opcoes_hipotecadas = {
        nome: dados
        for nome, dados in hipotecadas
    }

    prop_hipotecada = st.selectbox(
        "Propriedade hipotecada",
        list(opcoes_hipotecadas.keys()),
        key="resgatar_prop"
    )

    registro = opcoes_hipotecadas[
        prop_hipotecada
    ]

    valor_hipoteca = registro[
        "propriedade"
    ]["valor_hipoteca"]

    valor_resgate = round(
        valor_hipoteca * 1.10,
        2
    )

    st.info(
        f"Valor para resgate: R$ {valor_resgate:,.2f}"
    )

    if st.button("Resgatar Hipoteca"):

        saldo_atual = (
            registro_jogador["saldo"]
        )

        if saldo_atual < valor_resgate:

            st.error(
                "Saldo insuficiente para resgatar."
            )

        else:

            novo_saldo = (
                saldo_atual
                - valor_resgate
            )

            # Atualiza saldo
            supabase.table(
                "partida_jogadores"
            ).update({

                "saldo": novo_saldo

            }).eq(

                "id",
                registro_jogador["id"]

            ).execute()

            # Atualiza propriedade
            supabase.table(
                "propriedades_jogadores"
            ).update({

                "hipotecada": False

            }).eq(

                "id",
                registro["dados"]["id"]

            ).execute()

            # Transação
            supabase.table(
                "transacoes"
            ).insert({

                "partida_id": partida_id,
                "jogador_id": jogador_id,
                "tipo": "RESGATE_HIPOTECA",
                "origem": jogador_nome,
                "destino": "BANCO",
                "valor": valor_resgate,
                "descricao":
                f"Resgate da hipoteca de {prop_hipotecada}"

            }).execute()

            st.success(
                "Hipoteca resgatada!"
            )

            st.rerun()

else:

    st.info(
        "Nenhuma propriedade hipotecada."
    )

st.divider()

# ==========================
# RESUMO
# ==========================

st.subheader("📋 Resumo")

total_hipotecas = 0

for nome, registro in ativas:

    total_hipotecas += registro[
        "propriedade"
    ]["valor_hipoteca"]

st.metric(
    "Valor disponível em novas hipotecas",
    f"R$ {total_hipotecas:,.2f}"
)

st.metric(
    "Propriedades hipotecadas",
    len(hipotecadas)
)