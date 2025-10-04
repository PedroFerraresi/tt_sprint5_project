# utils/aux_functions.py
# ------------------------------------------------------------
# Helpers reutilizáveis pelo app (páginas e filtros)

import pandas as pd

# ---------------------------
# Seleção e listas auxiliares
# ---------------------------
def first_existing(df, candidates):
    """Retorna o primeiro nome de coluna que existir no df dentre os candidatos."""
    for c in candidates:
        if c in df.columns:
            return c
    return None

def range_from_series(s):
    """Retorna (min, max) seguro para sliders numéricos."""
    try:
        return float(pd.Series(s).min()), float(pd.Series(s).max())
    except Exception:
        return 0.0, 0.0

def unique_sorted(s):
    """Retorna valores únicos ordenados como lista (ignora NaN/None)."""
    try:
        vals = pd.Series(s).dropna().unique().tolist()
        vals = [v for v in vals if v is not None]
        return sorted(vals)
    except Exception:
        return []

# ---------------------------
# Geografia (EUA)
# ---------------------------
US_STATE_TO_ABBR = {
    "Alabama":"AL","Alaska":"AK","Arizona":"AZ","Arkansas":"AR","California":"CA","Colorado":"CO",
    "Connecticut":"CT","Delaware":"DE","District of Columbia":"DC","Florida":"FL","Georgia":"GA",
    "Hawaii":"HI","Idaho":"ID","Illinois":"IL","Indiana":"IN","Iowa":"IA","Kansas":"KS","Kentucky":"KY",
    "Louisiana":"LA","Maine":"ME","Maryland":"MD","Massachusetts":"MA","Michigan":"MI","Minnesota":"MN",
    "Mississippi":"MS","Missouri":"MO","Montana":"MT","Nebraska":"NE","Nevada":"NV","New Hampshire":"NH",
    "New Jersey":"NJ","New Mexico":"NM","New York":"NY","North Carolina":"NC","North Dakota":"ND",
    "Ohio":"OH","Oklahoma":"OK","Oregon":"OR","Pennsylvania":"PA","Rhode Island":"RI","South Carolina":"SC",
    "South Dakota":"SD","Tennessee":"TN","Texas":"TX","Utah":"UT","Vermont":"VT","Virginia":"VA",
    "Washington":"WA","West Virginia":"WV","Wisconsin":"WI","Wyoming":"WY"
}

def names_to_us_abbrev(series):
    """Converte nomes de estados para siglas. Se já estiver em sigla (2 letras), mantém."""
    s = pd.Series(series).astype(str)
    sample = s.dropna().head(50)
    if not sample.empty and (sample.str.fullmatch(r"[A-Z]{2}").mean() > 0.6):
        return s.str.upper()
    return s.map(US_STATE_TO_ABBR).fillna(s)

# ---------------------------
# Pareto / ABC
# ---------------------------
def build_pareto_full(df, value_col, key_col):
    """
    Calcula Pareto COMPLETO por 'key_col' com base em 'value_col'.
    Retorna dataframe ordenado desc + colunas 'share' e 'cum_share',
    e o total (soma) da métrica.
    """
    g = (
        df.groupby(key_col, as_index=False)[value_col]
          .sum()
          .sort_values(value_col, ascending=False)
          .reset_index(drop=True)
    )
    total = g[value_col].sum()
    if total == 0:
        g["share"] = 0.0
        g["cum_share"] = 0.0
    else:
        g["share"] = g[value_col] / total
        g["cum_share"] = g["share"].cumsum()
    return g, total

def abc_class(cum_share):
    """Classificação ABC tradicional: A≤80%, B≤95%, C>95%."""
    if cum_share <= 0.80:
        return "A"
    elif cum_share <= 0.95:
        return "B"
    return "C"

# ---------------------------
# Cohort (mês de pedido e tabela de contagem)
# ---------------------------
def ensure_month_col(df):
    """
    Gera coluna 'order_month' (timestamp do 1º dia do mês) e garante 'month_year'
    quando possível. Usa 'order_date' se existir; senão tenta 'month_year'.
    """
    temp = df.copy()
    if "order_date" in temp.columns and pd.api.types.is_datetime64_any_dtype(temp["order_date"]):
        temp["order_month"] = temp["order_date"].dt.to_period("M").dt.to_timestamp()
        if "month_year" not in temp.columns:
            temp["month_year"] = temp["order_date"].dt.to_period("M").astype(str)
    elif "month_year" in temp.columns:
        try:
            pidx = pd.PeriodIndex(temp["month_year"], freq="M")
            temp["order_month"] = pidx.to_timestamp(how="start")
        except Exception:
            temp["order_month"] = pd.NaT
    else:
        temp["order_month"] = pd.NaT
    return temp

def build_customer_cohort_count(df, customer_col, date_col_month):
    """
    Cohort por MÊS da 1ª compra (contagem de clientes).
    Retorna (pivot, cohort_sizes), onde:
      - pivot: linhas = mês da coorte; colunas = meses desde a coorte; valores = #clientes
      - cohort_sizes: coluna 0 do pivot (tamanho da coorte)
    """
    d = df[[customer_col, date_col_month]].copy()
    if d.empty:
        return pd.DataFrame(), pd.Series(dtype=float)

    first_purchase = (
        d.groupby(customer_col, as_index=False)[date_col_month]
         .min()
         .rename(columns={date_col_month: "cohort_month"})
    )
    d = d.merge(first_purchase, on=customer_col, how="left")

    d["cohort_index"] = (
        (d[date_col_month].dt.year - d["cohort_month"].dt.year) * 12
        + (d[date_col_month].dt.month - d["cohort_month"].dt.month)
    )

    grp = (
        d.groupby(["cohort_month", "cohort_index"])[customer_col]
         .nunique()
         .reset_index(name="value")
    )
    pivot = grp.pivot(index="cohort_month", columns="cohort_index", values="value").sort_index().fillna(0)

    cohort_sizes = pivot[0] if 0 in pivot.columns else pd.Series(dtype=float)
    return pivot, cohort_sizes
