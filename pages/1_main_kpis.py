# pages/1_main_kpis.py — Visão Geral (KPIs + tendências)
import streamlit as st
import plotly.express as px
from utils.pre_process import load_processed
from utils.lateral_filters import sidebar_filters
from utils.aux_functions import first_existing  # <- helper centralizado

@st.cache_data(show_spinner=False)
def get_df():
    from pathlib import Path
    paths = st.session_state.get("PATHS", {})
    processed = paths.get(
        "PROCESSED_PATH",
        str(Path(__file__).resolve().parents[1] / "data" / "processed" / "processed.csv")
    )
    return load_processed(processed)

def main(df=None):
    if df is None:
        df = get_df()

    # aplica filtros da barra lateral antes dos KPIs/gráficos
    df = sidebar_filters(df)

    st.title("Visão Geral")
    # st.dataframe(df.head(), use_container_width=True)

    # KPIs principais
    # KPIs de contagem
    cities_col = first_existing(df, ["city"])
    category_col = first_existing(df, ["category"])
    product_col = first_existing(df, ["product_name", "product"])
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    sales_col = first_existing(df, ["total_net_sales", "sales"])
    with col1:
        if sales_col:
            st.metric("Vendas Totais (R$)", f"{df[sales_col].sum():,.2f}")
    with col2:
        if "total_cost" in df.columns:
            st.metric("Custo Total (R$)", f"{df['total_cost'].sum():,.2f}")
    with col3:
        if "profit" in df.columns:
            st.metric("Receita Total (R$)", f"{df['profit'].sum():,.2f}")
    with col4:
        if cities_col:
            st.metric("Países únicos", f"{df[cities_col].nunique():,}")
    with col5:
        if category_col:
            st.metric("Categorias únicas", f"{df[category_col].nunique():,}")
    with col6:
        if product_col:
            st.metric("Produtos únicos", f"{df[product_col].nunique():,}")

    st.divider()

    # Tendência: total_gross_sales e profit
    if "month_year" in df.columns and "profit" in df.columns:
        series = []
        if "total_gross_sales" in df.columns:
            series.append("total_gross_sales")
        series.append("profit")
        if series:
            dfg = df.groupby("month_year", as_index=False)[series].sum()
            fig = px.line(dfg, x="month_year", y=series, markers=True,
                          title="Tendência mensal: Vendas Brutas vs Profit")
            fig.update_layout(legend_title_text="Métrica")
            st.plotly_chart(fig, use_container_width=True)

# execução
main()
