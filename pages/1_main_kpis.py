# pages/1_main_kpis.py — Visão Geral (KPIs + tendências)
# -------------------------------------------------------
# O que este arquivo faz:
# 1) Carrega o dataset processado (via utils.pre_process.load_processed)
# 2) Exibe uma amostra da base
# 3) Mostra KPIs:
#    - Sales líquida total (se existir 'total_net_sales')
#    - Profit total
#    - Total Cost
#    - Contagem de países únicos
#    - Contagem de categorias únicas
#    - Contagem de produtos únicos
# 4) Gráfico de linhas com tendência mensal de total_gross_sales e profit

import streamlit as st
import plotly.express as px
from utils.pre_process import load_processed
from utils.lateral_filters import sidebar_filters

# OPCIONAL (apenas se você executar esta página isolada no VS Code):
# from utils.bootstrap import add_root_relative_to
# add_root_relative_to(__file__, up=1)

@st.cache_data(show_spinner=False)
def get_df():
    # tenta pegar o caminho salvo pelo main.py; se não existir, usa o default
    from pathlib import Path
    paths = st.session_state.get("PATHS", {})
    processed = paths.get(
        "PROCESSED_PATH",
        str(Path(__file__).resolve().parents[1] / "data" / "processed" / "processed.csv")
    )
    return load_processed(processed)

def _first_existing(df, candidates):
    """Retorna o primeiro nome de coluna que existir no df dentre os candidatos."""
    for c in candidates:
        if c in df.columns:
            return c
    return None

def main(df=None):
    # 1) Carrega dados (se o main.py não injetou df)
    if df is None:
        df = get_df()
        
    # <- aplica filtros da barra lateral
    df = sidebar_filters(df)

    st.title("Visão Geral")

    # 2) Espelho rápido da base
    # st.caption("Amostra dos dados processados")
    # st.dataframe(df.head(), use_container_width=True)

    # 3) KPIs principais
    # 3.1 KPIs de contagem (países, categorias, produtos)
    # Colunas mais comuns após snake_case no Superstore:
    # city, category, product_name
    city_col = _first_existing(df, ["city"])
    category_col = _first_existing(df, ["category"])
    product_col = _first_existing(df, ["product_name", "product"])
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        if "total_net_sales" in df.columns:
            st.metric("Sales Líquida Total (R$)", f"{df['total_net_sales'].sum():,.2f}")
    with col2:
        if "profit" in df.columns:
            st.metric("Profit (total R$)", f"{df['profit'].sum():,.2f}")
    with col3:
        if "total_cost" in df.columns:
            st.metric("Total Cost", f"{df['total_cost'].sum():,.2f}")
    with col4:
        if city_col:
            st.metric("Países únicos", f"{df[city_col].nunique():,}")
    with col5:
        if category_col:
            st.metric("Categorias únicas", f"{df[category_col].nunique():,}")
    with col6:
        if product_col:
            st.metric("Produtos únicos", f"{df[product_col].nunique():,}")

    st.divider()

    # 4) Tendência mensal: total_gross_sale e profit no mesmo gráfico
    # Requisitos: 'month_year' (YYYY-MM), 'total_gross_sale' e 'profit'
    # Observação: se alguma coluna não existir, mostramos uma mensagem amigável.
    needed_cols = ["month_year", "total_gross_sale", "profit"]
    if all(column in df.columns for column in needed_cols):
        # agregação por mês/ano
        g = df.groupby("month_year", as_index=False)[["total_gross_sale", "profit"]].sum()

        # gráfico em "wide-form": duas séries no mesmo eixo Y
        fig = px.line(
            g,
            x="month_year",
            y=["total_gross_sale", "profit"],
            markers=True,
            title="Tendência mensal: Vendas Brutas (total_gross_sale) vs Profit"
        )
        fig.update_layout(legend_title_text="Métrica")
        st.plotly_chart(fig, use_container_width=True)
    else:
        missing = [c for c in needed_cols if c not in df.columns]
        st.info(
            "Para exibir a tendência mensal de vendas brutas e receita, "
            "o dataset precisa conter as colunas: "
            f"`month_year`, `total_gross_sale`, `profit`. "
            f"Faltando: {', '.join(missing)}"
        )

# Quando chamada via st.Page/st.navigation, o Streamlit executa o script;
# para garantir a renderização, chame main() aqui também.
main()
