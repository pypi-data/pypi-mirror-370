import numpy as np
import pandas as pd

def _as_2d_array(X):
    if isinstance(X, pd.DataFrame):
        return X.values, list(X.columns)
    X = np.asarray(X)
    if X.ndim == 1:
        X = X.reshape(-1,1)
    names = [f"feature_{i}" for i in range(X.shape[1])]
    return X, names

def sample_dataframe(X, y=None, max_rows=10000, random_state=0):
    import numpy as np
    import pandas as pd
    if isinstance(X, np.ndarray):
        n = X.shape[0]
        if n <= max_rows:
            return X, y
        rng = np.random.default_rng(random_state)
        sel = rng.choice(n, size=max_rows, replace=False)
        return X[sel], (y[sel] if y is not None else None)
    n = len(X)
    if n <= max_rows:
        return X, y
    if y is None:
        return X.sample(n=max_rows, random_state=random_state), None
    df = X.copy()
    df['_y_for_sampling'] = y
    frac = max_rows / n
    sampled = df.groupby('_y_for_sampling', group_keys=False).apply(lambda d: d.sample(frac=max(min(frac,1), 0.01), random_state=random_state))
    y_sampled = sampled['_y_for_sampling'].values
    sampled = sampled.drop(columns=['_y_for_sampling'])
    return sampled, y_sampled

def select_top_features_by_univariate(X, y, task='classification', k=50, random_state=0):
    import numpy as np
    from sklearn.feature_selection import mutual_info_classif, f_regression
    X_arr, names = (X.values, list(X.columns)) if hasattr(X, "values") else (np.asarray(X), [f"feature_{i}" for i in range(np.asarray(X).shape[1])])
    if k >= X_arr.shape[1]:
        return list(range(X_arr.shape[1])), names
    if task == 'classification':
        try:
            scores = mutual_info_classif(X_arr, y, random_state=random_state)
        except Exception:
            scores = np.var(X_arr, axis=0)
    else:
        try:
            f_vals, _ = f_regression(X_arr, y)
            scores = np.nan_to_num(f_vals)
        except Exception:
            scores = np.var(X_arr, axis=0)
    idx = (-scores).argsort()[:k]
    selected_names = [names[i] for i in idx]
    return idx.tolist(), selected_names
