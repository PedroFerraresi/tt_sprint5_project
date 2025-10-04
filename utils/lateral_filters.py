# utils/lateral_filters.py — filtros da barra lateral (período como slider)
# -----------------------------------------------------------------------
import streamlit as st
import pandas as pd
from utils.aux_functions import range_from_series, unique_sorted

def sidebar_filters(df):
    """
    Desenha filtros na barra lateral e devolve o DataFrame filtrado.
    Período é slider:
      - Se existir 'order_date' (datetime) -> slider de datas
      - Senão, se existir 'month_year' (YYYY-MM) -> slider com 1º dia do mês
    """
    st.sidebar.markdown("### 🔎 Filtros")

    df_filtered = df.copy()

    # =========================
    # Período (slider)
    # =========================
    if "order_date" in df_filtered.columns and pd.api.types.is_datetime64_any_dtype(df_filtered["order_date"]):
        min_d = pd.to_datetime(df_filtered["order_date"].min())
        max_d = pd.to_datetime(df_filtered["order_date"].max())
        if pd.notna(min_d) and pd.notna(max_d) and min_d <= max_d:
            start_date, end_date = st.sidebar.slider(
                "Período (Order Date)",
                min_value=min_d.to_pydatetime(),
                max_value=max_d.to_pydatetime(),
                value=(min_d.to_pydatetime(), max_d.to_pydatetime()),
            )
            start_date = pd.to_datetime(start_date)
            end_date = pd.to_datetime(end_date)
            df_filtered = df_filtered[(df_filtered["order_date"] >= start_date) & (df_filtered["order_date"] <= end_date)]

    elif "month_year" in df_filtered.columns:
        try:
            period_idx = pd.PeriodIndex(df_filtered["month_year"], freq="M")
            month_start = period_idx.to_timestamp(how="start")
            df_filtered["_month_start_tmp"] = month_start

            min_m = month_start.min()
            max_m = month_start.max()
            if pd.notna(min_m) and pd.notna(max_m) and min_m <= max_m:
                start_m, end_m = st.sidebar.slider(
                    "Período (Month-Year)",
                    min_value=min_m.to_pydatetime(),
                    max_value=max_m.to_pydatetime(),
                    value=(min_m.to_pydatetime(), max_m.to_pydatetime()),
                )
                start_p = pd.Period(pd.to_datetime(start_m), freq="M")
                end_p = pd.Period(pd.to_datetime(end_m), freq="M")
                cur_p = pd.PeriodIndex(df_filtered["month_year"], freq="M")
                mask = (cur_p >= start_p) & (cur_p <= end_p)
                df_filtered = df_filtered.loc[mask].copy()
        except Exception:
            pass
        finally:
            if "_month_start_tmp" in df_filtered.columns:
                df_filtered.drop(columns=["_month_start_tmp"], inplace=True, errors="ignore")

    # =========================
    # Dimensões de negócio
    # =========================
    if "category" in df_filtered.columns:
        opts = unique_sorted(df_filtered["category"])
        if opts:
            sel = st.sidebar.multiselect("Category", opts, default=opts)
            if sel:
                df_filtered = df_filtered[df_filtered["category"].isin(sel)]

    if "sub_category" in df_filtered.columns:
        opts = unique_sorted(df_filtered["sub_category"])
        if opts:
            sel = st.sidebar.multiselect("Sub-Category", opts, default=opts)
            if sel:
                df_filtered = df_filtered[df_filtered["sub_category"].isin(sel)]

    if "segment" in df_filtered.columns:
        opts = unique_sorted(df_filtered["segment"])
        if opts:
            sel = st.sidebar.multiselect("Segment", opts, default=opts)
            if sel:
                df_filtered = df_filtered[df_filtered["segment"].isin(sel)]

    if "country" in df_filtered.columns:
        opts = unique_sorted(df_filtered["country"])
        if opts:
            sel = st.sidebar.multiselect("Country", opts, default=opts)
            if sel:
                df_filtered = df_filtered[df_filtered["country"].isin(sel)]

    # =========================
    # Faixas numéricas
    # =========================
    if "sales" in df_filtered.columns:
        vmin, vmax = range_from_series(df_filtered["sales"])
        if vmin < vmax:
            sel = st.sidebar.slider("Sales (faixa)", min_value=float(vmin), max_value=float(vmax),
                                    value=(float(vmin), float(vmax)))
            df_filtered = df_filtered[(df_filtered["sales"] >= sel[0]) & (df_filtered["sales"] <= sel[1])]

    if "profit" in df_filtered.columns:
        vmin, vmax = range_from_series(df_filtered["profit"])
        if vmin < vmax:
            sel = st.sidebar.slider("Profit (faixa)", min_value=float(vmin), max_value=float(vmax),
                                    value=(float(vmin), float(vmax)))
            df_filtered = df_filtered[(df_filtered["profit"] >= sel[0]) & (df_filtered["profit"] <= sel[1])]

    if "total_cost" in df_filtered.columns:
        vmin, vmax = range_from_series(df_filtered["total_cost"])
        if vmin < vmax:
            sel = st.sidebar.slider("Total Cost (faixa)", min_value=float(vmin), max_value=float(vmax),
                                    value=(float(vmin), float(vmax)))
            df_filtered = df_filtered[(df_filtered["total_cost"] >= sel[0]) & (df_filtered["total_cost"] <= sel[1])]

    if "total_gross_sales" in df_filtered.columns:
        vmin, vmax = range_from_series(df_filtered["total_gross_sales"])
        if vmin < vmax:
            sel = st.sidebar.slider("Total Gross Sales (faixa)", min_value=float(vmin), max_value=float(vmax),
                                    value=(float(vmin), float(vmax)))
            df_filtered = df_filtered[(df_filtered["total_gross_sales"] >= sel[0]) & (df_filtered["total_gross_sales"] <= sel[1])]

    st.sidebar.caption(f"Linhas após filtros: {len(df_filtered):,}")
    return df_filtered
