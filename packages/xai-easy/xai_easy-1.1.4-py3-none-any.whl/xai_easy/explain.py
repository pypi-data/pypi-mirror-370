from typing import Optional, Iterable
import numpy as np
import pandas as pd
from .utils import _as_2d_array, select_top_features_by_univariate as _select_univariate, sample_dataframe

def _import_optional(name):
    try:
        return __import__(name)
    except Exception:
        return None

_shap = _import_optional("shap")

def _model_predict_proba_or_predict(model, X):
    try:
        if hasattr(model, "predict_proba"):
            return model.predict_proba(X)
        else:
            return model.predict(X)
    except Exception:
        return model.predict(X)

def select_top_features(X, y=None, task='classification', k=50, random_state=0):
    if y is None:
        X_arr, names = _as_2d_array(X)
        vars_ = np.var(X_arr, axis=0)
        idx = (-vars_).argsort()[:k].tolist()
        sel_names = [names[i] for i in idx]
        return idx, sel_names
    return _select_univariate(X, y, task=task, k=k, random_state=random_state)

def permutation_importance(model, X, y=None, metric:Optional[str]=None, n_repeats:int=5, random_state:Optional[int]=42, sample_rows:int=2000):
    Xs, names = _as_2d_array(X)
    if Xs.shape[0] > sample_rows:
        import numpy as np
        rng = np.random.default_rng(random_state)
        sel = rng.choice(Xs.shape[0], size=sample_rows, replace=False)
        Xs = Xs[sel]
        if y is not None:
            y = np.asarray(y)[sel]
    n_features = Xs.shape[1]
    importances = np.zeros(n_features, dtype=float)
    if y is None:
        baseline_pred = _model_predict_proba_or_predict(model, Xs)
        baseline_score = np.var(baseline_pred)
        def score_fn(y_true, y_pred): return np.var(y_pred)
    else:
        y_arr = np.asarray(y)
        if metric is None:
            metric = "accuracy" if len(np.unique(y_arr)) <= 20 else "r2"
        if metric == "accuracy":
            def score_fn(y_t, y_p): return np.mean(y_t == y_p)
        elif metric == "mse":
            def score_fn(y_t, y_p): return -np.mean((y_t - y_p)**2)
        else:
            def score_fn(y_t, y_p):
                ss_res = np.sum((y_t - y_p)**2)
                ss_tot = np.sum((y_t - np.mean(y_t))**2)
                return 1 - ss_res/ss_tot if ss_tot != 0 else 0.0
        baseline_pred = _model_predict_proba_or_predict(model, Xs)
        baseline_score = score_fn(y_arr, baseline_pred)
    rng = np.random.default_rng(random_state)
    for j in range(n_features):
        drops = []
        for _ in range(n_repeats):
            Xp = Xs.copy()
            rng.shuffle(Xp[:, j])
            pred = _model_predict_proba_or_predict(model, Xp)
            score = score_fn(y if y is not None else baseline_pred, pred)
            drops.append(baseline_score - score)
        importances[j] = float(np.mean(drops))
    importances = np.clip(importances, 0, None)
    if importances.sum() > 0:
        importances = importances / importances.sum()
    return importances

def explain_model(model, X, y=None, feature_names:Optional[Iterable[str]]=None, top_n:int=20, task:str='classification',
                  use_shap:Optional[bool]=None, auto_feature_selection:bool=False, sample_rows:int=2000, random_state:int=0):
    X_arr, names_from_X = _as_2d_array(X)
    if feature_names is None:
        feature_names = names_from_X
    n_features = X_arr.shape[1]
    if auto_feature_selection and n_features > max(1000, top_n*5):
        k = max(top_n*5, 500)
        idx, sel_names = select_top_features(X, y=y, task=task, k=k, random_state=random_state)
        X_sel = (X.iloc[:, idx] if hasattr(X, "iloc") else X_arr[:, idx])
        feature_names = sel_names
        X_for_imp = X_sel
    else:
        X_for_imp = X

    if use_shap is None:
        use_shap = (_shap is not None)
    if use_shap and _shap is not None:
        try:
            expl = _shap.TreeExplainer(model)
            vals = expl.shap_values(X_for_imp[:min(200, X_for_imp.shape[0])])
            shap_vals = np.mean(np.abs(vals), axis=0) if isinstance(vals, (list, tuple)) else np.mean(np.abs(vals), axis=0)
            imp = np.asarray(shap_vals, dtype=float)
            if imp.sum() > 0:
                imp = imp / imp.sum()
            df = pd.DataFrame({"feature": list(feature_names),"importance": imp})
            df = df.sort_values("importance", ascending=False).reset_index(drop=True).head(top_n)
            df["rank"] = np.arange(1, len(df)+1)
            df["explanation"] = df.apply(lambda r: f"Feature '{r.feature}' contributes approx {round(float(r.importance)*100,2)}% (SHAP).", axis=1)
            return df[["rank","feature","importance","explanation"]]
        except Exception:
            pass

    # native importances
    try:
        if hasattr(model, "feature_importances_"):
            imp = np.asarray(model.feature_importances_, dtype=float)
        elif hasattr(model, "coef_"):
            coef = np.asarray(model.coef_, dtype=float)
            imp = np.mean(np.abs(coef), axis=0) if coef.ndim > 1 else np.abs(coef)
        else:
            imp = None
    except Exception:
        imp = None

    if imp is None:
        imp = permutation_importance(model, X_for_imp, y=y, n_repeats=5, random_state=random_state, sample_rows=sample_rows)

    imp = np.nan_to_num(imp, nan=0.0)
    if imp.sum() > 0:
        imp = imp / imp.sum()
    df = pd.DataFrame({"feature": list(feature_names), "importance": imp})
    df = df.sort_values("importance", ascending=False).reset_index(drop=True).head(top_n)
    df["rank"] = np.arange(1, len(df)+1)
    df["explanation"] = df.apply(lambda r: f"Feature '{r.feature}' contributes approx {round(float(r.importance)*100,2)}% to model predictions.", axis=1)
    return df[["rank","feature","importance","explanation"]]

def explain_instance(model, X, instance, feature_names:Optional[Iterable[str]]=None, baseline:Optional[Iterable[float]]=None, use_shap:Optional[bool]=None, sample_rows:int=2000):
    X_arr, names_from_X = _as_2d_array(X)
    if feature_names is None:
        feature_names = names_from_X
    inst = np.asarray(instance).ravel()
    if inst.shape[0] != X_arr.shape[1]:
        raise ValueError("Instance length must match number of features in X.")
    if use_shap is None:
        use_shap = (_shap is not None)
    if use_shap and _shap is not None:
        try:
            background = X_arr[:min(100, X_arr.shape[0])]
            expl = _shap.TreeExplainer(model) if hasattr(model, 'feature_importances_') else _shap.KernelExplainer(lambda v: _model_predict_proba_or_predict(model, v), background)
            vals = expl.shap_values(inst.reshape(1, -1))
            arr = vals
            if isinstance(vals, (list, tuple)):
                arr = np.mean(np.abs(vals), axis=0)
            arr = np.asarray(arr).ravel()
            if arr.sum() != 0:
                arr = arr / np.sum(np.abs(arr))
            df = pd.DataFrame({"feature": list(feature_names), "contribution": arr})
            df = df.sort_values("contribution", ascending=False).reset_index(drop=True)
            df["explanation"] = df.apply(lambda r: f"Feature '{r.feature}' contributes {round(float(r.contribution)*100,2)}% of the local change (SHAP).", axis=1)
            return df
        except Exception:
            pass
    if baseline is None:
        baseline = np.mean(X_arr, axis=0)
    else:
        baseline = np.asarray(baseline).ravel()
    def _pred(x):
        x = np.asarray(x).reshape(1, -1)
        try:
            if hasattr(model, 'predict_proba'):
                proba = model.predict_proba(x)[0]
                return float(np.max(proba))
            else:
                return float(model.predict(x)[0])
        except Exception:
            return float(model.predict(x)[0])
    y_base = _pred(baseline)
    contributions = []
    for j in range(X_arr.shape[1]):
        pert = baseline.copy()
        pert[j] = inst[j]
        y_pert = _pred(pert)
        contributions.append(y_pert - y_base)
    contributions = np.nan_to_num(np.array(contributions, dtype=float))
    total = np.sum(np.abs(contributions))
    if total != 0:
        norm = contributions / total
    else:
        norm = contributions
    df = pd.DataFrame({"feature": list(feature_names), "contribution": norm})
    df = df.sort_values("contribution", ascending=False).reset_index(drop=True)
    df["explanation"] = df.apply(lambda r: f"Setting '{r.feature}' to the instance value changes the prediction by {round(float(r.contribution)*100,2)}% of the local change.", axis=1)
    return df
