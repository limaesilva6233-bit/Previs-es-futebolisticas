import itertools
import math
import streamlit as st

# Configuração da página Web
st.set_page_config(
    page_title="Preditor Copa 2026", page_icon="⚽", layout="centered"
)

# ==============================================================================
# DATA - AS 48 SELEÇÕES DA COPA 2026
# ==============================================================================
DADOS_COPA = {
    # GRUPO A
    "México": {
        "grupo": "A",
        "ataque": 1.8,
        "defesa": 1.1,
        "escanteios": 5.4,
        "chutes": 5.2,
        "cartoes": 2.1,
    },
    "África do Sul": {
        "grupo": "A",
        "ataque": 1.2,
        "defesa": 1.3,
        "escanteios": 4.6,
        "chutes": 3.9,
        "cartoes": 1.9,
    },
    "Coreia do Sul": {
        "grupo": "A",
        "ataque": 1.6,
        "defesa": 1.0,
        "escanteios": 5.1,
        "chutes": 4.8,
        "cartoes": 1.5,
    },
    "Chéquia": {
        "grupo": "A",
        "ataque": 1.5,
        "defesa": 1.2,
        "escanteios": 4.9,
        "chutes": 4.5,
        "cartoes": 2.3,
    },
    # GRUPO B
    "Canadá": {
        "grupo": "B",
        "ataque": 1.5,
        "defesa": 1.2,
        "escanteios": 5.2,
        "chutes": 4.6,
        "cartoes": 1.8,
    },
    "Bósnia e Herzegovina": {
        "grupo": "B",
        "ataque": 1.3,
        "defesa": 1.4,
        "escanteios": 4.7,
        "chutes": 4.1,
        "cartoes": 2.5,
    },
    "Catar": {
        "grupo": "B",
        "ataque": 1.1,
        "defesa": 1.6,
        "escanteios": 4.1,
        "chutes": 3.7,
        "cartoes": 2.0,
    },
    "Suíça": {
        "grupo": "B",
        "ataque": 1.6,
        "defesa": 1.0,
        "escanteios": 5.5,
        "chutes": 5.0,
        "cartoes": 1.7,
    },
    # GRUPO C
    "Brasil": {
        "grupo": "C",
        "ataque": 2.4,
        "defesa": 0.7,
        "escanteios": 6.8,
        "chutes": 6.5,
        "cartoes": 1.6,
    },
    "Marrocos": {
        "grupo": "C",
        "ataque": 1.9,
        "defesa": 0.8,
        "escanteios": 5.6,
        "chutes": 5.3,
        "cartoes": 2.1,
    },
    "Haiti": {
        "grupo": "C",
        "ataque": 0.9,
        "defesa": 2.1,
        "escanteios": 3.5,
        "chutes": 3.1,
        "cartoes": 2.4,
    },
    "Escócia": {
        "grupo": "C",
        "ataque": 1.3,
        "defesa": 1.4,
        "escanteios": 4.8,
        "chutes": 4.2,
        "cartoes": 2.2,
    },
    # GRUPO D
    "Estados Unidos": {
        "grupo": "D",
        "ataque": 1.9,
        "defesa": 1.0,
        "escanteios": 5.8,
        "chutes": 5.4,
        "cartoes": 1.9,
    },
    "Paraguai": {
        "grupo": "D",
        "ataque": 1.1,
        "defesa": 0.9,
        "escanteios": 4.5,
        "chutes": 3.8,
        "cartoes": 2.8,
    },
    "Austrália": {
        "grupo": "D",
        "ataque": 1.4,
        "defesa": 1.2,
        "escanteios": 5.0,
        "chutes": 4.3,
        "cartoes": 1.8,
    },
    "Turquia": {
        "grupo": "D",
        "ataque": 1.7,
        "defesa": 1.3,
        "escanteios": 5.3,
        "chutes": 4.9,
        "cartoes": 2.6,
    },
    # GRUPO E
    "Alemanha": {
        "grupo": "E",
        "ataque": 2.3,
        "defesa": 0.9,
        "escanteios": 6.5,
        "chutes": 6.2,
        "cartoes": 1.8,
    },
    "Curaçao": {
        "grupo": "E",
        "ataque": 0.8,
        "defesa": 2.3,
        "escanteios": 3.4,
        "chutes": 3.0,
        "cartoes": 2.3,
    },
    "Costa do Marfim": {
        "grupo": "E",
        "ataque": 1.6,
        "defesa": 1.1,
        "escanteios": 5.2,
        "chutes": 4.7,
        "cartoes": 2.2,
    },
    "Equador": {
        "grupo": "E",
        "ataque": 1.5,
        "defesa": 1.0,
        "escanteios": 5.1,
        "chutes": 4.6,
        "cartoes": 2.4,
    },
    # GRUPO F
    "Holanda": {
        "grupo": "F",
        "ataque": 2.1,
        "defesa": 0.9,
        "escanteios": 6.1,
        "chutes": 5.7,
        "cartoes": 1.7,
    },
    "Japão": {
        "grupo": "F",
        "ataque": 1.8,
        "defesa": 1.0,
        "escanteios": 5.5,
        "chutes": 5.2,
        "cartoes": 1.3,
    },
    "Suécia": {
        "grupo": "F",
        "ataque": 1.6,
        "defesa": 1.1,
        "escanteios": 5.4,
        "chutes": 4.8,
        "cartoes": 2.0,
    },
    "Tunísia": {
        "grupo": "F",
        "ataque": 1.1,
        "defesa": 1.3,
        "escanteios": 4.2,
        "chutes": 3.6,
        "cartoes": 2.2,
    },
    # GRUPO G
    "Bélgica": {
        "grupo": "G",
        "ataque": 2.0,
        "defesa": 1.0,
        "escanteios": 5.9,
        "chutes": 5.5,
        "cartoes": 1.6,
    },
    "Egito": {
        "grupo": "G",
        "ataque": 1.4,
        "defesa": 1.1,
        "escanteios": 4.6,
        "chutes": 4.2,
        "cartoes": 2.1,
    },
    "Irã": {
        "grupo": "G",
        "ataque": 1.3,
        "defesa": 1.2,
        "escanteios": 4.4,
        "chutes": 4.0,
        "cartoes": 2.3,
    },
    "Nova Zelândia": {
        "grupo": "G",
        "ataque": 1.0,
        "defesa": 1.7,
        "escanteios": 3.9,
        "chutes": 3.4,
        "cartoes": 1.7,
    },
    # GRUPO H
    "Espanha": {
        "grupo": "H",
        "ataque": 2.3,
        "defesa": 0.8,
        "escanteios": 6.7,
        "chutes": 6.3,
        "cartoes": 1.5,
    },
    "Cabo Verde": {
        "grupo": "H",
        "ataque": 1.1,
        "defesa": 1.5,
        "escanteios": 4.0,
        "chutes": 3.5,
        "cartoes": 2.1,
    },
    "Arábia Saudita": {
        "grupo": "H",
        "ataque": 1.2,
        "defesa": 1.4,
        "escanteios": 4.3,
        "chutes": 3.8,
        "cartoes": 2.4,
    },
    "Uruguai": {
        "grupo": "H",
        "ataque": 1.9,
        "defesa": 0.9,
        "escanteios": 5.6,
        "chutes": 5.2,
        "cartoes": 2.6,
    },
    # GRUPO I
    "França": {
        "grupo": "I",
        "ataque": 2.5,
        "defesa": 0.8,
        "escanteios": 6.4,
        "chutes": 6.6,
        "cartoes": 1.6,
    },
    "Iraque": {
        "grupo": "I",
        "ataque": 1.2,
        "defesa": 1.5,
        "escanteios": 4.2,
        "chutes": 3.7,
        "cartoes": 2.2,
    },
    "Noruega": {
        "grupo": "I",
        "ataque": 1.8,
        "defesa": 1.2,
        "escanteios": 5.3,
        "chutes": 5.0,
        "cartoes": 1.9,
    },
    "Senegal": {
        "grupo": "I",
        "ataque": 1.6,
        "defesa": 1.0,
        "escanteios": 5.0,
        "chutes": 4.6,
        "cartoes": 2.1,
    },
    # GRUPO J
    "Argentina": {
        "grupo": "J",
        "ataque": 2.4,
        "defesa": 0.7,
        "escanteios": 6.2,
        "chutes": 6.4,
        "cartoes": 2.0,
    },
    "Argélia": {
        "grupo": "J",
        "ataque": 1.5,
        "defesa": 1.2,
        "escanteios": 4.9,
        "chutes": 4.4,
        "cartoes": 2.3,
    },
    "Áustria": {
        "grupo": "J",
        "ataque": 1.6,
        "defesa": 1.1,
        "escanteios": 5.4,
        "chutes": 4.9,
        "cartoes": 2.1,
    },
    "Jordânia": {
        "grupo": "J",
        "ataque": 1.0,
        "defesa": 1.6,
        "escanteios": 3.8,
        "chutes": 3.5,
        "cartoes": 2.2,
    },
    # GRUPO K
    "Portugal": {
        "grupo": "K",
        "ataque": 2.4,
        "defesa": 0.8,
        "escanteios": 6.3,
        "chutes": 6.1,
        "cartoes": 1.9,
    },
    "RD do Congo": {
        "grupo": "K",
        "ataque": 1.3,
        "defesa": 1.3,
        "escanteios": 4.5,
        "chutes": 4.0,
        "cartoes": 2.4,
    },
    "Uzbequistão": {
        "grupo": "K",
        "ataque": 1.2,
        "defesa": 1.2,
        "escanteios": 4.4,
        "chutes": 4.2,
        "cartoes": 1.8,
    },
    "Colômbia": {
        "grupo": "K",
        "ataque": 1.8,
        "defesa": 0.9,
        "escanteios": 5.4,
        "chutes": 5.0,
        "cartoes": 2.7,
    },
    # GRUPO L
    "Inglaterra": {
        "grupo": "L",
        "ataque": 2.3,
        "defesa": 0.8,
        "escanteios": 6.6,
        "chutes": 6.0,
        "cartoes": 1.4,
    },
    "Croácia": {
        "grupo": "L",
        "ataque": 1.6,
        "defesa": 1.0,
        "escanteios": 5.2,
        "chutes": 4.7,
        "cartoes": 1.8,
    },
    "Gana": {
        "grupo": "L",
        "ataque": 1.4,
        "defesa": 1.4,
        "escanteios": 4.7,
        "chutes": 4.1,
        "cartoes": 2.3,
    },
    "Panamá": {
        "grupo": "L",
        "ataque": 1.1,
        "defesa": 1.6,
        "escanteios": 4.0,
        "chutes": 3.6,
        "cartoes": 2.0,
    },
}

# ==============================================================================
# MOTOR MATEMÁTICO (POISSON)
# ==============================================================================


def calcular_poisson(lambda_gols, k):
    return (math.exp(-lambda_gols) * (lambda_gols**k)) / math.factorial(k)


def processar_confronto(time_a, time_b):
    t_a = DADOS_COPA[time_a]
    t_b = DADOS_COPA[time_b]

    lambda_a = (t_a["ataque"] + t_b["defesa"]) / 2
    lambda_b = (t_b["ataque"] + t_a["defesa"]) / 2

    prob_a, prob_b, prob_empate = 0, 0, 0
    maior_prob_placar = 0
    placar_mais_provavel = (0, 0)

    for g_a, g_b in itertools.product(range(7), range(7)):
        p_a = calcular_poisson(lambda_a, g_a)
        p_b = calcular_poisson(lambda_b, g_b)
        p_combinada = p_a * p_b

        if g_a > g_b:
            prob_a += p_combinada
        elif g_b > g_a:
            prob_b += p_combinada
        else:
            prob_empate += p_combinada

        if p_combinada > maior_prob_placar:
            maior_prob_placar = p_combinada
            placar_mais_provavel = (g_a, g_b)

    return {
        "vitoria_a": prob_a,
        "empate": prob_empate,
        "vitoria_b": prob_b,
        "placar": f"{placar_mais_provavel[0]} x {placar_mais_provavel[1]}",
        "confianca_placar": round(maior_prob_placar * 100, 1),
        "escanteios": round(t_a["escanteios"] + t_b["escanteios"], 1),
        "chutes": round(t_a["chutes"] + t_b["chutes"], 1),
        "cartoes": round(t_a["cartoes"] + t_b["cartoes"], 1),
    }


# ==============================================================================
# FRONT-END STREAMLIT
# ==============================================================================
st.title("🏆 Motor de Análise Preditiva - Copa 2026")
st.markdown("---")

lista_selecoes = sorted(list(DADOS_COPA.keys()))

# Interface de Seleção dos Times
col1, col2 = st.columns(2)
with col1:
    selecao_a = st.selectbox(
        "Seleção A (Mandante)", lista_selecoes, index=lista_selecoes.index("Brasil")
    )
with col2:
    selecao_b = st.selectbox(
        "Seleção B (Visitante)",
        lista_selecoes,
        index=lista_selecoes.index("Marrocos"),
    )

if selecao_a == selecao_b:
    st.error("Por favor, selecione duas equipes diferentes para o confronto.")
else:
    # Processa os dados matemáticas
    res = processar_confronto(selecao_a, selecao_b)

    # Box de Destaque para o Placar Mais Provável
    st.markdown("### 🎯 Placar Mais Provável")
    st.info(f"### **{selecao_a} {res['placar']} {selecao_b}**")
    st.caption(
        f"Este placar exato tem **{res['confianca_placar']}%** de chance matemática de acontecer."
    )

    st.markdown("---")

    # Barras de Probabilidade (Mercado 1X2)
    st.markdown("### 📊 Probabilidades de Vitória")

    st.write(f"**Vitória {selecao_a}:** {round(res['vitoria_a']*100, 1)}%")
    st.progress(int(res["vitoria_a"] * 100))

    st.write(f"**Empate:** {round(res['empate']*100, 1)}%")
    st.progress(int(res["empate"] * 100))

    st.write(f"**Vitória {selecao_b}:** {round(res['vitoria_b']*100, 1)}%")
    st.progress(int(res["vitoria_b"] * 100))

    st.markdown("---")

    # Tabela com as Projeções de Scouts (Over/Under)
    st.markdown("### 📈 Projeção Estatística de Scouts (Média Combinada)")

    dados_scouts = {
        "Scout Analisado": [
            "Escanteios Totais Esperados",
            "Chutes a Gol Totais Esperados",
            "Cartões Amarelos Esperados",
        ],
        "Linha Projetada": [res["escanteios"], res["chutes"], res["cartoes"]],
    }
    st.table(dados_scouts)
