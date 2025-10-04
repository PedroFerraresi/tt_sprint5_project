# pages/2_sales_kpis.py — Vendas • Descontos • Custos
# ---------------------------------------------------
# O que esta página faz:
# 1) Carrega o dataset processado (processed.csv)
# 2) Aplica filtros da barra lateral (utils.lateral_filters.sidebar_filters)
# 3) Mostra KPIs de Vendas/Profit/Custo (e Gross, se existir)
# 4) Exibe gráficos: tendências mensais, barras por categoria, scatter Sales vs Profit,
#    distribuição de Discount (se existir) e distribuição de Total Cost
#
# OBS: Se você renomeou este arquivo para "2_sales_kpis.py", lembre de atualizar
#      utils/navigation.py para apontar para este caminho numerado.

import streamlit as st
import plotly.express as px
import pandas as pd

from utils.pre_process import load_processed
from utils.lateral_filters import sidebar_filters

# OPCIONAL (apenas se você executar esta página isolada no VS Code):
# from utils.bootstrap import add_root_relative_to
# add_root_relative_to(__file__, up=1)

# ------------------------------
# Helpers locais
# ------------------------------
def _first_existing(df, candidates):
    """Retorna o primeiro nome de coluna que existir no df dentre os candidatos."""
    for c in candidates:
        if c in df.columns:
            return c
    return None

@st.cache_data(show_spinner=False)
def get_df():
    """Lê o processed.csv salvo pelo main.py."""
    from pathlib import Path
    paths = st.session_state.get("PATHS", {})
    processed = paths.get(
        "PROCESSED_PATH",
        str(Path(__file__).resolve().parents[1] / "data" / "processed" / "processed.csv")
    )
    return load_processed(processed)

# ------------------------------
# Página
# ------------------------------
def main(df=None):
    # 1) Carregar dados (caso o main não tenha injetado df)
    if df is None:
        df = get_df()

    st.title("Vendas • Descontos • Custos")

    # 2) Filtros laterais (período como slider + dimensões + faixas numéricas)
    df = sidebar_filters(df)
    
    # st.caption("Amostra dos dados processados")
    # st.dataframe(df.head(), use_container_width=True)

    # 3) KPIs principais
    #    Considera nomes alternativos para Vendas: "total_net_sales" OU "sales"
    sales_col = _first_existing(df, ["total_net_sales", "sales"])
    profit_col = _first_existing(df, ["profit"])
    quantity_col = _first_existing(df, ["quantity"])
    cost_col = _first_existing(df, ["total_cost"])
    discount_col = _first_existing(df, ["discount"])
    gross_col = _first_existing(df, ["total_gross_sale"])  # opcional, se existir

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        if sales_col:
            st.metric("Vendas Totais (R$)", f"{df[sales_col].sum():,.2f}")
    with c2:
        if quantity_col:
            st.metric("Quantidade Totais (unidades)", f"{df[quantity_col].sum():,.2f}")
    with c3:
        if cost_col:
            st.metric("Custos Totais (R$)", f"{df[cost_col].sum():,.2f}")
    with c4:
        if gross_col:
            st.metric("Vendas Brutas Total (R$)", f"{df[gross_col].sum():,.2f}")
    with c5:
        if profit_col:
            st.metric("Receita Total (R$)", f"{df[profit_col].sum():,.2f}")
    with c6:
        if discount_col:
            st.metric("Desconto médio (%)", f"{df[discount_col].mean() * 100:,.2f}")

    st.divider()

    # 4) Tendência mensal de Vendas/Profit (e Gross, se existir)
    #    Requer: month_year + colunas numéricas
    if "month_year" in df.columns:
        series = []
        if gross_col: series.append(gross_col)
        if sales_col: series.append(sales_col)
        if profit_col: series.append(profit_col)

        if series:
            g = df.groupby("month_year", as_index=False)[series].sum()
            fig = px.line(
                g,
                x="month_year",
                y=series,
                markers=True,
                title="Tendência mensal: Vendas Brutas / Vendas / Profit"
            )
            fig.update_layout(legend_title_text="Métrica")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Não há colunas numéricas de vendas/lucro para a tendência mensal.")
    else:
        st.info("Coluna 'month_year' não encontrada — tendência mensal não pode ser exibida.")

    st.divider()

    # 5) Barras por Categoria (comparando Sales x Profit)
    cat_col = _first_existing(df, ["category"])
    if cat_col and sales_col and profit_col:
        g = df.groupby(cat_col, as_index=False)[[sales_col, profit_col]].sum()
        g = g.sort_values(sales_col, ascending=False)
        fig = px.bar(
            g, x=cat_col, y=[sales_col, profit_col],
            barmode="group",
            title="Vendas e Profit por Categoria"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Para barras por categoria, são necessárias as colunas 'category', vendas e profit.")

    st.divider()

    # 6) Scatter: Sales vs Profit (cor por Segment, tamanho por Discount se existir)
    seg_col = _first_existing(df, ["segment"])
    disc_col = _first_existing(df, ["discount"])
    if sales_col and profit_col:
        hover = []
        for c in ["product_name", "sub_category", "category"]:
            if c in df.columns:
                hover.append(c)
        fig = px.scatter(
            df, 
            x=profit_col, 
            y=sales_col,
            color=seg_col if seg_col else None,
            size=disc_col if disc_col else None,
            hover_data=hover,
            title="Dispersão: Vendas vs Profit (cor=Segmento, tamanho=Discount)"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Para o scatter, verifique se as colunas de Vendas e Profit existem.")

    st.divider()

    # 7) Distribuição de Discount (se existir)
    if disc_col:
        fig = px.histogram(
            df, x=disc_col, nbins=40,
            title="Distribuição de Discount"
        )
        st.plotly_chart(fig, use_container_width=True)

    # 8) Distribuição de Total Cost
    if cost_col:
        fig = px.histogram(
            df, x=cost_col, nbins=40,
            title="Distribuição de Total Cost"
        )
        st.plotly_chart(fig, use_container_width=True)

    # 9) Ranking de prejuízos (linhas com Profit < 0)
    if profit_col:
        losses = df[df[profit_col] < 0].copy()
        if not losses.empty:
            # Escolhe algumas colunas úteis se existirem
            cols_show = [c for c in ["order_id", "product_name", "sub_category", "category",
                                     sales_col, profit_col, cost_col, disc_col] if c and c in losses.columns]
            losses = losses.sort_values(profit_col, ascending=True).head(20)
            st.subheader("Top prejuízos (20)")
            st.dataframe(losses[cols_show], use_container_width=True)
        else:
            st.caption("Nenhuma linha com prejuízo encontrada nos filtros atuais.")

# Executa a página quando chamada via st.Page/st.navigation ou diretamente
main()
