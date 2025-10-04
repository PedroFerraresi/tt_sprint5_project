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
    """
    Converte nomes de estados dos EUA para siglas.
    Se já vier em sigla (duas letras), mantém.
    """
    s = pd.Series(series).astype(str)
    sample = s.dropna().head(50)
    if not sample.empty and (sample.str.fullmatch(r"[A-Z]{2}").mean() > 0.6):
        return s.str.upper()
    return s.map(US_STATE_TO_ABBR).fillna(s)
