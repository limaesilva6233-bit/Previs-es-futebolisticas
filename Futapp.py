import itertools
import math
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

# Configuração da página Web do Streamlit
st.set_page_config(
    page_title="Preditor Quantitativo Pro - Futebol",
    page_icon="📊",
    layout="wide",
)

# Constantes de Calibração Estatística Globais
MEDIA_GOLS_SÉRIE_A = 1.28
MEDIA_GOLS_FIFA = 1.35
FATOR_CASA_ATAQUE = 1.15  # Mandante herda +15% de força ofensiva no Brasileirão
FATOR_CASA_DEFESA = 0.85  # Mandante reduz em 15% os gols sofridos no Brasileirão

# ==============================================================================
# 1. BANCO DE DADOS: BRASILEIRÃO (MANDO E FORMA)
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

# ==============================================================================
# 2. BANCO DE DADOS: COPA 2026 COM PONDERAÇÃO (PESO 70% ELIMINATÓRIAS / ATUACÃO)
# dados estruturados com: "hist_ataque/defesa" (30%) e "elim_ataque/defesa" (70%)
# ==============================================================================
DADOS_COPA_PONDERADO = {
    "Brasil": {
        "hist_ataque": 2.5,
        "hist_defesa": 0.6,
        "elim_ataque": 1.6,
        "elim_defesa": 1.1,
        "atuacao_comentario": "Oscilante. Campanha irregular nas Eliminatórias refletiu problemas de transição defensiva e pouca criatividade contra blocos baixos.",
        "escanteios": 6.8,
        "cartoes": 1.6,
    },
    "Argentina": {
        "hist_ataque": 2.2,
        "hist_defesa": 0.7,
        "elim_ataque": 2.4,
        "elim_defesa": 0.5,
        "atuacao_comentario": "Excelente. Líder sólida das eliminatórias da CONMEBOL, com altíssima eficiência tática e solidez defensiva absurda.",
        "escanteios": 6.2,
        "cartoes": 1.9,
    },
    "França": {
        "hist_ataque": 2.4,
        "hist_defesa": 0.8,
        "elim_ataque": 2.6,
        "elim_defesa": 0.6,
        "atuacao_comentario": "Muito Forte. Classificação dominante na Europa. Transição ofensiva letal com poder de fogo devastador nos jogos recentes.",
        "escanteios": 6.5,
        "cartoes": 1.5,
    },
    "Marrocos": {
        "hist_ataque": 1.7,
        "hist_defesa": 0.9,
        "elim_ataque": 2.1,
        "elim_defesa": 0.7,
        "atuacao_comentario": "Em alta. Passou o trator nas eliminatórias africanas com um futebol muito mais agressivo e propositivo do que em 2022.",
        "escanteios": 5.6,
        "cartoes": 2.1,
    },
    "Inglaterra": {
        "hist_ataque": 2.2,
        "hist_defesa": 0.8,
        "elim_ataque": 2.3,
        "elim_defesa": 0.7,
        "atuacao_comentario": "Consistente. Sobrou no seu grupo europeu. Elenco jovem com volume ofensivo sufocante e ótima retenção de bola.",
        "escanteios": 6.4,
        "cartoes": 1.4,
    },
    "Alemanha": {
        "hist_ataque": 2.1,
        "hist_defesa": 1.0,
        "elim_ataque": 2.2,
        "elim_defesa": 0.9,
        "atuacao_comentario": "Recuperação. Mostrou evolução drástica sob comando tático recente, controlando jogos difíceis e melhorando a recomposição.",
        "escanteios": 6.3,
        "cartoes": 1.8,
    },
    "Panamá": {
        "hist_ataque": 1.1,
        "hist_defesa": 1.5,
        "elim_ataque": 1.4,
        "elim_defesa": 1.2,
        "atuacao_comentario": "Competitivo. Conquistou sua vaga de forma madura na CONCACAF, mostrando jogo coletivo arrumado e transição rápida pelas pontas.",
        "escanteios": 4.0,
        "cartoes": 2.0,
    },
    "Haiti": {
        "hist_ataque": 0.8,
        "hist_defesa": 2.2,
        "elim_ataque": 1.0,
        "elim_defesa": 1.9,
        "atuacao_comentario": "Zebra/Superação. Arrancou a vaga com aplicação tática totalmente defensiva. Sofre muita pressão em jogos grandes.",
        "escanteios": 3.5,
        "cartoes": 2.4,
    },
}


# ==============================================================================
# 3. MOTOR MATEMÁTICO QUANTITATIVO AVANÇADO
# ==============================================================================
def calcular_poisson(lambda_gols, k):
    if lambda_gols <= 0:
        return 0.0
    return (math.exp(-lambda_gols) * (lambda_gols**k)) / math.factorial(k)


def realizar_analise_completa(m_time, v_time, banco_dados, media_gols_base, eh_copa=False):
    t_m = banco_dados[m_time]
    t_v = banco_dados[v_time]

    # CÁLCULO DOS LAMBDAS (Gols Esperados)
    if not eh_copa:
        # Lógica do Brasileirão: Força Base Multiplicativa + Mando de Campo + Forma Recente
        lambda_m = (t_m["ataque"] * FATOR_CASA_ATAQUE) * (t_v["defesa"] / media_gols_base) * t_m["forma"]
        lambda_v = (t_v["ataque"] * (t_m["defesa"] * FATOR_CASA_DEFESA) / media_gols_base) * t_v["forma"]
        base_ataque_m, base_ataque_v = t_m["ataque"], t_v["ataque"]
        scout_cartoes = t_m["cartoes"] + t_v["cartoes"]
    else:
        # LÓGICA DA COPA: Ponderação Estatística Pura (30% Histórico Geral / 70% Eliminatórias e Atuação)
        ataque_ponderado_m = (t_m["hist_ataque"] * 0.3) + (t_m["elim_ataque"] * 0.7)
        defesa_ponderado_m = (t_m["hist_defesa"] * 0.3) + (t_m["elim_defesa"] * 0.7)

        ataque_ponderado_v = (t_v["hist_ataque"] * 0.3) + (t_v["elim_ataque"] * 0.7)
        defesa_ponderado_v = (t_v["hist_defesa"] * 0.3) + (t_v["elim_defesa"] * 0.7)

        # Na Copa (geralmente campo neutro), cruza-se as forças ponderadas calculadas
        lambda_m = ataque_ponderado_m * (defesa_ponderado_v / media_gols_base)
        lambda_v = ataque_ponderado_v * (defesa_ponderado_m / media_gols_base)
        base_ataque_m, base_ataque_v = ataque_ponderado_m, ataque_ponderado_v
        scout_cartoes = t_m["cartoes"] + t_v["cartoes"]

    # Criação da matriz bidimensional de probabilidades (0 a 6 gols)
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

    # Identificar o Placar com maior probabilidade isolada (A Moda da Distribuição)
    placar_index = matriz_gols.stack().idxmax()
    prob_placar_moda = matriz_gols.at[placar_index[0], placar_index[1]]

    # Conversão matemática de Probabilidade para Fair Odds Decimais
    odd_m = round(1 / prob_m, 2) if prob_m > 0 else 99.0
    odd_empate = round(1 / prob_empate, 2) if prob_empate > 0 else 99.0
    odd_v = round(1 / prob_v, 2) if prob_v > 0 else 99.0

    # Projeção de Scouts Dinâmicos baseados no Ritmo de jogo gerado pelos xG
    fator_ritmo = (lambda_m + lambda_v) / (base_ataque_m + base_ataque_v)
    escanteios_proj = (t_m["escanteios"] + t_v["escanteios"]) * fator_ritmo

    return {
        "prob_m": prob_m, "prob_empate": prob_empate, "prob_v": prob_v,
        "odd_m": odd_m, "odd_empate": odd_empate, "odd_v": odd_v,
        "placar_moda": f"{placar_index[0]} x {placar_index[1]}",
        "prob_placar": prob_placar_moda,
        "matriz": matriz_gols,
        "escanteios": round(escanteios_proj, 1),
        "cartoes": round(scout_cartoes, 1),
        "gols_esperados_m": round(lambda_m, 2),
        "gols_esperados_v": round(lambda_v, 2)
    }


# ==============================================================================
# 4. INTERFACE INTERATIVA (STREAMLIT DASHBOARD)
# ==============================================================================
st.title("📊 Plataforma de Inteligência Preditiva & Fair Odds")
st.markdown("Análise baseada em Cadeias de Poisson, Ajuste de Mando de Campo e Peso de 70% para Eliminatórias Recentes.")

tab_br, tab_copa = st.tabs(["🇧🇷 Campeonato Brasileiro (Série A)", "🌍 Copa do Mundo 2026"])

# --- LÓGICA DA ABA BRASILEIRÃO ---
with tab_br:
    col1, col2 = st.columns(2)
    with col1:
        time_m = st.selectbox("Mandante (Casa)", sorted(list(DADOS_BRASILEIRAO.keys())), index=0)
    with col2:
        time_v = st.selectbox("Visitante (Fora)", sorted(list(DADOS_BRASILEIRAO.keys())), index=1)

    if time_m == time_v:
        st.warning("Selecione equipes diferentes para o confronto.")
    else:
        res = realizar_analise_completa(time_m, time_v, DADOS_BRASILEIRAO, MEDIA_GOLS_SÉRIE_A, eh_copa=False)
        
        # Bloco de Métrica em Destaque
        c_mod, c_xg1, c_xg2 = st.columns(3)
        c_mod.metric("Placar Isolado Mais Provável", res["placar_moda"], f"{round(res['prob_placar']*100, 1)}% de chance")
        c_xg1.metric(f"Gols Esperados (xG) - {time_m}", res["gols_esperados_m"])
        c_xg2.metric(f"Gols Esperados (xG) - {time_v}", res["gols_esperados_v"])

        st.markdown("### 🎲 Precificação de Mercado (Odds Justas Estipuladas)")
        col_m, col_e, col_v = st.columns(3)
        col_m.metric(f"Vitória {time_m}", f"{round(res['prob_m']*100, 1)}%", f"Odd Justa: @{res['odd_m']}")
        col_e.metric("Empate", f"{round(res['prob_empate']*100, 1)}%", f"Odd Justa: @{res['odd_empate']}")
        col_v.metric(f"Vitória {time_v}", f"{round(res['prob_v']*100, 1)}%", f"Odd Justa: @{res['odd_v']}")

        # Renderização da Matriz de Calor
        st.markdown("### 🗺️ Matriz de Dispersão de Gols (Concentração de Probabilidade)")
        fig, ax = plt.subplots(figsize=(7, 3.5))
        sns.heatmap(res["matriz"], annot=True, fmt=".2%", cmap="YlGnBu", xticklabels=range(6), yticklabels=range(6), ax=ax)
        plt.xlabel(f"Gols do Visitante ({time_v})")
        plt.ylabel(f"Gols do Mandante ({time_m})")
        st.pyplot(fig)

        # Scouts Alternativos
        st.markdown("### 📈 Projeção Estatística de Over/Under")
        st.table({
            "Mercado de Estatísticas": ["Linha de Escanteios Totais", "Linha de Cartões Amarelos Totais"],
            "Projeção do Modelo Quant": [res["escanteios"], res["cartoes"]]
        })

# --- LÓGICA DA ABA COPA DO MUNDO (CAMPANHAS 70% PESADAS) ---
with tab_copa:
    col1, col2 = st.columns(2)
    with col1:
        selec_m = st.selectbox("Seleção Mandante (Fins de tabela)", sorted(list(DADOS_COPA_PONDERADO.keys())), index=0)
    with col2:
        selec_v = st.selectbox("Seleção Visitante (Fins de tabela)", sorted(list(DADOS_COPA_PONDERADO.keys())), index=4)

    if selec_m == selec_v:
        st.warning("Selecione seleções diferentes para o confronto.")
    else:
        # Executa modelo aplicando os pesos de 70% nas eliminatórias
        res_c = realizar_analise_completa(selec_m, selec_v, DADOS_COPA_PONDERADO, MEDIA_GOLS_FIFA, eh_copa=True)
        
        # Card Informativo de Análise de Desempenho Recente
        st.markdown("### 📝 Relatório de Atuação Recente (Eliminatórias)")
        col_rep1, col_rep2 = st.columns(2)
        with col_rep1:
            st.info(f"**{selec_m}:** {DADOS_COPA_PONDERADO[selec_m]['atuacao_comentario']}")
        with col_rep2:
            st.info(f"**{selec_v}:** {DADOS_COPA_PONDERADO[selec_v]['atuacao_comentario']}")
            
        st.markdown("---")

        cm_mod, cm_xg1, cm_xg2 = st.columns(3)
        cm_mod.metric("Placar Mais Provável (Moda)", res_c["placar_moda"], f"{round(res_c['prob_placar']*100, 1)}% de chance")
        cm_xg1.metric(f"xG Ponderado - {selec_m}", res_c["gols_esperados_m"])
        cm_xg2.metric(f"xG Ponderado - {selec_v}", res_c["gols_esperados_v"])

        st.markdown("### 🎲 Odds Justas e Probabilidades Reais")
        colm_m, colm_e, colm_v = st.columns(3)
        colm_m.metric(f"Vitória {selec_m}", f"{round(res_c['prob_m']*100, 1)}%", f"Odd: @{res_c['odd_m']}")
        colm_e.metric("Empate", f"{round(res_c['prob_empate']*100, 1)}%", f"Odd: @{res_c['odd_empate']}")
        colm_v.metric(f"Vitória {selec_v}", f"{round(res_c['prob_v']*100, 1)}%", f"Odd: @{res_c['odd_v']}")

        # Matriz de Calor da Copa
        st.markdown("### 🗺️ Matriz de Probabilidade de Placar Exato")
        fig_c, ax_c = plt.subplots(figsize=(7, 3.5))
        sns.heatmap(res_c["matriz"], annot=True, fmt=".2%", cmap="Oranges", xticklabels=range(6), yticklabels=range(6), ax=ax_c)
        plt.xlabel(f"Gols de {selec_v}")
        plt.ylabel(f"Gols de {selec_m}")
        st.pyplot(fig_c)
        
        st.markdown("### 📈 Projeção de Scouts")
        st.table({
            "Mercado de Estatísticas": ["Linha de Escanteios Totais", "Linha de Cartões Amarelos Totais"],
            "Projeção do Modelo Quant": [res_c["escanteios"], res_c["cartoes"]]
        })
