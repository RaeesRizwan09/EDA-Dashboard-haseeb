"""
filters.py — Filter logic for the Big Mac Index Dashboard
"""
import pandas as pd


def apply_filters(
    df: pd.DataFrame,
    year_range: tuple,
    selected_countries: list,
) -> pd.DataFrame:
    """
    Apply sidebar filters to the Big Mac dataframe.

    Parameters
    ----------
    df : raw dataframe
    year_range : (min_year, max_year) inclusive tuple
    selected_countries : list of country names; empty list = all countries
    """
    out = df.copy()

    if year_range and "year" in out.columns:
        out = out[(out["year"] >= year_range[0]) & (out["year"] <= year_range[1])]

    if selected_countries and "name" in out.columns:
        out = out[out["name"].isin(selected_countries)]

    return out
