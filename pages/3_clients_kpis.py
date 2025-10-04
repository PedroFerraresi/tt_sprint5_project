# pages/3_clients_kpis.py — Clientes • Geografia (mapa EUA por estado)
import streamlit as st
import plotly.express as px
import pandas as pd

from utils.pre_process import load_processed
from utils.lateral_filters import sidebar_filters
from utils.aux_functions import first_existing, names_to_us_abbrev

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

    st.title("Clientes • Geografia")
    df = sidebar_filters(df)

    sales_col = first_existing(df, ["total_net_sales", "sales"])
    profit_col = first_existing(df, ["profit"])
    cost_col = first_existing(df, ["total_cost"])
    country_col = first_existing(df, ["country"])
    state_col = first_existing(df, ["state"])
    city_col = first_existing(df, ["city"])
    segment_col = first_existing(df, ["segment"])
    customer_col = first_existing(df, ["customer_name", "customer_id", "customer"])

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Qtd Clientes (únicos)", f"{df[customer_col].nunique():,}" if customer_col else "—")
    with col2:
        st.metric("Qtd Segmentos (únicos)", f"{df[segment_col].nunique():,}" if segment_col else "—")
    with col3:
        st.metric("Qtd Países (únicos)", f"{df[country_col].nunique():,}" if country_col else "—")
    with col4:
        st.metric("Qtd Estados (únicos)", f"{df[state_col].nunique():,}" if state_col else "—")
    with col5:
        st.metric("Qtd Cidades (únicos)", f"{df[city_col].nunique():,}" if city_col else "—")

    st.divider()

    # Barras por Segment
    if segment_col and (sales_col or profit_col):
        agg_cols = [column for column in [sales_col, profit_col] if column]
        
        dfg = (
            df
            .groupby(segment_col, as_index=False)
            [agg_cols].sum()
            .sort_values(agg_cols[0], ascending=False)
        )
        
        st.plotly_chart(
            px.bar(
                dfg
                , x=segment_col
                , y=agg_cols
                , barmode="group"
                , title="Resultados por Segmento"
            )
            , use_container_width=True
        )

    st.divider()

    # Mapa por Estados dos EUA
    df_us = df.copy()
    if country_col:
        usa_aliases = {"United States", "United States of America", "USA", "US", "U.S.", "U.S.A.", "UNITED STATES"}
        mask_usa = df_us[country_col].astype(str).str.upper().isin({s.upper() for s in usa_aliases})
        if mask_usa.any():
            df_us = df_us[mask_usa]
    if not state_col:
        st.info("Para o mapa por estados dos EUA, é necessário ter a coluna 'state'.")
    elif not sales_col:
        st.info("Para o mapa por estados dos EUA, é necessário ter a coluna de Vendas (sales/total_net_sales).")
    else:
        g = df_us.groupby(state_col, as_index=False)[sales_col].sum()
        if g.empty:
            st.caption("Sem dados para exibir no mapa por estados com os filtros atuais.")
        else:
            g["state_code"] = names_to_us_abbrev(g[state_col]).str.upper()
            g = g[g["state_code"].str.fullmatch(r"[A-Z]{2}")]
            if g.empty:
                st.caption("Não foi possível mapear estados para siglas dos EUA. Exibindo barras como fallback.")
                st.plotly_chart(px.bar(g, x=state_col, y=sales_col, title="Vendas por Estado (fallback)"),
                                use_container_width=True)
            else:
                try:
                    fig = px.choropleth(
                        g, locations="state_code", locationmode="USA-states",
                        color=sales_col, scope="usa", hover_name=state_col,
                        title=f"Vendas por Estado (EUA) — métrica: {sales_col}"
                    )
                    fig.update_layout(coloraxis_colorbar=dict(title=sales_col))
                    st.plotly_chart(fig, use_container_width=True)
                except Exception:
                    st.plotly_chart(px.bar(g.sort_values(sales_col, ascending=False),
                                           x=state_col, y=sales_col,
                                           title="Vendas por Estado (fallback em barras)"),
                                    use_container_width=True)

    st.divider()

    # Top Cidades por Sales
    if city_col and sales_col:
        g = df.groupby(city_col, as_index=False)[sales_col].sum().sort_values(sales_col, ascending=False).head(20)
        st.plotly_chart(px.bar(g, x=city_col, y=sales_col, title="Top cidades por Vendas (Top 20)"),
                        use_container_width=True)

    st.divider()

    # Top Clientes
    if customer_col and (sales_col or profit_col):
        agg_cols = [c for c in [sales_col, profit_col] if c]
        g = df.groupby(customer_col, as_index=False)[agg_cols].sum()
        if sales_col:
            st.plotly_chart(px.bar(g.sort_values(sales_col, ascending=False).head(20),
                                   x=customer_col, y=sales_col, title="Top clientes por Vendas (Top 20)"),
                            use_container_width=True)
        if profit_col:
            st.plotly_chart(px.bar(g.sort_values(profit_col, ascending=False).head(20),
                                   x=customer_col, y=profit_col, title="Top clientes por Profit (Top 20)"),
                            use_container_width=True)
            st.plotly_chart(px.bar(g.sort_values(profit_col, ascending=True).head(20),
                                   x=customer_col, y=profit_col, title="Maiores prejuízos por cliente (Top 20)"),
                            use_container_width=True)

main()
