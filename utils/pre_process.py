# utils/pre_process.py — pré-processamento (sem Discount/Gross Sale) + month_year + snake_case
# -------------------------------------------------------------------------------------------
# O que este módulo faz:
# - Lê o CSV bruto com tolerância de encoding
# - Converte TODOS os nomes de colunas para snake_case (minúsculas, _)
# - Faz parse de datas (order_date e ship_date, se existirem)
# - Cria:
#     * month_year = mês/ano (YYYY-MM) a partir de order_date
# - Remove linhas com dados faltantes (df.dropna())
# - Salva o CSV processado (processed.csv)
# - Expõe helpers cacheados para o app
import streamlit as st
import pandas as pd
import numpy as np
import re
from pathlib import Path


# ---------------------------
# Utilidades internas
# ---------------------------
def _read_csv_robusto(path):
    """Lê CSV tentando encodings comuns (utf-8, latin1, cp1252)."""
    p = Path(path)
    for enc in ("utf-8", "latin1", "cp1252"):
        try:
            return pd.read_csv(p, encoding=enc)
        except Exception:
            continue
    return pd.read_csv(p)

def _to_snake_case(name):
    """Converte um nome de coluna para snake_case (minúsculas com underscore)."""
    s = str(name).strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)       # remove chars não alfanum/underscore/hífen/espaço
    s = s.replace("-", " ").replace(".", " ")
    s = re.sub(r"\s+", "_", s)           # espaços consecutivos -> "_"
    s = re.sub(r"_+", "_", s)            # múltiplos "_" -> um só
    return s.strip("_")


# ---------------------------
# Pipeline principal
# ---------------------------
def load_and_prepare(raw_path, processed_path=None):
    """
    Lê o CSV bruto e aplica transformações essenciais:
      1) Renomeia colunas para snake_case
      2) Parse de datas: order_date / ship_date (se existirem)
      3) total_cost = sales - profit
      4) month_year = YYYY-MM derivado de order_date
      5) Remove linhas com qualquer dado faltante
      6) (Opcional) salva em processed_path
    """
    df = _read_csv_robusto(raw_path)

    # 1) Colunas em snake_case
    df.columns = [_to_snake_case(c) for c in df.columns]

    # 2) Parse de datas (se existirem)
    for col in ("order_date", "ship_date"):
        if col in df.columns:
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass

    # 3) Cria a coluna month_year
    df["month_year"] = df["order_date"].dt.to_period("M").astype(str)


    # 4) Remover linhas com QUALQUER dado faltante
    antes = len(df)
    df = df.dropna().reset_index(drop=True)
    removidas = antes - len(df)
    if removidas > 0:
        try:
            st.info(f"Linhas removidas por dados faltantes: {removidas} (de {antes})")
        except Exception:
            pass  # fora do Streamlit, apenas ignore

    # 5) Salvar processado (opcional)
    if processed_path:
        try:
            Path(processed_path).parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(processed_path, index=False)
        except Exception:
            pass

    return df


@st.cache_data(show_spinner="Preparando dados...")
def run_preprocessing(raw_path, processed_path):
    """
    Wrapper cacheado que lê e processa o RAW e garante o processed.csv em disco.
    """
    raw_path = Path(raw_path)
    processed_path = Path(processed_path)

    if not raw_path.exists():
        raise FileNotFoundError("RAW não encontrado: {}".format(raw_path))

    df = load_and_prepare(str(raw_path), str(processed_path))
    try:
        df.to_csv(processed_path, index=False)
    except Exception:
        pass
    return df


@st.cache_data(show_spinner=False)
def load_processed(processed_path):
    """Lê o CSV processado (para uso nas páginas)."""
    return _read_csv_robusto(processed_path)
