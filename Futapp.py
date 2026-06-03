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
# CONFIGURAÇÃO DO GOOGLE SHEETS (AUTOMATIZAÇÃO DOS JOGOS)
# ==============================================================================
# ⚠️ INSIRA O ID DA SUA PLANILHA AQUI:
ID_DA_PLANILHA = "1qudxtcLg7y_iw0dxxCN3l8IWX1LdnEb2X4SaBNvuV4I" 
URL_PLANILHA = f"https://docs.google.com/spreadsheets/d/{1qudxtcLg7y_iw0dxxCN3l8IWX1LdnEb2X4SaBNvuV4}/gviz/tq?tqx=out:csv"
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
    "Estados Unidos": {"grupo": "D", "hist_ataque": 1.9, "hist_defesa": 1.0, "
