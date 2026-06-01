import itertools
import math
import streamlit as st

# Configuração da página Web do seu App
st.set_page_config(
    page_title="Dashboard Preditivo - Futebol 2026",
    page_icon="⚽",
    layout="centered",
)

# Constantes baseadas nas médias históricas de gols por partida
MEDIA_GOLS_BRASILEIRAO = 1.25  # Média de gols por time em um jogo do Brasileirão
MEDIA_GOLS_FIFA = 1.35  # Média de gols por time em um jogo de Copa

# ==============================================================================
# 1. BANCO DE DADOS: 20 TIMES DO BRASILEIRÃO & 48 SELEÇÕES DA COPA
# ==============================================================================
DADOS_BRASILEIRAO = {
    "Palmeiras": {
        "ataque": 2.1,
        "defesa": 0.8,
        "escanteios": 6.4,
        "chutes": 5.8,
        "cartoes": 2.1,
    },
    "Flamengo": {
        "ataque": 2.3,
        "defesa": 0.9,
        "escanteios": 5.9,
        "chutes": 6.2,
        "cartoes": 2.4,
    },
    "Atlético-MG": {
        "ataque": 1.8,
        "defesa": 1.0,
        "escanteios": 5.5,
        "chutes": 4.9,
        "cartoes": 2.8,
    },
    "São Paulo": {
        "ataque": 1.7,
        "defesa": 0.9,
        "escanteios": 5.2,
        "chutes": 4.5,
        "cartoes": 2.6,
    },
    "Botafogo": {
        "ataque": 2.0,
        "defesa": 1.0,
        "escanteios": 5.8,
        "chutes": 5.5,
        "cartoes": 2.3,
    },
    "Grêmio": {
        "ataque": 1.6,
        "defesa": 1.2,
        "escanteios": 5.0,
        "chutes": 4.6,
        "cartoes": 2.7,
    },
    "Fluminense": {
        "ataque": 1.5,
        "defesa": 1.1,
        "escanteios": 4.8,
        "chutes": 4.3,
        "cartoes": 2.5,
    },
    "Athletico-PR": {
        "ataque": 1.6,
        "defesa": 1.0,
        "escanteios": 5.6,
        "chutes": 4.8,
        "cartoes": 2.4,
    },
    "Internacional": {
        "ataque": 1.7,
        "defesa": 0.9,
        "escanteios": 5.3,
        "chutes": 4.7,
        "cartoes": 2.6,
    },
    "Fortaleza": {
        "ataque": 1.5,
        "defesa": 1.1,
        "escanteios": 5.1,
        "chutes": 4.4,
        "cartoes": 2.2,
    },
    "Corinthians": {
        "ataque": 1.4,
        "defesa": 1.2,
        "escanteios": 5.0,
        "chutes": 4.2,
        "cartoes": 2.5,
    },
    "Cruzeiro": {
        "ataque": 1.3,
        "defesa": 1.1,
        "escanteios": 4.9,
        "chutes": 4.1,
        "cartoes": 2.4,
    },
    "Vasco": {
        "ataque": 1.4,
        "defesa": 1.4,
        "escanteios": 4.8,
        "chutes": 4.3,
        "cartoes": 2.8,
    },
    "Bahia": {
        "ataque": 1.5,
        "defesa": 1.3,
        "escanteios": 5.2,
        "chutes": 4.6,
        "cartoes": 2.1,
    },
    "Santos": {
        "ataque": 1.4,
        "defesa": 1.1,
        "escanteios": 5.0,
        "chutes": 4.4,
        "cartoes": 2.3,
    },
    "Bragantino": {
        "ataque": 1.5,
        "defesa": 1.2,
        "escanteios": 5.5,
        "chutes": 4.9,
        "cartoes": 2.5,
    },
    "Cuiabá": {
        "ataque": 1.1,
        "defesa": 1.2,
        "escanteios": 4.2,
        "chutes": 3.7,
        "cartoes": 2.6,
    },
    "Vitória": {
        "ataque": 1.2,
        "defesa": 1.5,
        "escanteios": 4.5,
        "chutes": 3.9,
        "cartoes": 2.7,
    },
    "Juventude": {
        "ataque": 1.1,
        "defesa": 1.4,
        "escanteios": 4.3,
        "chutes": 3.6,
        "cartoes": 2.9,
    },
    "Criciúma": {
        "ataque": 1.2,
        "defesa": 1.6,
        "escanteios": 4.4,
        "chutes": 3.8,
        "cartoes": 2.6,
    },
}

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
        "ataque": 2.6,
        "defesa": 0.6,
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
        "ataque": 0.8,
        "defesa": 2.4,
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
        "ataque": 0.7,
        "defesa": 2.5,
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
# 2. MOTOR ESTATÍSTICO DE POISSON (FORÇA RELATIVA MULTIPLICATIVA)
# ==============================================================================


def calcular_poisson(lambda_gols, k):
    return (math.exp(-lambda_gols) * (lambda_gols**k)) / math.factorial(k)


def renderizar_analise_confronto(time_a, time_b, dados_origem, media_gols_base):
    t_a = dados_origem[time_a]
    t_b = dados_origem[time_b]

    # Modelo Multiplicativo Avançado para forçar placares realistas e evitar o efeito 1x1 em disparidades
    lambda_a = t_a["ataque"] * (t_b["defesa"] / media_gols_base)
    lambda_b = t_b["ataque"] * (t_a["defesa"] / media_gols_base)

    prob_a, prob_b, prob_empate = 0, 0, 0
    maior_prob_placar = 0
    placar_mais_provavel = (0, 0)

    # Varredura matricial expandida de gols (0 a 7 gols por equipe)
    for g_a, g_b in itertools.product(range(8), range(8)):
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

    # Ajuste dinâmico do volume de Scouts (ritmo ofensivo da partida)
    fator_ritmo = (lambda_a + lambda_b) / (t_a["ataque"] + t_b["ataque"])
    escanteios_proj = (t_a["escanteios"] + t_b["escanteios"]) * fator_ritmo
    chutes_proj = (t_a["chutes"] + t_b["chutes"]) * fator_ritmo
    cartoes_proj = t_a["cartoes"] + t_b["cartoes"]

    # --- INTERFACE DE EXIBIÇÃO COM STREAMLIT ---
    st.markdown("### 🎯 Placar Mais Provável")
    st.success(f"### **{time_a} {placar_mais_provavel[0]} x {placar_mais_provavel[1]} {time_b}**")
    st.caption(
        f"A assertividade matemática deste placar exato é estimada em **{round(maior_prob_placar * 100, 1)}%**."
    )
    st.markdown("---")

    st.markdown("### 📊 Probabilidades Probabilísticas (1X2)")
    col_pct1, col_pct2, col_pct3 = st.columns(3)
    col_pct1.metric(f"Vitória {time_a}", f"{round(prob_a * 100, 1)}%")
    col_pct2.metric("Empate", f"{round(prob_empate * 100, 1)}%")
    col_pct3.metric(f"Vitória {time_b}", f"{round(prob_b * 100, 1)}%")

    st.progress(int(prob_a * 100))

    st.markdown("---")
    st.markdown("### 📈 Linhas Médias de Scouts Projetadas")
    tabela_scouts = {
        "Scout Técnico": [
            "Escanteios Totais",
            "Chutes a Gol Totais",
            "Cartões Amarelos Totais",
        ],
        "Linha Esperada": [
            round(escanteios_proj, 1),
            round(chutes_proj, 1),
            round(cartoes_proj, 1),
        ],
    }
    st.table(tabela_scouts)


# ==============================================================================
# 3. INTERFACE DE NAVEGAÇÃO PRINCIPAL (ABAS MULTI-COMPETIÇÃO)
# ==============================================================================
st.title("⚽ Centro Avançado de Estatísticas de Futebol")
st.markdown("Selecione a competição desejada na aba abaixo para iniciar os cruzamentos técnicos.")

# Criação das Abas Nativas do App
tab_brasileirao, tab_copa = st.tabs(
    ["🏆 Campeonato Brasileiro", "🌎 Copa do Mundo 2026"]
)

# --- CONFIGURAÇÃO DA ABA BRASILEIRÃO ---
with tab_brasileirao:
    st.header("Série A - Campeonato Brasileiro")
    lista_br = sorted(list(DADOS_BRASILEIRAO.keys()))

    col_br1, col_br2 = st.columns(2)
    with col_br1:
        br_mandante = st.selectbox(
            "Selecione o Mandante ",
            lista_br,
            index=lista_br.index("Palmeiras"),
        )
    with col_br2:
        br_visitante = st.selectbox(
            "Selecione o Visitante ",
            lista_br,
            index=lista_br.index("Flamengo"),
        )

    if br_mandante == br_visitante:
        st.error(
            "Selecione equipes distintas para obter uma análise de confronto válida."
        )
    else:
        renderizar_analise_confronto(
            br_mandante, br_visitante, DADOS_BRASILEIRAO, MEDIA_GOLS_BRASILEIRAO
        )

# --- CONFIGURAÇÃO DA ABA COPA ---
with tab_copa:
    st.header("Copa do Mundo FIFA 2026")
    lista_copa = sorted(list(DADOS_COPA.keys()))

    col_cp1, col_cp2 = st.columns(2)
    with col_cp1:
        cp_mandante = st.selectbox(
            "Selecione a Seleção A",
            lista_copa,
            index=lista_copa.index("Brasil"),
        )
    with col_cp2:
        cp_visitante = st.selectbox(
            "Selecione a Seleção B",
            lista_copa,
            index=lista_copa.index("Haiti"),
        )

    if cp_mandante == cp_visitante:
        st.error(
            "Selecione seleções distintas para obter uma análise de confronto válida."
        )
    else:
        renderizar_analise_confronto(
            cp_mandante, cp_visitante, DADOS_COPA, MEDIA_GOLS_FIFA
        )
