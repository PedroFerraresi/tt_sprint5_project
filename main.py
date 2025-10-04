# main.py — Streamlit 1.50.0 (versão essencial + utils, com bootstrap centralizado)
# ---------------------------------------------------------------------------
# 1) Bootstrap de imports (via utils/bootstrap.py)
# 2) Lê RAW, pré-processa e salva processed.csv (usando utils)
# 3) Monta navegação (utils) e roda a página principal

from pathlib import Path
from utils.bootstrap import add_root

# adiciona a raiz do projeto ao sys.path
PROJECT_ROOT = add_root(Path(__file__).resolve().parent)

import streamlit as st
from utils.app_paths import get_paths, ensure_dirs
from utils.pre_process import run_preprocessing
from utils.navigation import build_navigation

st.set_page_config(
    page_title="Superstore Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

with st.sidebar:
    st.markdown("### 📊 Superstore Dashboard")
    st.caption("Streamlit 1.50.0")

def main():
    # caminhos padrão do projeto (data/raw, data/processed, etc.)
    paths = get_paths(PROJECT_ROOT)
    ensure_dirs(paths)

    # pré-processamento (gera processed.csv; cacheado em utils/pre_process.py)
    try:
        _ = run_preprocessing(paths["RAW_PATH"], paths["PROCESSED_PATH"])
    except Exception as e:
        st.exception(e)
        st.stop()

    # navegação programática (st.Page / st.navigation)
    nav = build_navigation(PROJECT_ROOT)

    # compartilha caminhos com as páginas
    st.session_state.setdefault("PATHS", {
        "RAW_PATH": str(paths["RAW_PATH"]),
        "PROCESSED_PATH": str(paths["PROCESSED_PATH"]),
    })

    nav.run()

if __name__ == "__main__":
    main()
