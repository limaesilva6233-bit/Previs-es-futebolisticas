import itertools
import math
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

# Configuração da página Web do Streamlit
st.set_page_config(
    page_title="Preditor Quantitativo Pro - Futebol 2026",
    page_icon="📊",
    layout="wide",
)

# ==============================================================================
# CONFIGURAÇÃO DO GOOGLE SHEETS (VIA EXCEL PARSE)
# ==============================================================================
# ID e URL corrigidos para evitar falhas de autenticação 404
ID_DA_PLANILHA = "1qudxtcLg7y_iw0dxXCN318IWX1LdnEb2X4SaBNvuV4I"
URL_PLANILHA = f"https://docs.google.com/spreadsheets/d/{ID_DA_PLANILHA}/export?format=xlsx"

# Constantes de Calibração Estatística Globais
MEDIA_GOLS_SÉRIE_A = 1.28
MEDIA_GOLS_FIFA = 1.35
FATOR_CASA_ATAQUE = 1.15  
FATOR_CASA_DEFESA = 0.85  

# ==============================================================================
# BANCOS DE DADOS
# ==============================================================================
DADOS_BRASILEIRAO = {
    "Athletico-PR": {"ataque": 1.5, "defesa": 1.1, "forma": 0.98, "escanteios": 5.5, "cartoes": 2.5, "faltas": 14.2},
    "Atlético-GO": {"ataque": 1.1, "defesa": 1.5, "forma": 0.90, "escanteios": 4.5, "cartoes": 2.8, "faltas": 15.6},
    "Atlético-MG": {"ataque": 1.7, "defesa": 1.1, "forma": 0.95, "escanteios": 5.4, "cartoes": 2.7, "faltas": 14.8},
    "Bahia": {"ataque": 1.6, "defesa": 1.2, "forma": 1.05, "escanteios": 5.3, "cartoes": 2.1, "faltas": 12.4},
    "Botafogo": {"ataque": 2.0, "defesa": 0.9, "forma": 1.20, "escanteios": 5.8, "cartoes": 2.2, "faltas": 13.9},
    "Bragantino": {"ataque": 1.4, "defesa": 1.3, "forma": 0.92, "escanteios": 5.4, "cartoes": 2.6, "faltas": 14.5},
    "Corinthians": {"ataque": 1.4, "defesa": 1.1, "forma": 0.90, "escanteios": 5.1, "cartoes": 2.5, "faltas": 15.1},
    "Criciúma": {"ataque": 1.2, "defesa": 1.5, "forma": 0.90, "escanteios": 4.3, "cartoes": 2.5, "faltas": 14.9},
    "Cruzeiro": {"ataque": 1.4, "defesa": 1.0, "forma": 1.02, "escanteios": 5.0, "cartoes": 2.4, "faltas": 13.6},
    "Cuiabá": {"ataque": 1.0, "defesa": 1.3, "forma": 0.88, "escanteios": 4.1, "cartoes": 2.7, "faltas": 15.3},
    "Flamengo": {"ataque": 2.1, "defesa": 0.9, "forma": 1.10, "escanteios": 5.9, "cartoes": 2.4, "faltas": 12.8},
    "Fluminense": {"ataque": 1.3, "defesa": 1.2, "forma": 0.85, "escanteios": 4.6, "cartoes": 2.6, "faltas": 13.1},
    "Fortaleza": {"ataque": 1.6, "defesa": 1.0, "forma": 1.08, "escanteios": 5.4, "cartoes": 2.3, "faltas": 13.5},
    "Grêmio": {"ataque": 1.5, "defesa": 1.3, "forma": 0.96, "escanteios": 4.9, "cartoes": 2.6, "faltas": 14.4},
    "Internacional": {"ataque": 1.5, "defesa": 0.8, "forma": 1.05, "escanteios": 5.3, "cartoes": 2.4, "faltas": 13.7},
    "Juventude": {"ataque": 1.1, "defesa": 1.3, "forma": 0.96, "escanteios": 4.3, "cartoes": 2.9, "faltas": 16.2},
    "Palmeiras": {"ataque": 1.9, "defesa": 0.8, "forma": 1.15, "escanteios": 6.2, "cartoes": 2.1, "faltas": 13.0},
    "Santos": {"ataque": 1.3, "defesa": 1.1, "forma": 1.00, "escanteios": 4.9, "cartoes": 2.3, "faltas": 14.0},
    "São Paulo": {"ataque": 1.6, "defesa": 0.9, "forma": 1.00, "escanteios": 5.2, "cartoes": 2.5, "faltas": 14.2},
    "Vasco": {"ataque": 1.3, "defesa": 1.3, "forma": 0.95, "escanteios": 4.8, "cartoes": 2.7, "faltas": 15.0},
}

DADOS_COPA_PONDERADO = {
    "México": {"grupo": "A", "hist_ataque": 1.8, "hist_defesa": 1.1, "elim_ataque": 1.6, "elim_defesa": 1.2, "escanteios": 5.4, "cartoes": 2.1, "faltas": 13.2},
    "África do Sul": {"grupo": "A", "hist_ataque": 1.2, "hist_defesa": 1.3, "elim_ataque": 1.3, "elim_defesa": 1.1, "escanteios": 4.6, "cartoes": 1.9, "faltas": 14.5},
    "Coreia do Sul": {"grupo": "A", "hist_ataque": 1.6, "hist_defesa": 1.0, "elim_ataque": 1.8, "elim_defesa": 0.9, "escanteios": 5.1, "cartoes": 1.5, "faltas": 11.2},
    "Chéquia": {"grupo": "A", "hist_ataque": 1.5, "hist_defesa": 1.2, "elim_ataque": 1.4, "elim_defesa": 1.1, "escanteios": 4.9, "cartoes": 2.3, "faltas": 13.8},
    "Canadá": {"grupo": "B", "hist_ataque": 1.5, "hist_defesa": 1.2, "elim_ataque": 1.7, "elim_defesa": 1.1, "escanteios": 5.2, "cartoes": 1.8, "faltas": 12.9},
    "Bósnia e Herzegovina": {"grupo": "B", "hist_ataque": 1.3, "hist_defesa": 1.4, "elim_ataque": 1.2, "elim_defesa": 1.3, "escanteios": 4.7, "cartoes": 2.5, "faltas": 14.7},
    "Catar": {"grupo": "B", "hist_ataque": 1.1, "hist_defesa": 1.6, "elim_ataque": 1.3, "elim_defesa": 1.5, "escanteios": 4.1, "cartoes": 2.0, "faltas": 12.1},
    "Suíça": {"grupo": "B", "hist_ataque": 1.6, "hist_defesa": 1.0, "elim_ataque": 1.7, "elim_defesa": 0.9, "escanteios": 5.5, "cartoes": 1.7, "faltas": 12.5},
    "Brasil": {"grupo": "C", "hist_ataque": 2.5, "hist_defesa": 0.6, "elim_ataque": 1.6, "elim_defesa": 1.1, "escanteios": 6.8, "cartoes": 1.6, "faltas": 13.2},
    "Marrocos": {"grupo": "C", "hist_ataque": 1.9, "hist_defesa": 0.8, "elim_ataque": 2.2, "elim_defesa": 0.7, "escanteios": 5.6, "cartoes": 2.1, "faltas": 14.0},
    "Haiti": {"grupo": "C", "hist_ataque": 0.8, "hist_defesa": 2.4, "elim_ataque": 1.0, "elim_defesa": 2.0, "escanteios": 3.5, "cartoes": 2.4, "faltas": 16.0},
    "Escócia": {"grupo": "C", "hist_ataque": 1.3, "hist_defesa": 1.4, "elim_ataque": 1.4, "elim_defesa": 1.2, "escanteios": 4.8, "cartoes": 2.2, "faltas": 14.2},
    "Estados Unidos": {"grupo": "D", "hist_ataque": 1.9, "hist_defesa": 1.0, "elim_ataque": 1.8, "elim_defesa": 0.9, "escanteios": 5.8, "cartoes": 1.9, "faltas": 12.2},
    "Paraguai": {"grupo": "D", "hist_ataque": 1.1, "hist_defesa": 0.9, "elim_ataque": 1.0, "elim_defesa": 0.8, "escanteios": 4.5, "cartoes": 2.8, "faltas": 16.5},
    "Austrália": {"grupo": "D", "hist_ataque": 1.4, "hist_defesa": 1.2, "elim_ataque": 1.3, "elim_defesa": 1.1, "escanteios": 5.0, "cartoes": 1.8, "faltas": 13.5},
    "Turquia": {"grupo": "D", "hist_ataque": 1.7, "hist_defesa": 1.3, "elim_ataque": 1.8, "elim_defesa": 1.1, "escanteios": 5.3, "cartoes": 2.6, "faltas": 14.8},
    "Alemanha": {"grupo": "E", "hist_ataque": 2.3, "hist_defesa": 0.9, "elim_ataque": 2.2, "elim_defesa": 0.9, "escanteios": 6.5, "cartoes": 1.8, "faltas": 11.9},
    "Curaçao": {"grupo": "E", "hist_ataque": 0.7, "hist_defesa": 2.5, "elim_ataque": 0.9, "elim_defesa": 2.1, "escanteios": 3.4, "cartoes": 2.3, "faltas": 15.2},
    "Costa do Marfim": {"grupo": "E", "hist_ataque": 1.6, "hist_defesa": 1.1, "elim_ataque": 1.8, "elim_defesa": 1.0, "escanteios": 5.2, "cartoes": 2.2, "faltas": 14.1},
    "Equador": {"grupo": "E", "hist_ataque": 1.5, "hist_defesa": 1.0, "elim_ataque": 1.4, "elim_defesa": 0.8, "escanteios": 5.1, "cartoes": 2.4, "faltas": 15.0},
    "Holanda": {"grupo": "F", "hist_ataque": 2.1, "hist_defesa": 0.9, "elim_ataque": 2.3, "elim_defesa": 0.8, "escanteios": 6.1, "cartoes": 1.7, "faltas": 12.4},
    "Japão": {"grupo": "F", "hist_ataque": 1.8, "hist_defesa": 1.0, "elim_ataque": 2.1, "elim_defesa": 0.7, "escanteios": 5.5, "cartoes": 1.3, "faltas": 10.5},
    "Suécia": {"grupo": "F", "hist_ataque": 1.6, "hist_defesa": 1.1, "elim_ataque": 1.5, "elim_defesa": 1.0, "escanteios": 5.4, "cartoes": 2.0, "faltas": 13.0},
    "Tunísia": {"grupo": "F", "hist_ataque": 1.1, "hist_defesa": 1.3, "elim_ataque": 1.2, "elim_defesa": 1.1, "escanteios": 4.2, "cartoes": 2.2, "faltas": 14.9},
    "Bélgica": {"grupo": "G", "hist_ataque": 2.0, "hist_defesa": 1.0, "elim_ataque": 1.9, "elim_defesa": 1.1, "escanteios": 5.9, "cartoes": 1.6, "faltas": 11.8},
    "Egito": {"grupo": "G", "hist_ataque": 1.4, "hist_defesa": 1.1, "elim_ataque": 1.5, "elim_defesa": 1.0, "escanteios": 4.6, "cartoes": 2.1, "faltas": 13.4},
    "Irã": {"grupo": "G", "hist_ataque": 1.3, "hist_defesa": 1.2, "elim_ataque": 1.4, "elim_defesa": 1.1, "escanteios": 4.4, "cartoes": 2.3, "faltas": 14.2},
    "Nova Zelândia": {"grupo": "G", "hist_ataque": 1.0, "hist_defesa": 1.7, "elim_ataque": 1.2, "elim_defesa": 1.4, "escanteios": 3.9, "cartoes": 1.7, "faltas": 13.1},
    "Espanha": {"grupo": "H", "hist_ataque": 2.3, "hist_defesa": 0.8, "elim_ataque": 2.4, "elim_defesa": 0.6, "escanteios": 6.7, "cartoes": 1.5, "faltas": 11.0},
    "Cabo Verde": {"grupo": "H", "hist_ataque": 1.1, "hist_defesa": 1.5, "elim_ataque": 1.3, "elim_defesa": 1.3, "escanteios": 4.0, "cartoes": 2.1, "faltas": 14.6},
    "Arábia Saudita": {"grupo": "H", "hist_ataque": 1.2, "hist_defesa": 1.4, "elim_ataque": 1.3, "elim_defesa": 1.2, "escanteios": 4.3, "cartoes": 2.4, "faltas": 13.9},
    "Uruguai": {"grupo": "H", "hist_ataque": 1.9, "hist_defesa": 0.9, "elim_ataque": 2.1, "elim_defesa": 0.8, "escanteios": 5.6, "cartoes": 2.6, "faltas": 15.4},
    "França": {"grupo": "I", "hist_ataque": 2.5, "hist_defesa": 0.8, "elim_ataque": 2.6, "elim_defesa": 0.6, "escanteios": 6.4, "cartoes": 1.5, "faltas": 11.5},
    "Iraque": {"grupo": "I", "hist_ataque": 1.2, "hist_defesa": 1.5, "elim_ataque": 1.3, "elim_defesa": 1.3, "escanteios": 4.2, "cartoes": 2.2, "faltas": 14.5},
    "Noruega": {"grupo": "I", "hist_ataque": 1.8, "hist_defesa": 1.2, "elim_ataque": 2.0, "elim_defesa": 1.0, "escanteios": 5.3, "cartoes": 1.9, "faltas": 12.0},
    "Senegal": {"grupo": "I", "hist_ataque": 1.6, "hist_defesa": 1.0, "elim_ataque": 1.7, "elim_defesa": 0.9, "escanteios": 5.0, "cartoes": 2.1, "faltas": 14.3},
    "Argentina": {"grupo": "J", "hist_ataque": 2.4, "hist_defesa": 0.7, "elim_ataque": 2.5, "elim_defesa": 0.5, "escanteios": 6.2, "cartoes": 2.0, "faltas": 12.6},
    "Argélia": {"grupo": "J", "hist_ataque": 1.5, "hist_defesa": 1.2, "elim_ataque": 1.6, "elim_defesa": 1.0, "escanteios": 4.9, "cartoes": 2.3, "faltas": 14.0},
    "Áustria": {"grupo": "J", "hist_ataque": 1.6, "hist_defesa": 1.1, "elim_ataque": 1.7, "elim_defesa": 1.0, "escanteios": 5.4, "cartoes": 2.1, "faltas": 13.5},
    "Jordânia": {"grupo": "J", "hist_ataque": 1.0, "hist_defesa": 1.6, "elim_ataque": 1.2, "elim_defesa": 1.4, "escanteios": 3.8, "cartoes": 2.2, "faltas": 15.0},
    "Portugal": {"grupo": "K", "hist_ataque": 2.4, "hist_defesa": 0.8, "elim_ataque": 2.5, "elim_defesa": 0.7, "escanteios": 6.3, "cartoes": 1.9, "faltas": 11.4},
    "RD do Congo": {"grupo": "K", "hist_ataque": 1.3, "hist_defesa": 1.3, "elim_ataque": 1.4, "elim_defesa": 1.1, "escanteios": 4.5, "cartoes": 2.4, "faltas": 15.5},
    "Uzbequistão": {"grupo": "K", "hist_ataque": 1.2, "hist_defesa": 1.2, "elim_ataque": 1.4, "elim_defesa": 1.0, "escanteios": 4.4, "cartoes": 1.8, "faltas": 13.2},
    "Colômbia": {"grupo": "K", "hist_ataque": 1.8, "hist_defesa": 0.9, "elim_ataque": 2.0, "elim_defesa": 0.8, "escanteios": 5.4, "cartoes": 2.7, "faltas": 14.9},
    "Inglaterra": {"grupo": "L", "hist_ataque": 2.3, "hist_defesa": 0.8, "elim_ataque": 2.4, "elim_defesa": 0.7, "escanteios": 6.6, "cartoes": 1.4, "faltas": 11.2},
    "Croácia": {"grupo": "L", "hist_ataque": 1.6, "hist_defesa": 1.0, "elim_ataque": 1.5, "elim_defesa": 0.9, "escanteios": 5.2, "cartoes": 1.8, "faltas": 12.1},
    "Gana": {"grupo": "L", "hist_ataque": 1.4, "hist_defesa": 1.4, "elim_ataque": 1.5, "elim_defesa": 1.2, "escanteios": 4.7, "cartoes": 2.3, "faltas": 14.8},
    "Panamá": {"grupo": "L", "hist_ataque": 1.1, "hist_defesa": 1.6, "elim_ataque": 1.4, "elim_defesa": 1.2, "escanteios": 4.0, "cartoes": 2.0, "faltas": 13.6},
}

# ==============================================================================
# MOTOR MATEMÁTICO DE POISSON
# ==============================================================================
def calcular_poisson(lambda_gols, k):
    if lambda_gols <= 0: return 0.0
    return (math.exp(-lambda_gols) * (lambda_gols**k)) / math.factorial(k)

# ==============================================================================
# SISTEMA DE CÁLCULO DE PONTOS DO BOLÃO
# ==============================================================================
def computar_pontos_bolao(gols_m_prev, gols_v_prev, gols_m_real, gols_v_real, eh_mata_mata=False):
    vencedor_prev = "M" if gols_m_prev > gols_v_prev else ("V" if gols_v_prev > gols_m_prev else "E")
    vencedor_real = "M" if gols_m_real > gols_v_real else ("V" if gols_v_real > gols_m_real else "E")
    
    saldo_prev = gols_m_prev - gols_v_prev
    saldo_real = gols_m_real - gols_v_real

    gols_vencedor_prev = max(gols_m_prev, gols_v_prev) if vencedor_prev != "E" else gols_m_prev
    gols_vencedor_real = max(gols_m_real, gols_v_real) if vencedor_real != "E" else gols_m_real
    
    gols_perdedor_prev = min(gols_m_prev, gols_v_prev) if vencedor_prev != "E" else gols_m_prev
    gols_perdedor_real = min(gols_m_real, gols_v_real) if vencedor_real != "E" else gols_m_real

    pontos = 0
    if gols_m_prev == gols_m_real and gols_v_prev == gols_v_real:
        pontos = 25
    elif vencedor_prev == vencedor_real and gols_vencedor_prev == gols_vencedor_real and vencedor_real != "E":
        pontos = 18
    elif vencedor_prev == vencedor_real and saldo_prev == saldo_real:
        pontos = 15
    elif gols_perdedor_prev == gols_perdedor_real and vencedor_real != "E":
        pontos = 12
    elif vencedor_prev == vencedor_real:
        pontos = 10
    else:
        pontos = 0

    if eh_mata_mata:
        pontos *= 2
        
    return pontos

def realizar_analise_completa(m_time, v_time, banco_dados, media_gols_base, eh_copa=False):
    t_m = banco_dados[m_time]
    t_v = banco_dados[v_time]

    if not eh_copa:
        lambda_m = (t_m["ataque"] * FATOR_CASA_ATAQUE) * (t_v["defesa"] / media_gols_base) * t_m["forma"]
        lambda_v = (t_v["ataque"] * (t_m["defesa"] * FATOR_CASA_DEFESA) / media_gols_base) * t_v["forma"]
    else:
        ataque_m = ((t_m["hist_ataque"] * 0.3) + (t_m["elim_ataque"] * 0.7))
        defesa_m = ((t_m["hist_defesa"] * 0.3) + (t_m["elim_defesa"] * 0.7))
        
        ataque_v = ((t_v["hist_ataque"] * 0.3) + (t_v["elim_ataque"] * 0.7))
        defesa_v = ((t_v["hist_defesa"] * 0.3) + (t_v["elim_defesa"] * 0.7))
        
        lambda_m = ataque_m * (defesa_v / media_gols_base)
        lambda_v = ataque_v * (defesa_m / media_gols_base)

    max_gols = 6
    matriz_gols = pd.DataFrame(0.0, index=range(max_gols), columns=range(max_gols))
    prob_m, prob_v, prob_empate = 0.0, 0.0, 0.0
    prob_btts_sim = 0.0
    prob_over_15 = prob_over_25 = 0.0

    for g_m, g_v in itertools.product(range(max_gols), range(max_gols)):
        p_combinada = calcular_poisson(lambda_m, g_m) * calcular_poisson(lambda_v, g_v)
        matriz_gols.at[g_m, g_v] = p_combinada

        if g_m > g_v: prob_m += p_combinada
        elif g_v > g_m: prob_v += p_combinada
        else: prob_empate += p_combinada

        if g_m > 0 and g_v > 0: prob_btts_sim += p_combinada
        if g_m + g_v > 1.5: prob_over_15 += p_combinada
        if g_m + g_v > 2.5: prob_over_25 += p_combinada

    placar_index = matriz_gols.stack().idxmax()
    prob_placar_moda = matriz_gols.at[placar_index[0], placar_index[1]]

    return {
        "prob_m": prob_m, "prob_empate": prob_empate, "prob_v": prob_v,
        "placar_moda_m": placar_index[0], "placar_moda_v": placar_index[1],
        "placar_moda_str": f"{placar_index[0]} x {placar_index[1]}", "prob_placar": prob_placar_moda,
        "matriz": matriz_gols, "escanteios": round((t_m["escanteios"] + t_v["escanteios"]), 1),
        "cartoes": round(t_m["cartoes"] + t_v["cartoes"], 1), "faltas": round((t_m["faltas"] + t_v["faltas"]), 1),
        "gols_esperados_m": round(lambda_m, 2), "gols_esperados_v": round(lambda_v, 2),
        "btts_sim": prob_btts_sim, "btts_nao": 1.0 - prob_btts_sim,
        "over_15": prob_over_15, "over_25": prob_over_25
    }

# ==============================================================================
# INTERFACE INTERATIVA (STREAMLIT DASHBOARD)
# ==============================================================================
st.title("📊 Preditor Quantitativo Pro - Especial Bolão Copa 2026")

tab_br, tab_copa, tab_auditoria = st.tabs(["🇧🇷 Campeonato Brasileiro", "🌍 Copa do Mundo 2026", "🏆 Histórico & Auditoria do Bolão"])

with tab_br:
    col1, col2 = st.columns(2)
    with col1: time_m = st.selectbox("Mandante (Casa)", sorted(list(DADOS_BRASILEIRAO.keys())), index=0)
    with col2: time_v = st.selectbox("Visitante (Fora)", sorted(list(DADOS_BRASILEIRAO.keys())), index=1)
    
    if time_m == time_v:
        st.warning("⚠️ Selecione dois times diferentes.")
    else:
        res = realizar_analise_completa(time_m, time_v, DADOS_BRASILEIRAO, MEDIA_GOLS_SÉRIE_A)
        c_mod, c_xg1, c_xg2 = st.columns(3)
        c_mod.metric("Placar Conclusivo", res["placar_moda_str"], f"{round(res['prob_placar']*100, 1)}% de chance")
        c_xg1.metric(f"xG - {time_m}", res["gols_esperados_m"])
        c_xg2.metric(f"xG - {time_v}", res["gols_esperados_v"])

        with st.expander("📊 Ver Matriz de Probabilidades Estendida"):
            fig, ax = plt.subplots(figsize=(6, 4))
            sns.heatmap(res["matriz"], annot=True, fmt=".1%", cmap="YlOrBr", ax=ax, xticklabels=range(6), yticklabels=range(6))
            st.pyplot(fig)

with tab_copa:
    lista_completa_copa = sorted(list(DADOS_COPA_PONDERADO.keys()))
    col_c1, col_c2 = st.columns(2)
    with col_c1: selec_m = st.selectbox("Seleção A", lista_completa_copa, index=lista_completa_copa.index("Brasil"))
    with col_c2: selec_v = st.selectbox("Seleção B", lista_completa_copa, index=lista_completa_copa.index("Marrocos"))

    if selec_m == selec_v:
        st.warning("⚠️ Selecione duas seleções diferentes.")
    else:
        res_c = realizar_analise_completa(selec_m, selec_v, DADOS_COPA_PONDERADO, MEDIA_GOLS_FIFA, eh_copa=True)
        
        cm_mod, cm_xg1, cm_xg2 = st.columns(3)
        cm_mod.metric("Placar Sugerido pelo Modelo", res_c["placar_moda_str"], f"{round(res_c['prob_placar']*100, 1)}% de confiança")
        cm_xg1.metric(f"xG Ajustado - {selec_m}", res_c["gols_esperados_m"])
        cm_xg2.metric(f"xG Ajustado - {selec_v}", res_c["gols_esperados_v"])

        st.markdown("### ⚽ Probabilidades de Linhas de Gols")
        col_cg1, col_cg2 = st.columns(2)
        with col_cg1:
            st.markdown(f"**Mais de 1.5 Gols:** {round(res_c['over_15']*100, 1)}%")
            st.markdown(f"**Mais de 2.5 Gols:** {round(res_c['over_25']*100, 1)}%")
        with col_cg2:
            st.markdown(f"**Ambas Marcam - SIM:** {round(res_c['btts_sim']*100, 1)}%")
            st.markdown(f"**Ambas Marcam - NÃO:** {round(res_c['btts_nao']*100, 1)}%")

# ==============================================================================
# AUDITORIA TOTALMENTE PROCESSADA EM SEGUNDO PLANO
# ==============================================================================
with tab_auditoria:
    st.header("🏆 Auditoria de Performance em Tempo Real")
    st.markdown("Esta aba calcula automaticamente a pontuação que o algoritmo obteria com base nos resultados preenchidos na sua planilha.")

    try:
        df_sheets = pd.read_excel(URL_PLANILHA)
        df_sheets.columns = df_sheets.columns.str.strip()
        
        colunas_obrigatorias = ['Selecao_A', 'Selecao_B', 'Gols_A', 'Gols_B', 'Mata_Mata']
        
        if all(col in df_sheets.columns for col in colunas_obrigatorias):
            df_encerrados = df_sheets.dropna(subset=['Gols_A', 'Gols_B']).copy()
            
            df_encerrados['Gols_A'] = pd.to_numeric(df_encerrados['Gols_A'], errors='coerce')
            df_encerrados['Gols_B'] = pd.to_numeric(df_encerrados['Gols_B'], errors='coerce')
            df_encerrados = df_encerrados.dropna(subset=['Gols_A', 'Gols_B'])

            historico_calculado = []
            
            for _, linha in df_encerrados.iterrows():
                time_a = str(linha['Selecao_A']).strip()
                time_v = str(linha['Selecao_B']).strip()
                gols_a_real = int(linha['Gols_A'])
                gols_b_real = int(linha['Gols_B'])
                eh_mata = int(linha['Mata_Mata']) == 1
                
                if time_a in DADOS_COPA_PONDERADO and time_v in DADOS_COPA_PONDERADO:
                    analise_retroativa = realizar_analise_completa(time_a, time_v, DADOS_COPA_PONDERADO, MEDIA_GOLS_FIFA, eh_copa=True)
                    
                    g_a_sugerido = analise_retroativa["placar_moda_m"]
                    g_v_sugerido = analise_retroativa["placar_moda_v"]
                    placar_sugerido_texto = analise_retroativa["placar_moda_str"]
                    
                    pontos = computar_pontos_bolao(g_a_sugerido, g_v_sugerido, gols_a_real, gols_b_real, eh_mata_mata=eh_mata)
                    
                    historico_calculado.append({
                        "Partida": f"{time_a} x {time_v}",
                        "Tipo": "Mata-Mata" if eh_mata else "Fase de Grupos",
                        "Sugestão do App": placar_sugerido_texto,
                        "Placar Real Oficial": f"{gols_a_real} x {gols_b_real}",
                        "Pontos Obtidos": pontos
                    })

            if len(historico_calculado) > 0:
                df_final = pd.DataFrame(historico_calculado)
                total_pontos = df_final["Pontos Obtidos"].sum()
                
                c_m1, c_m2 = st.columns(2)
                c_m1.metric("🎯 Total Acumulado pelo App", f"{total_pontos} pts")
                c_m2.metric("🏁 Jogos Encerrados Processados", f"{len(df_final)} partidas")
                
                st.markdown("#### 📋 Histórico de Cruzamento (Modelo vs Realidade)")
                st.dataframe(df_final, use_container_width=True)
            else:
                st.info("📅 Preencha os placares de gols na sua planilha para ver os pontos computados aqui!")
        else:
            st.error(f"⚠️ As colunas lidas não batem. Nomes esperados: {colunas_obrigatorias}")
            
    except Exception as e:
        st.error(f"Erro ao processar estrutura: {e}")
