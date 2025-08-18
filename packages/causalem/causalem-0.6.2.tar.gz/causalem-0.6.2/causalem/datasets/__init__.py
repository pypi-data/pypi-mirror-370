import importlib.resources
import warnings

import numpy as np
import pandas as pd


def load_data_tof(
    *,
    raw: bool = True,
    treat_levels: list[str] = ["PrP", "SPS"],
    binarize_outcome: bool = False,
    binarization_threshold: float | None = None,
) -> pd.DataFrame | tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Load the simulated tetralogy of Fallot (TOF) dataset. By default
    returns a DataFrame with time-to-event information.
    If ``raw=False``, returns ``(X, t, y)`` where:
      • X : array (n × 2) of [age, zscore]
      • t : array (n,) binary indicator per treat_levels[1]
      • y : array (n × 2) of [time, status]
    When ``binarize_outcome=True`` the outcome is converted to a binary
    failure indicator using ``binarization_threshold``. If the threshold is
    ``None`` it defaults to ``df['time'].median()``. Observations censored
    before the threshold are dropped.
    Parameters
    ----------
    raw : bool
        If True, return pd.DataFrame. If False, return (X,t,y).
    treat_levels : list[str]
        Two-item list [control_label, treatment_label].
        Must be subset of the three levels in the data.
    binarize_outcome : bool, default False
        Convert the time-to-event outcome into a binary failure indicator.
    binarization_threshold : float or None, default None
        Threshold used for binarization. If ``None`` uses the median time.
    """
    # --- load CSV ---
    pkg = importlib.resources.files("causalem.datasets")
    path = pkg.joinpath("tof_survival.csv")
    df = pd.read_csv(path.open("r"))

    if binarize_outcome:
        threshold = (
            float(binarization_threshold)
            if binarization_threshold is not None
            else float(df["time"].median())
        )
        cens_mask = (df["time"] <= threshold) & (df["status"] == 0)
        n_removed = int(cens_mask.sum())
        if n_removed:
            warnings.warn(
                f"Removed {n_removed} observations censored before threshold {threshold}",
                UserWarning,
            )
        df = df.loc[~cens_mask].copy()
        df["outcome"] = np.where(df["time"] > threshold, 0, 1)
        if raw:
            return df.drop(columns=["time", "status"])

    if raw:
        return df

    # --- validate treat_levels ---
    levels = set(df["treatment"].unique())
    if (
        not isinstance(treat_levels, (list, tuple))
        or len(treat_levels) != 2
        or any(lbl not in levels for lbl in treat_levels)
    ):
        raise ValueError(
            f"treat_levels must be two of {sorted(levels)}, got {treat_levels!r}"
        )

    # --- filter to those two groups ---
    df2 = df[df["treatment"].isin(treat_levels)].copy()

    # --- build arrays ---
    X = df2[["age", "zscore"]].to_numpy(dtype=float)
    t = (df2["treatment"] == treat_levels[1]).astype(int).to_numpy()
    if binarize_outcome:
        y = df2["outcome"].astype(int).to_numpy()
    else:
        y = df2[["time", "status"]].to_numpy()

    return X, t, y


def load_data_lalonde(
    *,
    raw: bool = True,
    binarize_outcome: bool = False,
    binarization_threshold: float | None = None,
) -> pd.DataFrame | tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Load the Lalonde job training data.
    By default returns a DataFrame.
    If ``raw=False``, returns ``(X, t, y)`` where:
      • X : array of confounders (all cols except treat, re78)
      • t : array of binary treatment indicator (from ``treat``)
      • y : array of outcomes (from ``re78``)
    When ``binarize_outcome=True`` the ``re78`` column is thresholded at
    ``binarization_threshold`` (or its median if ``None``) and converted to
    a 0/1 indicator.
    """
    pkg = importlib.resources.files("causalem.datasets")
    path = pkg.joinpath("lalonde.csv")
    df = pd.read_csv(path.open("r"))

    if binarize_outcome:
        threshold = (
            float(binarization_threshold)
            if binarization_threshold is not None
            else float(df["re78"].median())
        )
        df["re78"] = (df["re78"] > threshold).astype(int)
        if raw:
            return df

    if raw:
        return df

    # --- build arrays ---
    if "treat" not in df.columns or "re78" not in df.columns:
        raise ValueError("Expected columns 'treat' and 're78' in Lalonde data")

    t = df["treat"].astype(int).to_numpy()
    y = df["re78"].to_numpy()
    X = df.drop(columns=["treat", "re78"]).to_numpy()

    return X, t, y
