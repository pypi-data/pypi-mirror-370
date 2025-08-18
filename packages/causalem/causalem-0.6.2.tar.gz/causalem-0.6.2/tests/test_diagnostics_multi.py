import numpy as np
import pandas as pd

from causalem import summarize_matching


def test_multiarm_diagnostics_runs():
    rng = np.random.default_rng(0)
    n_per = 30
    t = np.repeat([0, 1, 2], n_per)
    # fake covariates
    X = pd.DataFrame(
        {
            "age": rng.integers(10, 60, size=t.size),
            "bmi": rng.normal(25, 3, size=t.size),
        }
    )
    # clusters: deterministic one-of-each id (every consecutive triple)
    cid = -np.ones((t.size, 1), int)
    cid[:, 0] = np.repeat(np.arange(n_per), 3)

    diag = summarize_matching(cid, X, treatment=t, ref_group=0, plot=False)

    assert "combined" in diag.ess
    assert isinstance(diag.ess["combined"], float)
    assert diag.ess["combined"] > 0
    assert diag.per_sample.index.nlevels == 3  # draw,cov,pair
    assert diag.summary.shape[0] == 2  # two covariates
