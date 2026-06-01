import itertools
import math
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

# Configuração da página Web
st.set_page_config(
    page_title="Preditor Quantitativo Pro", page_icon="📊", layout="wide"
)

# Constantes de Calibração Estatística
MEDIA_GOLS_SÉRIE_A = 1.28
MEDIA_GOLS_FIFA = 1.35
FATOR_CASA_ATAQUE = 1.15  # Mandante herda +15% de força ofensiva
FATOR_CASA_DEFESA = 0.85  # Mandante reduz em 15% os gols sofridos (defesa melhor)

# ==============================================================================
# BANCO DE DADOS ATUALIZADO COM FATOR DE MOMENTO (FORMA RECENTE)
# "forma": 1.0 é a média normal. Acima de 1.0 é fase excelente, abaixo é crise.
# ==============================================================================
DADOS_BRASILEIRAO = {
    "Palmeiras": {
        "ataque": 1.9,
        "defesa": 0.8,
        "forma": 1.15,
        "escanteios": 6.2,
        "cartoes": 2.1,
    },
    "Flamengo": {
        "ataque": 2.1,
        "defesa": 0.9,
        "forma": 1.10,
        "escanteios": 5.9,
        "cartoes": 2.4,
    },
    "Botafogo": {
        "ataque": 2.0,
        "defesa": 0.9,
        "forma": 1.20,
        "escanteios": 5.8,
        "cartoes": 2.2,
    },
    "Atlético-MG": {
        "ataque": 1.7,
        "defesa": 1.1,
        "forma": 0.95,
        "escanteios": 5.4,
        "cartoes": 2.7,
    },
    "São Paulo": {
        "ataque": 1.6,
        "defesa": 0.9,
        "forma": 1.00,
        "escanteios": 5.2,
        "cartoes": 2.5,
    },
    "Internacional": {
        "ataque": 1.5,
        "defesa": 0.8,
        "forma": 1.05,
        "escanteios": 5.3,
        "cartoes": 2.4,
    },
    "Fluminense": {
        "ataque": 1.3,
        "defesa": 1.2,
        "forma": 0.85,
        "escanteios": 4.6,
        "cartoes": 2.6,
    },
    "Corinthians": {
        "ataque": 1.4,
        "defesa": 1.1,
        "forma": 0.90,
        "escanteios": 5.1,
        "cartoes": 2.5,
    },
    "Santos": {
        "ataque": 1.3,
        "defesa": 1.1,
        "forma": 1.00,
        "escanteios": 4.9,
        "cartoes": 2.3,
    },
    "Cruzeiro": {
        "ataque": 1.4,
        "defesa": 1.0,
        "forma": 1.02,
        "escanteios": 5.0,
        "cartoes": 2.4,
    },
    "Vasco": {
        "ataque": 1.3,
        "defesa": 1.3,
        "forma": 0.95,
        "escanteios": 4.8,
        "cartoes": 2.7,
    },
    "Bahia": {
        "ataque": 1.6,
        "defesa": 1.2,
        "forma": 1.05,
        "escanteios": 5.3,
        "cartoes": 2.1,
    },
    "Athletico-PR": {
        "ataque": 1.5,
        "defesa": 1.1,
        "forma": 0.98,
        "escanteios": 5.5,
        "cartoes": 2.5,
    },
    "Fortaleza": {
        "ataque": 1.6,
        "defesa": 1.0,
        "forma": 1.08,
        "escanteios": 5.4,
        "cartoes": 2.3,
    },
    "Bragantino": {
        "ataque": 1.4,
        "defesa": 1.3,
        "forma": 0.92,
        "escanteios": 5.4,
        "cartoes": 2.6,
    },
    "Cuiabá": {
        "ataque": 1.0,
        "defesa": 1.3,
        "forma": 0.88,
        "escanteios": 4.1,
        "cartoes": 2.7,
    },
    "Vitória": {
        "ataque": 1.1,
        "defesa": 1.4,
        "forma": 0.94,
        "escanteios": 4.4,
        "cartoes": 2.8,
    },
    "Juventude": {
        "ataque": 1.1,
        "defesa": 1.3,
        "forma": 0.96,
        "escanteios": 4.3,
        "cartoes": 2.9,
    },
    "Criciúma": {
        "ataque": 1.2,
        "defesa": 1.5,
        "forma": 0.90,
        "escanteios": 4.3,
        "cartoes": 2.5,
    },
}

# (DADOS_COPA mantido e simplificado para focar na nova estrutura de análise)
DADOS_COPA = {
    "Brasil": {"ataque": 2.5, "defesa": 0.6, "forma": 0.90, "escanteios": 6.8, "cartoes": 1.6},  # Baixei a forma recente do Brasil para corrigir o viés histórico
    "Marrocos": {"ataque": 1.9, "defesa": 0.8, "forma": 1.10, "escanteios": 5.6, "cartoes": 2.1},
    "França": {"ataque": 2.4, "defesa": 0.7, "forma": 1.15, "escanteios": 6.5, "cartoes": 1.5},
    "Argentina": {"ataque": 2.3, "defesa": 0.7, "forma": 1.12, "escanteios": 6.2, "cartoes": 1.9},
    "Panamá": {"ataque": 1.1, "defesa": 1.6, "forma": 0.95, "escanteios": 4.0, "cartoes": 2.0},
    "Haiti": {"ataque": 0.8, "defesa": 2.4, "forma": 0.85, "escanteios": 3.5, "cartoes": 2.4},
    "Alemanha": {"ataque": 2.2, "defesa": 0.9, "forma": 1.05, "escanteios": 6.3, "cartoes": 1.8},
    "Inglaterra": {"ataque": 2.3, "defesa": 0.8, "forma": 1.08, "escanteios": 6.4, "cartoes": 1.4},
}


# ==============================================================================
# MOTOR MATEMÁTICO QUANTITATIVO AVANÇADO
# ==============================================================================
def calcular_poisson(lambda_gols, k):
    if lambda_gols <= 0:
        return 0.0
    return (math.exp(-lambda_gols) * (lambda_gols**k)) / math.factorial(k)


def realizar_analise_completa(m_time, v_time, banco_dados, media_gols_base, eh_copa=False):
    t_m = banco_dados[m_time]
    t_v = banco_dados[v_time]

    # 1. Ajuste de Gols Esperados usando Mando de Campo e Forma Recente
    if not eh_copa:
        # No Brasileirão, o mando de campo é muito forte
        lambda_m = (t_m["ataque"] * FATOR_CASA_ATAQUE) * (t_v["defesa"] / media_gols_base) * t_m["forma"]
        lambda_v = (t_v["ataque"] * (t_m["defesa"] * FATOR_CASA_DEFESA) / media_gols_base) * t_v["forma"]
    else:
        # Na Copa (campo neutro geralmente), removemos o fator casa, usamos apenas a Forma Recente
        lambda_m = t_m["ataque"] * (t_v["defesa"] / media_gols_base) * t_m["forma"]
        lambda_v = t_v["ataque"] * (t_m["defesa"] / media_gols_base) * t_v["forma"]

    # Matriz bidimensional de probabilidades de placar (0 a 6 gols)
    max_gols = 6
    matriz_gols = pd.DataFrame(0.0, index=range(max_gols), columns=range(max_gols))

    prob_m, prob_v, prob_empate = 0.0, 0.0, 0.0

    for g_m, g_v in itertools.product(range(max_gols), range(max_gols)):
        p_m = calcular_poisson(lambda_m, g_m)
        p_v = calcular_poisson(lambda_v, g_v)
        p_combinada = p_m * p_v
        matriz_gols.at[g_m, g_v] = p_combinada

        if g_m > g_v:
            prob_m += p_combinada
        elif g_v > g_m:
            prob_v += p_combinada
        else:
            prob_empate += p_combinada

    # Encontrar o placar de maior probabilidade isolada (Moda)
    placar_index = matriz_gols.stack().idxmax()
    prob_placar_moda = matriz_gols.at[placar_index[0], placar_index[1]]

    # Conversão Probabilidade -> Odds Precificadas (Formato Decimal)
    odd_m = round(1 / prob_m, 2) if prob_m > 0 else 99.0
    odd_empate = round(1 / prob_empate, 2) if prob_empate > 0 else 99.0
    odd_v = round(1 / prob_v, 2) if prob_v > 0 else 99.0

    # Projeção de Scouts baseados no Ritmo de jogo projetado
    fator_ritmo = (lambda_m + lambda_v) / (t_m["ataque"] + t_v["ataque"])
    escanteios_proj = (t_m["escanteios"] + t_v.get("escanteios", 5.0)) * fator_ritmo
    cartoes_proj = t_m["cartoes"] + t_v["cartoes"]

    return {
        "prob_m": prob_m, "prob_empate": prob_empate, "prob_v": prob_v,
        "odd_m": odd_m, "odd_empate": odd_empate, "odd_v": odd_v,
        "placar_moda": f"{placar_index[0]} x {placar_index[1]}",
        "prob_placar": prob_placar_moda,
        "matriz": matriz_gols,
        "escanteios": round(escanteios_proj, 1),
        "cartoes": round(cartoes_proj, 1),
        "gols_esperados_m": round(lambda_m, 2),
        "gols_esperados_v": round(lambda_v, 2)
    }

# ==============================================================================
# INTERFACE GRÁFICA INTERATIVA
# ==============================================================================
st.title("📊 Plataforma de Inteligência Preditiva & Fair Odds")
st.markdown("Análise quantitativa baseada em Cadeias de Poisson, Ajuste de Mando e Forma Recente.")

tab_br, tab_copa = st.tabs(["🇧🇷 Campeonato Brasileiro (Série A)", "🌍 Copa do Mundo"])

# --- LÓGICA DA ABA BRASILEIRÃO ---
with tab_br:
    col1, col2 = st.columns(2)
    with col1:
        time_m = st.selectbox("Mandante (Casa)", sorted(list(DADOS_BRASILEIRAO.keys())), index=0)
    with col2:
        time_v = st.selectbox("Visitante (Fora)", sorted(list(DADOS_BRASILEIRAO.keys())), index=1)

    if time_m == time_v:
        st.warning("Selecione equipes diferentes.")
    else:
        res = realizar_analise_completa(time_m, time_v, DADOS_BRASILEIRAO, MEDIA_GOLS_SÉRIE_A, eh_copa=False)
        
        # Grid Principal de Resultados
        c_mod, c_xg1, c_xg2 = st.columns(3)
        c_mod.metric("Placar Mais Provável (Moda)", res["placar_moda"], f"{round(res['prob_placar']*100, 1)}% de chance")
        c_xg1.metric(f"Gols Esperados (xG) - {time_m}", res["gols_esperados_m"])
        c_xg2.metric(f"Gols Esperados (xG) - {time_v}", res["gols_esperados_v"])

        st.markdown("### 🎲 Precificação de Mercado (Fair Odds vs Probabilidades)")
        
        col_m, col_e, col_v = st.columns(3)
        col_m.subheader(f"Vitória {time_m}")
        col_m.markdown(f"**Probabilidade:** {round(res['prob_m']*100, 1)}%")
        col_m.info(f"**Odd Justa:** @{res['odd_m']}")

        col_e.subheader("Empate")
        col_e.markdown(f"**Probabilidade:** {round(res['prob_empate']*100, 1)}%")
        col_e.info(f"**Odd Justa:** @{res['odd_empate']}")

        col_v.subheader(f"Vitória {time_v}")
        col_v.markdown(f"**Probabilidade:** {round(res['prob_v']*100, 1)}%")
        col_v.info(f"**Odd Justa:** @{res['odd_v']}")

        # Bloco Gráfico: Matriz de Calor de Gols Exatos
        st.markdown("### 🗺️ Matriz de Dispersão de Gols (Onde o jogo tende a terminar)")
        
        fig, ax = plt.subplots(figsize=(7, 4))
        sns.heatmap(res["matriz"], annot=True, fmt=".2%", cmap="YlGnBu", xticklabels=range(6), yticklabels=range(6), ax=ax)
        plt.xlabel(f"Gols do Visitante ({time_v})")
        plt.ylabel(f"Gols do Mandante ({time_m})")
        plt.title("Concentração Estatística de Placares")
        st.pyplot(fig)

        # Estatísticas adicionais de Linhas de Mercado
        st.markdown("### 📈 Projeção Estatística de Over/Under")
        st.table({
            "Mercado Alternativo": ["Linha de Escanteios Totais", "Linha de Cartões Amarelos Totais"],
            "Projeção do Modelo Quant": [res["escanteios"], res["cartoes"]]
        })

# --- LÓGICA DA ABA COPA ---
with tab_copa:
    col1, col2 = st.columns(2)
    with col1:
        selec_m = st.selectbox("Seleção Mandante", sorted(list(DADOS_COPA.keys())), index=0)
    with col2:
        selec_v = st.selectbox("Seleção Visitante", sorted(list(DADOS_COPA.keys())), index=4)

    if selec_m == selec_v:
        st.warning("Selecione seleções diferentes.")
    else:
        res_c = realizar_analise_completa(selec_m, selec_v, DADOS_COPA, MEDIA_GOLS_FIFA, eh_copa=True)
        
        cm_mod, cm_xg1, cm_xg2 = st.columns(3)
        cm_mod.metric("Placar Mais Provável (Moda)", res_c["placar_moda"], f"{round(res_c['prob_placar']*100, 1)}% de chance")
        cm_xg1.metric(f"xG Projetado - {selec_m}", res_c["gols_esperados_m"])
        cm_xg2.metric(f"xG Projetado - {selec_v}", res_c["gols_esperados_v"])

        st.markdown("### 🎲 Precificação de Mercado - Copa do Mundo")
        colm_m, colm_e, colm_v = st.columns(3)
        colm_m.metric(f"Vitória {selec_m}", f"{round(res_c['prob_m']*100, 1)}%", f"Odd: @{res_c['odd_m']}")
        colm_e.metric("Empate", f"{round(res_c['prob_empate']*100, 1)}%", f"Odd: @{res_c['odd_empate']}")
        colm_v.metric(f"Vitória {selec_v}", f"{round(res_c['prob_v']*100, 1)}%", f"Odd: @{res_c['odd_v']}")

        fig_c, ax_c = plt.subplots(figsize=(7, 4))
        sns.heatmap(res_c["matriz"], annot=True, fmt=".2%", cmap="Oranges", xticklabels=range(6), yticklabels=range(6), ax=ax_c)
        plt.xlabel(f"Gols de {selec_v}")
        plt.ylabel(f"Gols de {selec_m}")
        st.pyplot(fig_c)
