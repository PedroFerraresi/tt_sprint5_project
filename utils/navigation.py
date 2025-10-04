# utils/navigation.py — configuração de páginas (Streamlit 1.50.0)
# Corrigido: usar argumento posicional no st.Page (sem 'path=')

import streamlit as st
from pathlib import Path

def build_navigation(project_root):
    pages_dir = Path(project_root) / "pages"

    home = st.Page(
        str(pages_dir / "1_main_kpis.py"),   # <- caminho como 1º argumento posicional
        title="Visão Geral",
        icon="🏠",
        default=True,
    )
    sales = st.Page(
        str(pages_dir / "2_sales_kpis.py"),
        title="Vendas • Descontos • Custos",
        icon="💸",
    )
    clients = st.Page(
        str(pages_dir / "3_clients_kpis.py"),
        title="Clientes • Geografia",
        icon="🗺️",
    )
    products = st.Page(
        str(pages_dir / "4_products_kpis.py"),
        title="Produtos (ABC / Pareto)",
        icon="📦",
    )
    data_dict = st.Page(
        str(pages_dir / "5_data_dict.py"),
        title="Dicionário de Dados",
        icon="📚",
    )

    nav = st.navigation({
        "Dashboard": [home, sales, clients, products],
        "Ajuda": [data_dict],
    })
    return nav
