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

# Constantes de Calibração Estatística Globais
MEDIA_GOLS_SÉRIE_A = 1.28
MEDIA_GOLS_FIFA = 1.35
FATOR_CASA_ATAQUE = 1.15  # Mandante ganha +15% de força ofensiva no Brasileirão
FATOR_CASA_DEFESA = 0.85  # Mandante reduz em 15% os gols sofridos no Brasileirão

# ==============================================================================
# 1. BANCO DE DADOS COMPLETO: OS 20 TIMES DA SÉRIE A DO BRASILEIRÃO
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

# ==============================================================================
# 2. BANCO DE DADOS COMPLETO: AS 48 SELEÇÕES DA COPA DO MUNDO 2026
# Pesos: 30% Histórico Geral / 70% Campanha nas Eliminatórias e Atuação Recente
# ==============================================================================
DADOS_COPA_PONDERADO = {
    # GRUPO A
    "México": {"grupo": "A", "hist_ataque": 1.8, "hist_defesa": 1.1, "elim_ataque": 1.6, "elim_defesa": 1.2, "escanteios": 5.4, "cartoes": 2.1, "faltas": 13.2, "atuacao_comentario": "Sólido jogando em casa, mas com dificuldades de criação contra defesas fechadas europeias."},
    "África do Sul": {"grupo": "A", "hist_ataque": 1.2, "hist_defesa": 1.3, "elim_ataque": 1.3, "elim_defesa": 1.1, "escanteios": 4.6, "cartoes": 1.9, "faltas": 14.5, "atuacao_comentario": "Campanha surpreendente e física no continente africano, baseada em contra-ataques velozes."},
    "Coreia do Sul": {"grupo": "A", "hist_ataque": 1.6, "hist_defesa": 1.0, "elim_ataque": 1.8, "elim_defesa": 0.9, "escanteios": 5.1, "cartoes": 1.5, "faltas": 11.2, "atuacao_comentario": "Dominante nas eliminatórias asiáticas com transição ofensiva muito rápida organizada e limpa."},
    "Chéquia": {"grupo": "A", "hist_ataque": 1.5, "hist_defesa": 1.2, "elim_ataque": 1.4, "elim_defesa": 1.1, "escanteios": 4.9, "cartoes": 2.3, "faltas": 13.8, "atuacao_comentario": "Jogo aéreo muito forte e físico, garantiu vaga com consistência na repescagem europeia."},
    # GRUPO B
    "Canadá": {"grupo": "B", "hist_ataque": 1.5, "hist_defesa": 1.2, "elim_ataque": 1.7, "elim_defesa": 1.1, "escanteios": 5.2, "cartoes": 1.8, "faltas": 12.9, "atuacao_comentario": "Grande evolução de ritmo e volume ofensivo pelas pontas nas partidas recentes da CONCACAF."},
    "Bósnia e Herzegovina": {"grupo": "B", "hist_ataque": 1.3, "hist_defesa": 1.4, "elim_ataque": 1.2, "elim_defesa": 1.3, "escanteios": 4.7, "cartoes": 2.5, "faltas": 14.7, "atuacao_comentario": "Equipe muito truncada e faltosa. Conquistou pontos importantes jogando de forma reativa."},
    "Catar": {"grupo": "B", "hist_ataque": 1.1, "hist_defesa": 1.6, "elim_ataque": 1.3, "elim_defesa": 1.5, "escanteios": 4.1, "cartoes": 2.0, "faltas": 12.1, "atuacao_comentario": "Organizado taticamente, mas possui sérias desvantagens de imposição física contra elencos de elite."},
    "Suíça": {"grupo": "B", "hist_ataque": 1.6, "hist_defesa": 1.0, "elim_ataque": 1.7, "elim_defesa": 0.9, "escanteios": 5.5, "cartoes": 1.7, "faltas": 12.5, "atuacao_comentario": "Altíssima disciplina tática. Modelo defensivo sólido que pune os erros adversários com eficácia."},
    # GRUPO C
    "Brasil": {"grupo": "C", "hist_ataque": 2.5, "hist_defesa": 0.6, "elim_ataque": 1.6, "elim_defesa": 1.1, "escanteios": 6.8, "cartoes": 1.6, "faltas": 13.2, "atuacao_comentario": "Oscilante nas Eliminatórias. Transições defensivas problemáticas e dificuldades contra blocos baixos."},
    "Marrocos": {"grupo": "C", "hist_ataque": 1.9, "hist_defesa": 0.8, "elim_ataque": 2.2, "elim_defesa": 0.7, "escanteios": 5.6, "cartoes": 2.1, "faltas": 14.0, "atuacao_comentario": "Excelente fase. Passou o trator na África com estilo muito mais agressivo do que na Copa passada."},
    "Haiti": {"grupo": "C", "hist_ataque": 0.8, "hist_defesa": 2.4, "elim_ataque": 1.0, "elim_defesa": 2.0, "escanteios": 3.5, "cartoes": 2.4, "faltas": 16.0, "atuacao_comentario": "Vaga histórica conquistada na retranca. Apresenta sérias fragilidades se sofrer gol cedo."},
    "Escócia": {"grupo": "C", "hist_ataque": 1.3, "hist_defesa": 1.4, "elim_ataque": 1.4, "elim_defesa": 1.2, "escanteios": 4.8, "cartoes": 2.2, "faltas": 14.2, "atuacao_comentario": "Futebol britânico clássico de muita entrega física, forte marcação e bolas paradas perigosas."},
    # GRUPO D
    "Estados Unidos": {"grupo": "D", "hist_ataque": 1.9, "hist_defesa": 1.0, "elim_ataque": 1.8, "elim_defesa": 0.9, "escanteios": 5.8, "cartoes": 1.9, "faltas": 12.2, "atuacao_comentario": "Geração veloz com boa intensidade de pressão na saída de bola adversária durante a preparação."},
    "Paraguai": {"grupo": "D", "hist_ataque": 1.1, "hist_defesa": 0.9, "elim_ataque": 1.0, "elim_defesa": 0.8, "escanteios": 4.5, "cartoes": 2.8, "faltas": 16.5, "atuacao_comentario": "A menor média de gols somados das eliminatórias. Jogo extremamente faltoso, truncado e focado em travar o rival."},
    "Austrália": {"grupo": "D", "hist_ataque": 1.4, "hist_defesa": 1.2, "elim_ataque": 1.3, "elim_defesa": 1.1, "escanteios": 5.0, "cartoes": 1.8, "faltas": 13.5, "atuacao_comentario": "Jogo físico de recomposição rápida. Garante estabilidade atrás, mas cria pouco no ataque."},
    "Turquia": {"grupo": "D", "hist_ataque": 1.7, "hist_defesa": 1.3, "elim_ataque": 1.8, "elim_defesa": 1.1, "escanteios": 5.3, "cartoes": 2.6, "faltas": 14.8, "atuacao_comentario": "Equipe muito técnica e imprevisível. Costuma protagonizar jogos abertos e indisciplinados."},
    # GRUPO E
    "Alemanha": {"grupo": "E", "hist_ataque": 2.3, "hist_defesa": 0.9, "elim_ataque": 2.2, "elim_defesa": 0.9, "escanteios": 6.5, "cartoes": 1.8, "faltas": 11.9, "atuacao_comentario": "Grande evolução sob novo comando tático, retomando o controle possessivo do meio-campo."},
    "Curaçao": {"grupo": "E", "hist_ataque": 0.7, "hist_defesa": 2.5, "elim_ataque": 0.9, "elim_defesa": 2.1, "escanteios": 3.4, "cartoes": 2.3, "faltas": 15.2, "atuacao_comentario": "A maior zebra das Américas. Elenco esforçado, mas com sérios problemas de posicionamento na zaga."},
    "Costa do Marfim": {"grupo": "E", "hist_ataque": 1.6, "hist_defesa": 1.1, "elim_ataque": 1.8, "elim_defesa": 1.0, "escanteios": 5.2, "cartoes": 2.2, "faltas": 14.1, "atuacao_comentario": "Futebol vertical de altíssima força física e imposição nas divididas de meio de campo."},
    "Equador": {"grupo": "E", "hist_ataque": 1.5, "hist_defesa": 1.0, "elim_ataque": 1.4, "elim_defesa": 0.8, "escanteios": 5.1, "cartoes": 2.4, "faltas": 15.0, "atuacao_comentario": "Defesa fortíssima e veloz na transição. Jogo de muita imposição física e intensidade atlética."},
    # GRUPO F
    "Holanda": {"grupo": "F", "hist_ataque": 2.1, "hist_defesa": 0.9, "elim_ataque": 2.3, "elim_defesa": 0.8, "escanteios": 6.1, "cartoes": 1.7, "faltas": 12.4, "atuacao_comentario": "Futebol total com alas agressivos. Excelente aproveitamento ofensivo nas eliminatórias europeias."},
    "Japão": {"grupo": "F", "hist_ataque": 1.8, "hist_defesa": 1.0, "elim_ataque": 2.1, "elim_defesa": 0.7, "escanteios": 5.5, "cartoes": 1.3, "faltas": 10.5, "atuacao_comentario": "Campanha irretocável na Ásia. Dinâmica coletiva espetacular e baixíssimo número de faltas cometidas."},
    "Suécia": {"grupo": "F", "hist_ataque": 1.6, "hist_defesa": 1.1, "elim_ataque": 1.5, "elim_defesa": 1.0, "escanteios": 5.4, "cartoes": 2.0, "faltas": 13.0, "atuacao_comentario": "Jogo compacto, disciplinado e de forte recomposição pelas linhas de quatro defensores."},
    "Tunísia": {"grupo": "F", "hist_ataque": 1.1, "hist_defesa": 1.3, "elim_ataque": 1.2, "elim_defesa": 1.1, "escanteios": 4.2, "cartoes": 2.2, "faltas": 14.9, "atuacao_comentario": "Estilo focado em quebrar o ritmo dos favoritos usando forte contato físico na intermediária."},
    # GRUPO G
    "Bélgica": {"grupo": "G", "hist_ataque": 2.0, "hist_defesa": 1.0, "elim_ataque": 1.9, "elim_defesa": 1.1, "escanteios": 5.9, "cartoes": 1.6, "faltas": 11.8, "atuacao_comentario": "Transição de geração em andamento. Mantém qualidade técnica alta, mas cedeu espaços na zaga."},
    "Egito": {"grupo": "G", "hist_ataque": 1.4, "hist_defesa": 1.1, "elim_ataque": 1.5, "elim_defesa": 1.0, "escanteios": 4.6, "cartoes": 2.1, "faltas": 13.4, "atuacao_comentario": "Futebol focado em lançamentos longos e jogadas individuais rápidas de seus atacantes de ponta."},
    "Irã": {"grupo": "G", "hist_ataque": 1.3, "hist_defesa": 1.2, "elim_ataque": 1.4, "elim_defesa": 1.1, "escanteios": 4.4, "cartoes": 2.3, "faltas": 14.2, "atuacao_comentario": "Uma das defesas mais consolidadas da Ásia. Sabe sofrer e travar partidas contra gigantes."},
    "Nova Zelândia": {"grupo": "G", "hist_ataque": 1.0, "hist_defesa": 1.7, "elim_ataque": 1.2, "elim_defesa": 1.4, "escanteios": 3.9, "cartoes": 1.7, "faltas": 13.1, "atuacao_comentario": "Dominou a Oceania com folga, mas o ritmo competitivo local é abaixo dos padrões de Copa."},
    # GRUPO H
    "Espanha": {"grupo": "H", "hist_ataque": 2.3, "hist_defesa": 0.8, "elim_ataque": 2.4, "elim_defesa": 0.6, "escanteios": 6.7, "cartoes": 1.5, "faltas": 11.0, "atuacao_comentario": "Futebol de extrema posse e sufocamento. Sofre pouquíssimas faltas e finaliza com alta precisão."},
    "Cabo Verde": {"grupo": "H", "hist_ataque": 1.1, "hist_defesa": 1.5, "elim_ataque": 1.3, "elim_defesa": 1.3, "escanteios": 4.0, "cartoes": 2.1, "faltas": 14.6, "atuacao_comentario": "Classificação heroica. Coletivo muito bem encaixado com transições rápidas pelos lados."},
    "Arábia Saudita": {"grupo": "H", "hist_ataque": 1.2, "hist_defesa": 1.4, "elim_ataque": 1.3, "elim_defesa": 1.2, "escanteios": 4.3, "cartoes": 2.4, "faltas": 13.9, "atuacao_comentario": "Time veloz e intenso em casa, mas que costuma apresentar desatenções táticas na Europa/Américas."},
    "Uruguai": {"grupo": "H", "hist_ataque": 1.9, "hist_defesa": 0.9, "elim_ataque": 2.1, "elim_defesa": 0.8, "escanteios": 5.6, "cartoes": 2.6, "faltas": 15.4, "atuacao_comentario": "Futebol de altíssima intensidade (pressão sufocante). Jogo muito vertical com forte contato."},
    # GRUPO I
    "França": {"grupo": "I", "hist_ataque": 2.5, "hist_defesa": 0.8, "elim_ataque": 2.6, "elim_defesa": 0.6, "escanteios": 6.4, "cartoes": 1.5, "faltas": 11.5, "atuacao_comentario": "Favorita destacada. Elenco cirúrgico e letal com poder de fogo devastador nos jogos recentes."},
    "Iraque": {"grupo": "I", "hist_ataque": 1.2, "hist_defesa": 1.5, "elim_ataque": 1.3, "elim_defesa": 1.3, "escanteios": 4.2, "cartoes": 2.2, "faltas": 14.5, "atuacao_comentario": "Conquistou a vaga com base em bolas paradas e uma defesa aguerrida de forte imposição interna."},
    "Noruega": {"grupo": "I", "hist_ataque": 1.8, "hist_defesa": 1.2, "elim_ataque": 2.0, "elim_defesa": 1.0, "escanteios": 5.3, "cartoes": 1.9, "faltas": 12.0, "atuacao_comentario": "Ataque impulsionado por centroavante de elite mundial. Depende muito do ritmo de seus meias."},
    "Senegal": {"grupo": "I", "hist_ataque": 1.6, "hist_defesa": 1.0, "elim_ataque": 1.7, "elim_defesa": 0.9, "escanteios": 5.0, "cartoes": 2.1, "faltas": 14.3, "atuacao_comentario": "Principal força africana em balanço tático. Robusto no meio, rápido nas pontas e zaga segura."},
    # GRUPO J
    "Argentina": {"grupo": "J", "hist_ataque": 2.4, "hist_defesa": 0.7, "elim_ataque": 2.5, "elim_defesa": 0.5, "escanteios": 6.2, "cartoes": 2.0, "faltas": 12.6, "atuacao_comentario": "Atual campeã com domínio total das Eliminatórias. Solidez defensiva espetacular e controle absoluto."},
    "Argélia": {"grupo": "J", "hist_ataque": 1.5, "hist_defesa": 1.2, "elim_ataque": 1.6, "elim_defesa": 1.0, "escanteios": 4.9, "cartoes": 2.3, "faltas": 14.0, "atuacao_comentario": "Futebol muito técnico e intenso. Apresentou grande evolução na criação ofensiva recente."},
    "Áustria": {"grupo": "J", "hist_ataque": 1.6, "hist_defesa": 1.1, "elim_ataque": 1.7, "elim_defesa": 1.0, "escanteios": 5.4, "cartoes": 2.1, "faltas": 13.5, "atuacao_comentario": "Estilo baseado em pressão alta agressiva constante, forçando erros na saída adversária."},
    "Jordânia": {"grupo": "J", "hist_ataque": 1.0, "hist_defesa": 1.6, "elim_ataque": 1.2, "elim_defesa": 1.4, "escanteios": 3.8, "cartoes": 2.2, "faltas": 15.0, "atuacao_comentario": "Zebra asiática focada em fechar espaços centrais e abusar de faltas táticas no meio-campo."},
    # GRUPO K
    "Portugal": {"grupo": "K", "hist_ataque": 2.4, "hist_defesa": 0.8, "elim_ataque": 2.5, "elim_defesa": 0.7, "escanteios": 6.3, "cartoes": 1.9, "faltas": 11.4, "atuacao_comentario": "Campanha avassaladora na Europa com alto índice de posse criativa e finalizações por jogo."},
    "RD do Congo": {"grupo": "K", "hist_ataque": 1.3, "hist_defesa": 1.3, "elim_ataque": 1.4, "elim_defesa": 1.1, "escanteios": 4.5, "cartoes": 2.4, "faltas": 15.5, "atuacao_comentario": "Estilo físico explosivo. Consegue incomodar defesas lentas, mas deixa espaços atrás."},
    "Uzbequistão": {"grupo": "K", "hist_ataque": 1.2, "hist_defesa": 1.2, "elim_ataque": 1.4, "elim_defesa": 1.0, "escanteios": 4.4, "cartoes": 1.8, "faltas": 13.2, "atuacao_comentario": "Time em clara ascensão tática na Ásia, focado em forte disciplina posicional de linhas compactas."},
    "Colômbia": {"grupo": "K", "hist_ataque": 1.8, "hist_defesa": 0.9, "elim_ataque": 2.0, "elim_defesa": 0.8, "escanteios": 5.4, "cartoes": 2.7, "faltas": 14.9, "atuacao_comentario": "Campanha sólida na CONMEBOL. Jogo físico intenso aliado a meias de altíssima capacidade criativa."},
    # GRUPO L
    "Inglaterra": {"grupo": "L", "hist_ataque": 2.3, "hist_defesa": 0.8, "elim_ataque": 2.4, "elim_defesa": 0.7, "escanteios": 6.6, "cartoes": 1.4, "faltas": 11.2, "atuacao_comentario": "Sufocante. Domínio amplo do seu grupo europeu com elenco de altíssimo valor de mercado e repertório."},
    "Croácia": {"grupo": "L", "hist_ataque": 1.6, "hist_defesa": 1.0, "elim_ataque": 1.5, "elim_defesa": 0.9, "escanteios": 5.2, "cartoes": 1.8, "faltas": 12.1, "atuacao_comentario": "Meio-campo cerebral que controla o ritmo das partidas e dita a velocidade das ações de jogo."},
    "Gana": {"grupo": "L", "hist_ataque": 1.4, "hist_defesa": 1.4, "elim_ataque": 1.5, "elim_defesa": 1.2, "escanteios": 4.7, "cartoes": 2.3, "faltas": 14.8, "atuacao_comentario": "Transição ofensiva de alta velocidade e explosão, mas vulnerável se pressionada na saída."},
    "Panamá": {"grupo": "L", "hist_ataque": 1.1, "hist_defesa": 1.6, "elim_ataque": 1.4, "elim_defesa": 1.2, "escanteios": 4.0, "cartoes": 2.0, "faltas": 13.6, "atuacao_comentario": "Classificação muito madura na CONCACAF com forte base tática coletiva montada nos últimos anos."},
}


# ==============================================================================
# 3. MOTOR MATEMÁTICO QUANTITATIVO DE POISSON
# ==============================================================================
def calcular_poisson(lambda_gols, k):
    if lambda_gols <= 0:
        return 0.0
    return (math.exp(-lambda_gols) * (lambda_gols**k)) / math.factorial(k)


def realizar_analise_completa(m_time, v_time, banco_dados, media_gols_base, eh_copa=False):
    t_m = banco_dados[m_time]
    t_v = banco_dados[v_time]

    # CÁLCULO DOS LAMBDAS (Gols Esperados por Equipe)
    if not eh_copa:
        # Lógica Brasileirão: Força Base Multiplicativa + Mando de Campo + Forma Recente
        lambda_m = (t_m["ataque"] * FATOR_CASA_ATAQUE) * (t_v["defesa"] / media_gols_base) * t_m["forma"]
        lambda_v = (t_v["ataque"] * (t_m["defesa"] * FATOR_CASA_DEFESA) / media_gols_base) * t_v["forma"]
        base_ataque_m, base_ataque_v = t_m["ataque"], t_v["ataque"]
    else:
        # LÓGICA DA COPA: Ponderação Pura (30% Histórico Geral / 70% Eliminatórias Recentes)
        ataque_ponderado_m = (t_m["hist_ataque"] * 0.3) + (t_m["elim_ataque"] * 0.7)
        defesa_ponderado_m = (t_m["hist_defesa"] * 0.3) + (t_m["elim_defesa"] * 0.7)

        ataque_ponderado_v = (t_v["hist_ataque"] * 0.3) + (t_v["elim_ataque"] * 0.7)
        defesa_ponderado_v = (t_v["hist_defesa"] * 0.3) + (t_v["elim_defesa"] * 0.7)

        # Cruzamento direto das forças ponderadas calculadas (Campo Neutro)
        lambda_m = ataque_ponderado_m * (defesa_ponderado_v / media_gols_base)
        lambda_v = ataque_ponderado_v * (defesa_ponderado_m / media_gols_base)
        base_ataque_m, base_ataque_v = ataque_ponderado_m, ataque_ponderado_v

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

    # Identificar a Moda da Distribuição (Placar isolado de maior probabilidade)
    placar_index = matriz_gols.stack().idxmax()
    prob_placar_moda = matriz_gols.at[placar_index[0], placar_index[1]]

    # Conversão para Fair Odds Decimais
    odd_m = round(1 / prob_m, 2) if prob_m > 0 else 99.0
    odd_empate = round(1 / prob_empate, 2) if prob_empate > 0 else 99.0
    odd_v = round(1 / prob_v, 2) if prob_v > 0 else 99.0

    # Projeção de Scouts baseados no Ritmo de Jogo gerado pelos xG
    fator_ritmo = (lambda_m + lambda_v) / (base_ataque_m + base_ataque_v)
    escanteios_proj = (t_m["escanteios"] + t_v["escanteios"]) * fator_ritmo
    cartoes_proj = t_m["cartoes"] + t_v["cartoes"]
    
    # Cálculo Dinâmico de Faltas Esperadas
    faltas_proj = (t_m["faltas"] + t_v["faltas"]) * (fator_ritmo * 0.95)

    return {
        "prob_m": prob_m, "prob_empate": prob_empate, "prob_v": prob_v,
        "odd_m": odd_m, "odd_empate": odd_empate, "odd_v": odd_v,
        "placar_moda": f"{placar_index[0]} x {placar_index[1]}",
        "prob_placar": prob_placar_moda,
        "matriz": matriz_gols,
        "escanteios": round(escanteios_proj, 1),
        "cartoes": round(cartoes_proj, 1),
        "faltas": round(faltas_proj, 1),
        "gols_esperados_m": round(lambda_m, 2),
        "gols_esperados_v": round(lambda_v, 2)
    }


# ==============================================================================
# 4. INTERFACE GRÁFICA INTERATIVA (STREAMLIT DASHBOARD)
# ==============================================================================
st.title("📊 Plataforma de Inteligência Preditiva & Fair Odds")
st.markdown("Análise baseada em Cadeias de Poisson, Ajuste de Mando de Campo, Volume de Faltas e Peso de 70% para Eliminatórias Recentes.")

tab_br, tab_copa = st.tabs(["🇧🇷 Campeonato Brasileiro (Série A)", "🌍 Copa do Mundo 2026"])

# --- CONFIGURAÇÃO DA ABA BRASILEIRÃO ---
with tab_br:
    col1, col2 = st.columns(2)
    with col1:
        time_m = st.selectbox("Mandante (Casa)", sorted(list(DADOS_BRASILEIRAO.keys())), index=sorted(list(DADOS_BRASILEIRAO.keys())).index("Palmeiras"))
    with col2:
        time_v = st.selectbox("Visitante (Fora)", sorted(list(DADOS_BRASILEIRAO.keys())), index=sorted(list(DADOS_BRASILEIRAO.keys())).index("Flamengo"))

    if time_m == time_v:
        st.warning("Selecione equipes diferentes para o confronto do Brasileirão.")
    else:
        res = realizar_analise_completa(time_m, time_v, DADOS_BRASILEIRAO, MEDIA_GOLS_SÉRIE_A, eh_copa=False)
        
        # Grid Principal de Resultados
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

        # Scouts Alternativos (Agora incluindo Faltas)
        st.markdown("### 📈 Projeção Estatística de Over/Under")
        st.table({
            "Mercado de Estatísticas": ["Linha de Escanteios Totais", "Linha de Cartões Amarelos Totais", "Linha de Faltas Totais Cometidas"],
            "Projeção do Modelo Quant": [res["escanteios"], res["cartoes"], res["faltas"]]
        })

# --- CONFIGURAÇÃO DA ABA COPA DO MUNDO (TODAS AS 48 SELEÇÕES) ---
with tab_copa:
    col1, col2 = st.columns(2)
    with col1:
        # Agrupamento opcional visual por ordem alfabética de todas as 48 seleções
        lista_completa_copa = sorted(list(DADOS_COPA_PONDERADO.keys()))
        selec_m = st.selectbox("Seleção Mandante", lista_completa_copa, index=lista_completa_copa.index("Brasil"))
    with col2:
        selec_v = st.selectbox("Seleção Visitante", lista_completa_copa, index=lista_completa_copa.index("Panamá"))

    if selec_m == selec_v:
        st.warning("Selecione seleções diferentes para o confronto da Copa.")
    else:
        # Executa modelo aplicando a proporção de 70% nas eliminatórias recentes
        res_c = realizar_analise_completa(selec_m, selec_v, DADOS_COPA_PONDERADO, MEDIA_GOLS_FIFA, eh_copa=True)
        
        # Card Informativo de Análise de Desempenho Recente
        st.markdown("### 📝 Relatório de Atuação Recente (Peso de 70% nas Eliminatórias)")
        col_rep1, col_rep2 = st.columns(2)
        with col_rep1:
            st.info(f"**{selec_m} (Grupo {DADOS_COPA_PONDERADO[selec_m]['grupo']}):** {DADOS_COPA_PONDERADO[selec_m]['atuacao_comentario']}")
        with col_rep2:
            st.info(f"**{selec_v} (Grupo {DADOS_COPA_PONDERADO[selec_v]['grupo']}):** {DADOS_COPA_PONDERADO[selec_v]['atuacao_comentario']}")
            
        st.markdown("---")

        cm_mod, cm_xg1, cm_xg2 = st.columns(3)
        cm_mod.metric("Placar Isolado Mais Provável", res_c["placar_moda"], f"{round(res_c['prob_placar']*100, 1)}% de chance")
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
        
        # Tabela contendo a nova linha de faltas da Copa
        st.markdown("### 📈 Projeção de Scouts")
        st.table({
            "Mercado de Estatísticas": ["Linha de Escanteios Totais", "Linha de Cartões Amarelos Totais", "Linha de Faltas Totais Cometidas"],
            "Projeção do Modelo Quant": [res_c["escanteios"], res_c["cartoes"], res_c["faltas"]]
        })
