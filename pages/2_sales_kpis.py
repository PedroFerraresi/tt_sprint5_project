# pages/2_sales_kpis.py — Vendas • Descontos • Custos
import streamlit as st
import plotly.express as px
import pandas as pd

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

    st.title("Vendas • Descontos • Custos")
    st.dataframe(df.head(), use_container_width=True)

    df = sidebar_filters(df)

    sales_col = first_existing(df, ["total_net_sales", "sales"])
    profit_col = first_existing(df, ["profit"])
    cost_col = first_existing(df, ["total_cost"])
    gross_col = first_existing(df, ["total_gross_sales"])
    orders_col = first_existing(df, ["order_id"])
    quantity_col = first_existing(df, ["quantity"])
    discount_col = first_existing(df, ["discount"])

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        if orders_col:
            st.metric("Pedidos (total)", f"{df[sales_col].nunique()}")
    with col2:
        if sales_col:
            st.metric("Vendas Líquidas Totais (R$)", f"{df[sales_col].sum():,.2f}")
    with col3:
        if cost_col:
            st.metric("Custo Total (R$)", f"{df[cost_col].sum():,.2f}")
    with col4:
        if profit_col:
            st.metric("Receita Total (R$)", f"{df[profit_col].sum():,.2f}")
    with col5:
        if quantity_col:
            st.metric("Quantidade Total de Produtos (unidades)", f"{df[quantity_col].sum()}")
    with col6:
        if discount_col:
            st.metric("Receita Total (R$)", f"{df[discount_col].mean() * 100:,.2f}")

    st.divider()

    if "month_year" in df.columns:
        series = []
        if gross_col: series.append(gross_col)
        if sales_col: series.append(sales_col)
        if profit_col: series.append(profit_col)
        if series:
            g = df.groupby("month_year", as_index=False)[series].sum()
            fig = px.line(g, x="month_year", y=series, markers=True,
                          title="Tendência mensal: Vendas Brutas / Vendas / Profit")
            fig.update_layout(legend_title_text="Métrica")
            st.plotly_chart(fig, use_container_width=True)

    st.divider()

    cat_col = first_existing(df, ["category"])
    if cat_col and sales_col and profit_col:
        g = df.groupby(cat_col, as_index=False)[[sales_col, profit_col]].sum().sort_values(sales_col, ascending=False)
        fig = px.bar(g, x=cat_col, y=[sales_col, profit_col], barmode="group", title="Vendas e Profit por Categoria")
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    seg_col = first_existing(df, ["segment"])
    disc_col = first_existing(df, ["discount"])
    if sales_col and profit_col:
        hover = [c for c in ["product_name", "sub_category", "category"] if c in df.columns]
        fig = px.scatter(df, x=profit_col, y=sales_col, color=seg_col if seg_col else None,
                         size=disc_col if disc_col else None, hover_data=hover,
                         title="Dispersão: Vendas vs Profit (cor=Segmento, tam=Discount)")
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    if disc_col:
        st.plotly_chart(px.histogram(df, x=disc_col, nbins=40, title="Distribuição de Discount"),
                        use_container_width=True)
    if cost_col:
        st.plotly_chart(px.histogram(df, x=cost_col, nbins=40, title="Distribuição de Total Cost"),
                        use_container_width=True)

    if profit_col:
        losses = df[df[profit_col] < 0].copy()
        if not losses.empty:
            cols_show = [c for c in ["order_id", "product_name", "sub_category", "category",
                                     sales_col, profit_col, cost_col, disc_col] if c and c in losses.columns]
            losses = losses.sort_values(profit_col, ascending=True).head(20)
            st.subheader("Top prejuízos (20)")
            st.dataframe(losses[cols_show], use_container_width=True)

main()
