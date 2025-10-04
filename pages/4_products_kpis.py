# pages/4_products_kpis.py — Produtos (ABC / Pareto) + Cohort (clientes)
# -------------------------------------------------------------------------------
import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

from utils.pre_process import load_processed
from utils.lateral_filters import sidebar_filters
from utils.aux_functions import (
    first_existing,
    build_pareto_full,
    abc_class,
    ensure_month_col,
    build_customer_cohort_count,
)

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

    st.title("Produtos (ABC / Pareto) + Cohort (clientes)")

    # Filtros laterais
    df = sidebar_filters(df)

    # Colunas relevantes
    sales_col = first_existing(df, ["total_net_sales", "sales"])
    profit_col = first_existing(df, ["profit"])
    cost_col = first_existing(df, ["total_cost"])
    qty_col = first_existing(df, ["quantity"])
    cat_col = first_existing(df, ["category"])
    subcat_col = first_existing(df, ["sub_category"])
    prod_col = first_existing(df, ["product_name", "product"])
    segment_col = first_existing(df, ["segment"])
    customer_col = first_existing(df, ["customer_name", "customer_id", "customer"])

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Produtos únicos", f"{df[prod_col].nunique():,}" if prod_col else "—")
    with c2: 
        if sales_col: st.metric("Vendas (total)", f"{df[sales_col].sum():,.2f}")
    with c3: 
        if profit_col: st.metric("Profit (total)", f"{df[profit_col].sum():,.2f}")
    with c4: 
        if qty_col: st.metric("Qtd. total vendida", f"{df[qty_col].sum():,}")

    st.divider()

    # Barras empilhadas por segmento (3 gráficos)
    if segment_col and cat_col and subcat_col and sales_col:
        segs = df[segment_col].dropna().unique().tolist()
        segs = sorted(segs)
        if len(segs) == 0:
            st.info("Nenhum segmento encontrado após os filtros.")
        else:
            cols = st.columns(min(3, len(segs)))
            for i, seg in enumerate(segs):
                sub = df[df[segment_col] == seg]
                if sub.empty:
                    continue
                t = (
                    sub.groupby([cat_col, subcat_col], as_index=False)[[c for c in [sales_col, profit_col] if c]].sum()
                    .sort_values(sales_col, ascending=False)
                )
                with cols[i % 3]:
                    fig = px.bar(
                        t,
                        x=cat_col,
                        y=sales_col,
                        color=subcat_col,
                        barmode="stack",
                        title=f"Vendas por Categoria (empilhado por Sub-Category) — {seg}",
                        hover_data=[profit_col] if profit_col else None
                    )
                    fig.update_layout(legend_title_text="Sub-Category")
                    st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Para as barras empilhadas por segmento, verifique se existem 'segment', 'category', 'sub_category' e 'sales'.")

    st.divider()

    # Pareto (ABC) — slider com TODOS + filtro de grupos
    if prod_col and sales_col:
        pareto_full, sales_total = build_pareto_full(df, sales_col, prod_col)
        if sales_total == 0 or pareto_full.empty:
            st.caption("Sem dados suficientes para o Pareto de produtos.")
        else:
            pareto_full["abc"] = pareto_full["cum_share"].apply(abc_class)
            n_products = pareto_full.shape[0]
            default_n = min(30, n_products)
            top_n = st.slider(
                "Exibir Top-N produtos por Vendas (ordem decrescente)",
                min_value=1,
                max_value=int(n_products),
                value=int(default_n),
                step=1
            )
            group_sel = st.multiselect(
                "Grupos ABC a exibir",
                options=["A", "B", "C"],
                default=["A", "B", "C"],
                help="Selecione as classes que deseja visualizar no gráfico e na tabela."
            )
            pareto_view = pareto_full.head(top_n).copy()
            if group_sel:
                pareto_view = pareto_view[pareto_view["abc"].isin(group_sel)]

            fig = px.bar(
                pareto_view,
                x=prod_col,
                y=sales_col,
                color="abc",
                title=f"Pareto de Produtos por Vendas — Top {top_n} (ABC)",
                color_discrete_map={"A": "#1f77b4", "B": "#ff7f0e", "C": "#2ca02c"},
            )
            fig.add_scatter(
                x=pareto_view[prod_col],
                y=(pareto_view["cum_share"] * 100.0),
                mode="lines+markers",
                name="Cumulativo (%)",
                yaxis="y2"
            )
            fig.update_layout(
                yaxis=dict(title="Vendas"),
                yaxis2=dict(title="Cumulativo (%)", overlaying="y", side="right", range=[0, 100]),
                legend_title_text="Classe ABC"
            )
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("Tabela (com classificação ABC)")
            tmp = pareto_view.copy()
            tmp["share"] = (tmp["share"] * 100).round(2)
            tmp["cum_share"] = (tmp["cum_share"] * 100).round(2)
            st.dataframe(tmp[[prod_col, sales_col, "share", "cum_share", "abc"]], use_container_width=True)
    else:
        st.info("Para o Pareto de produtos, verifique se existem 'product_name'/'product' e 'sales'.")

    st.divider()

    # Rankings por Profit
    if prod_col and profit_col:
        top_k = st.slider("Top-N ranking por Profit", min_value=5, max_value=50, value=20, step=5)
        agg = df.groupby(prod_col, as_index=False)[profit_col].sum()
        gains = agg.sort_values(profit_col, ascending=False).head(top_k)
        if not gains.empty:
            st.plotly_chart(px.bar(gains, x=prod_col, y=profit_col, title=f"Top {top_k} Produtos por Profit"),
                            use_container_width=True)
        losses = agg.sort_values(profit_col, ascending=True).head(top_k)
        if not losses.empty:
            st.plotly_chart(px.bar(losses, x=prod_col, y=profit_col, title=f"Maiores Prejuízos por Produto (Top {top_k})"),
                            use_container_width=True)

    st.divider()

    # Cohort (APENAS CONTAGEM)
    st.subheader("Cohort de clientes (contagem)")
    if not customer_col:
        st.info("Para a análise de cohort é necessário ter uma coluna de cliente (ex.: 'customer_name' ou 'customer_id').")
        return

    base = ensure_month_col(df)
    if "order_month" not in base.columns or base["order_month"].isna().all():
        st.info("Não foi possível determinar o mês de pedido para construir a coorte (faltam 'order_date' ou 'month_year').")
        return

    normalize = st.checkbox("Exibir como % da coorte (normalizado por linha)", value=True)

    pivot, cohort_sizes = build_customer_cohort_count(
        base, customer_col=customer_col, date_col_month="order_month"
    )

    if pivot.empty:
        st.caption("Sem dados suficientes para construir a coorte com os filtros selecionados.")
        return

    to_show = pivot.copy()
    if normalize:
        denom = to_show[0].replace({0: np.nan})
        to_show = (to_show.T / denom).T * 100.0
        colorbar_title = "%"
        title_suffix = " (normalizado)"
        text_fmt = ".1f"
    else:
        colorbar_title = "Clientes"
        title_suffix = ""
        text_fmt = ".0f"

    to_show = to_show.sort_index()

    fig = px.imshow(
        to_show,
        labels=dict(x="Meses desde a coorte", y="Mês da coorte", color=colorbar_title),
        text_auto=text_fmt,
        aspect="auto",
        title=f"Cohort por mês de 1ª compra — Clientes (contagem){title_suffix}"
    )
    fig.update_xaxes(type="category")
    fig.update_layout(height=900)
    fig.update_traces(textfont_size=12)
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Ver tabela da coorte"):
        st.dataframe(to_show, use_container_width=True)

# Execução
main()
