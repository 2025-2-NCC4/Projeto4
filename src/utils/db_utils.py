# =============================================================================
# MÓDULO DE UTILIDADES PARA PROCESSAMENTO DE DADOS
# =============================================================================

# Importação das bibliotecas necessárias
import pandas as pd  # Para manipulação de dados tabulares
import numpy as np   # Para operações numéricas e valores ausentes

# Definição dos caminhos dos arquivos CSV
# Cada arquivo contém um conjunto específico de dados do sistema
path_massa = "data/lojas_valores.csv"        # Dados das lojas e valores
path_pedestres = "data/pedestres_paulista.csv"  # Dados de fluxo de pedestres
path_trans = "data/transacoes_cupons.csv"    # Dados de transações de cupons
path_players = "data/base_players.csv"       # Dados dos usuários do sistema

# Carregamento dos arquivos CSV
# Utilizamos parâmetros flexíveis para garantir a leitura correta:
# - sep=None: Detecta automaticamente o separador
# - engine="python": Usa o engine mais flexível do pandas
# - encoding="utf-8": Garante suporte a caracteres especiais
# - on_bad_lines='skip': Ignora linhas com problemas de formatação
df_massa = pd.read_csv(path_massa, sep=None, engine="python", encoding="utf-8", on_bad_lines='skip')
df_pedestres = pd.read_csv(path_pedestres, sep=None, engine="python", encoding="utf-8", on_bad_lines='skip')
df_trans = pd.read_csv(path_trans, sep=None, engine="python", encoding="utf-8", on_bad_lines='skip')
df_players = pd.read_csv(path_players, sep=None, engine="python", encoding="utf-8", on_bad_lines='skip')

# =============================================================================
# FUNÇÕES DE NORMALIZAÇÃO DE DADOS
# =============================================================================

def norm_cel(s):
    """
    Normaliza números de celular removendo caracteres não numéricos.
    
    Args:
        s: String contendo o número de celular
        
    Returns:
        String contendo apenas os dígitos do número
    """
    if pd.isna(s): return s  # Retorna como está se for valor ausente
    return ''.join(ch for ch in str(s) if ch.isdigit())

# Padronização dos números de celular em todos os datasets
# Isso é necessário para permitir o cruzamento correto dos dados entre as tabelas
for df in [df_massa, df_pedestres, df_trans, df_players]:
    # Alguns datasets usam 'numero_celular', outros usam 'celular'
    # Padronizamos para usar sempre 'celular'
    if "numero_celular" in df.columns:
        df["celular"] = df["numero_celular"].astype(str).apply(norm_cel)
    if "celular" in df.columns:
        df["celular"] = df["celular"].astype(str).apply(norm_cel)

# Padronização dos campos de data
# Convertemos todas as datas para o formato datetime do pandas
# - dayfirst=True: Assume formato brasileiro (dia/mês/ano)
# - errors="coerce": Converte valores inválidos para NaT (Not a Time)
if "data_captura" in df_massa.columns:
    df_massa["data_captura"] = pd.to_datetime(df_massa["data_captura"], dayfirst=True, errors="coerce")
if "data" in df_pedestres.columns:
    df_pedestres["data"] = pd.to_datetime(df_pedestres["data"], dayfirst=True, errors="coerce")
if "data" in df_trans.columns:
    df_trans["data"] = pd.to_datetime(df_trans["data"], dayfirst=True, errors="coerce")
if "data_nascimento" in df_players.columns:
    df_players["data_nascimento"] = pd.to_datetime(df_players["data_nascimento"], dayfirst=True, errors="coerce")

# Hora: criar coluna datetime quando possível
for df, date_col, time_col in [
    (df_trans, "data", "hora"),
    (df_pedestres, "data", "horario"),
]:
    if date_col in df.columns and time_col in df.columns:
        df[time_col] = df[time_col].astype(str).str.zfill(4)  # tentativa
        df["datetime"] = pd.to_datetime(df[date_col].dt.date.astype(str) + " " + df[time_col].astype(str), errors="coerce")

# Converter colunas de valor para numérico (trocar vírgula por ponto se houver)
# def money_to_float(s):
#     if pd.isna(s): return np.nan
#     t = str(s).replace(".", "").replace(",", ".")
#     # remover símbolos não numéricos exceto ponto e minus
#     t = ''.join(ch for ch in t if ch.isdigit() or ch == "." or ch == "-")
#     try:
#         return float(t)
#     except:
#         return np.nan
#
# # colunas possíveis
# for col in ["valor_compra", "valor_cupom", "ultimo_valor_capturado", "repasse_picmoney"]:
#     for df in [df_massa, df_trans, df_pedestres]:
#         if col in df.columns:
#             df[col] = df[col].apply(money_to_float)

# idade: se houver em players ou pedestres, garantir numérico
for df in [df_players, df_pedestres]:
    if "idade" in df.columns:
        df["idade"] = pd.to_numeric(df["idade"], errors="coerce")

# faixa etária (bins)
bins = [0, 17, 24, 34, 44, 54, 64, 200]
labels = ["<=17","18-24","25-34","35-44","45-54","55-64","65+"]
if "idade" in df_players.columns:
    df_players["faixa_etaria"] = pd.cut(df_players["idade"], bins=bins, labels=labels, right=True)

# weekday / hour helpers
for df, date_col in [(df_trans, "data"), (df_massa, "data_captura"), (df_pedestres, "data")]:
    if date_col in df.columns:
        df["weekday"] = df[date_col].dt.day_name()
for df, time_col in [(df_trans, "hora"), (df_pedestres, "horario")]:
    if time_col in df.columns:
        # extrair hora (se formato HHMM ou HH:MM)
        def extract_hour(x):
            try:
                s = str(x)
                if ":" in s:
                    return int(s.split(":")[0])
                s = s.zfill(4)
                return int(s[:2])
            except:
                return np.nan
        df["hour"] = df[time_col].apply(extract_hour)

# ready: df_massa, df_pedestres, df_trans, df_players
#print("Pré-processamento concluído.")
#print("Registros: massa={}, pedestres={}, trans={}, players={}".format(
#    len(df_massa), len(df_pedestres), len(df_trans), len(df_players)
#))
