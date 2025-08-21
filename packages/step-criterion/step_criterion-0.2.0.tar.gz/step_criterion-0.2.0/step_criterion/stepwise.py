from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf


@dataclass
class StepwiseResult:
    model: object                      # statsmodels Results object
    anova: pd.DataFrame                # R-like step path
    keep: Optional[pd.DataFrame] = None


# --------------------------
# Formula utilities
# --------------------------

def _lhs_rhs(formula: str) -> Tuple[str, str]:
    lhs, rhs = formula.split("~", 1)
    return lhs.strip(), rhs.strip()


def _has_no_intercept(rhs: str) -> bool:
    tokens = [t.strip() for t in rhs.replace("\n", " ").split("+")]
    return any(tok in {"-1", "0"} for tok in tokens)


def _parse_terms(rhs: str) -> List[str]:
    parts = [t.strip() for t in rhs.replace("\n", " ").split("+")]
    cleaned = []
    for t in parts:
        if not t:
            continue
        if t in {"1", "0", "-1"}:
            continue
        cleaned.append(t)
    return cleaned


def _build_formula(lhs: str, terms: List[str], no_intercept: bool) -> str:
    if no_intercept:
        rhs = "-1"
        if terms:
            rhs = " -1 + " + " + ".join(terms)
    else:
        rhs = "1"
        if terms:
            rhs = "1 + " + " + ".join(terms)
    return f"{lhs} ~ {rhs}"


def _fit(formula: str,
         data: pd.DataFrame,
         family=None,
         **fit_kwargs):
    # Suppress scipy stats warnings about small sample sizes
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", 
                              message=".*only valid for n>=20.*continuing anyway.*",
                              category=UserWarning,
                              module="scipy.stats.*")
        if family is None:
            model = smf.ols(formula, data=data)
        else:
            model = smf.glm(formula, data=data, family=family)
        res = model.fit(**fit_kwargs)
    return res


def _aic_k(result, k: float) -> float:
    llf = getattr(result, "llf", None)
    if llf is None or not np.isfinite(llf):
        raise ValueError("Model log-likelihood not available; cannot compute information criteria.")
    return -2.0 * llf + k * len(result.params)


def _bic(result) -> float:
    nobs = int(result.nobs)
    return _aic_k(result, np.log(nobs))


def _adjr2(result) -> float:
    adj = getattr(result, "rsquared_adj", None)
    if adj is None or not np.isfinite(adj):
        raise ValueError("Adjusted R^2 not available (only valid for OLS models).")
    # maximize adjR2 -> minimize negative
    return -float(adj)


def _my_deviance(result) -> float:
    dev = getattr(result, "deviance", None)
    if dev is not None and np.isfinite(dev):
        return float(dev)
    llf = getattr(result, "llf", None)
    if llf is not None and np.isfinite(llf):
        return float(-2.0 * llf)
    return np.nan


def _score(result, criterion: str, k: float) -> float:
    criterion = criterion.lower()
    if criterion == "aic":
        return _aic_k(result, k)
    if criterion == "bic":
        return _bic(result)
    if criterion == "adjr2":
        return _adjr2(result)
    raise ValueError("Unsupported criterion for numeric scoring.")


def _glm_term_pvalue_wald(res, term_name: str) -> Optional[float]:
    """Return Wald test p-value for a formula term on a GLM/OLS result, if available."""
    try:
        # Suppress FutureWarning about wald_test behavior change
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", 
                                  message="The behavior of wald_test will change after 0.14.*",
                                  category=FutureWarning)
            wt = res.wald_test_terms(skip_single=False, scalar=True)  # Use future behavior
        table = getattr(wt, "table", None)
        if table is None:
            return None
        if term_name not in table.index:
            return None
        for col in ("P>chi2", "Pr(>F)", "pvalue", "P>|z|"):
            if col in table.columns:
                val = table.loc[term_name, col]
                return float(val)
    except Exception:
        return None
    return None


def _step_core(
    *,
    data: pd.DataFrame,
    initial: str,
    scope: Optional[Union[str, Dict[str, str]]],
    direction: str,
    criterion: str,
    trace: int,
    keep: Optional[Callable[[object, float], dict]],
    steps: int,
    family,
    fit_kwargs: Optional[dict],
    alpha_enter: float,
    alpha_exit: float,
    glm_test: str,
    aic_k: float,
) -> StepwiseResult:
    if fit_kwargs is None:
        fit_kwargs = {}

    # Parse starting formula
    lhs, rhs0 = _lhs_rhs(initial)
    no_intercept0 = _has_no_intercept(rhs0)
    current_terms = _parse_terms(rhs0)

    # Parse scope
    if scope is None:
        lower_terms = []
        upper_terms = current_terms[:]  # backward only
        forward_allowed = direction in {"both", "forward"} and False
    else:
        if isinstance(scope, str):
            _, rhs_u = _lhs_rhs(scope)
            upper_terms = _parse_terms(rhs_u)
            lower_terms = []
        elif isinstance(scope, dict):
            lower_terms = []
            upper_terms = []
            if scope.get("lower") is not None:
                _, rhs_l = _lhs_rhs(scope["lower"])
                lower_terms = _parse_terms(rhs_l)
            if scope.get("upper") is not None:
                _, rhs_u = _lhs_rhs(scope["upper"])
                upper_terms = _parse_terms(rhs_u)
        else:
            raise TypeError("scope must be None, a formula string, or a dict with 'lower'/'upper'.")
        forward_allowed = direction in {"both", "forward"}

    backward_allowed = direction in {"both", "backward"}

    # Fit initial model
    current_formula = _build_formula(lhs, current_terms, no_intercept0)
    fit = _fit(current_formula, data, family=family, **fit_kwargs)

    # Base display AIC and score
    if criterion == "p-value":
        base_aic = _aic_k(fit, 2.0)
        base_score = np.nan
    else:
        base_score = _score(fit, criterion, k=aic_k)
        base_aic = _aic_k(fit, 2.0 if criterion != "bic" else np.log(int(fit.nobs)))

    nobs0 = int(fit.nobs)

    if trace:
        print(f"Start:  AIC={base_aic:.3f}")
        print(current_formula, "\n")

    models_path = [{
        "change": "",
        "deviance": _my_deviance(fit),
        "df.resid": int(fit.df_resid),
        "AIC": base_aic
    }]
    keep_records = []
    if keep is not None:
        keep_records.append(keep(fit, base_score))

    tol = 1e-7
    steps_remaining = steps

    def can_drop(terms: List[str], t: str) -> bool:
        if not lower_terms:
            return True
        after = set(terms) - {t}
        return set(lower_terms).issubset(after)

    def candidates(terms: List[str]) -> Tuple[List[str], List[str]]:
        drops = [t for t in terms if can_drop(terms, t)]
        adds = [t for t in upper_terms if t not in terms]
        return drops, adds

    while steps_remaining > 0:
        steps_remaining -= 1

        best_change = None
        best_model = None
        best_score = base_score
        best_aic_for_path = base_aic
        best_deviance = None
        best_df_resid = None

        drops, adds = candidates(current_terms)
        rows = []

        if criterion == "p-value":
            chosen = None

            # Backward
            if backward_allowed and drops:
                if family is None:
                    # OLS: F-test via restricted model
                    worst_p = -np.inf
                    for t in drops:
                        new_terms = [x for x in current_terms if x != t]
                        new_formula = _build_formula(lhs, new_terms, no_intercept0)
                        try:
                            res_restricted = _fit(new_formula, data, family=family, **fit_kwargs)
                            F, pval, df_diff = fit.compare_f_test(res_restricted)
                            aic_val = _aic_k(res_restricted, 2.0)
                            rows.append(("-", t, pval, aic_val))
                            if pval > alpha_exit and pval > worst_p:
                                worst_p = pval
                                chosen = (f"- {t}", res_restricted, np.nan, aic_val, new_terms)
                        except Exception as e:
                            rows.append(("-", t, np.nan, np.nan))
                            warnings.warn(f"Drop '{t}' failed: {e}")
                else:
                    if glm_test == "wald":
                        # Use Wald term tests on full model without refitting
                        worst_p = -np.inf
                        for t in drops:
                            pval = _glm_term_pvalue_wald(fit, t)
                            if pval is None or not np.isfinite(pval):
                                rows.append(("-", t, np.nan, np.nan))
                                continue
                            rows.append(("-", t, float(pval), np.nan))
                            if pval > alpha_exit and pval > worst_p:
                                worst_p = pval
                                # need restricted model for transition
                                new_terms = [x for x in current_terms if x != t]
                                new_formula = _build_formula(lhs, new_terms, no_intercept0)
                                try:
                                    res_restricted = _fit(new_formula, data, family=family, **fit_kwargs)
                                    aic_val = _aic_k(res_restricted, 2.0)
                                    chosen = (f"- {t}", res_restricted, np.nan, aic_val, new_terms)
                                except Exception as e:
                                    warnings.warn(f"Restricted fit for drop '{t}' failed: {e}")
                    else:
                        # 'lr', 'score', 'gradient' -> use LR fallback
                        if glm_test in {"score", "gradient"}:
                            warnings.warn("glm_test='score' or 'gradient' not fully implemented; using LR test.")
                        worst_p = -np.inf
                        for t in drops:
                            new_terms = [x for x in current_terms if x != t]
                            new_formula = _build_formula(lhs, new_terms, no_intercept0)
                            try:
                                res_restricted = _fit(new_formula, data, family=family, **fit_kwargs)
                                # Manual LR test for GLM: LR = 2 * (llf_full - llf_reduced)
                                lr_stat = 2 * (fit.llf - res_restricted.llf)
                                df_diff = fit.df_model - res_restricted.df_model
                                from scipy import stats
                                pval = 1 - stats.chi2.cdf(lr_stat, df_diff) if df_diff > 0 else 1.0
                                aic_val = _aic_k(res_restricted, 2.0)
                                rows.append(("-", t, pval, aic_val))
                                if pval > alpha_exit and pval > worst_p:
                                    worst_p = pval
                                    chosen = (f"- {t}", res_restricted, np.nan, aic_val, new_terms)
                            except Exception as e:
                                rows.append(("-", t, np.nan, np.nan))
                                warnings.warn(f"Drop '{t}' failed: {e}")

            # Forward
            if chosen is None and forward_allowed and adds:
                if family is None:
                    best_p = np.inf
                    for t in adds:
                        new_terms = current_terms + [t]
                        new_formula = _build_formula(lhs, new_terms, no_intercept0)
                        try:
                            res_full = _fit(new_formula, data, family=family, **fit_kwargs)
                            F, pval, df_diff = res_full.compare_f_test(fit)
                            aic_val = _aic_k(res_full, 2.0)
                            rows.append(("+", t, pval, aic_val))
                            if pval < alpha_enter and pval < best_p:
                                best_p = pval
                                chosen = (f"+ {t}", res_full, np.nan, aic_val, new_terms)
                        except Exception as e:
                            rows.append(("+", t, np.nan, np.nan))
                            warnings.warn(f"Add '{t}' failed: {e}")
                else:
                    if glm_test == "wald":
                        best_p = np.inf
                        for t in adds:
                            new_terms = current_terms + [t]
                            new_formula = _build_formula(lhs, new_terms, no_intercept0)
                            try:
                                res_full = _fit(new_formula, data, family=family, **fit_kwargs)
                                pval = _glm_term_pvalue_wald(res_full, t)
                                aic_val = _aic_k(res_full, 2.0)
                                rows.append(("+", t, pval, aic_val))
                                if pval is not None and pval < alpha_enter and pval < best_p:
                                    best_p = pval
                                    chosen = (f"+ {t}", res_full, np.nan, aic_val, new_terms)
                            except Exception as e:
                                rows.append(("+", t, np.nan, np.nan))
                                warnings.warn(f"Add '{t}' failed: {e}")
                    else:
                        if glm_test in {"score", "gradient"}:
                            warnings.warn("glm_test='score' or 'gradient' not fully implemented; using LR test.")
                        best_p = np.inf
                        for t in adds:
                            new_terms = current_terms + [t]
                            new_formula = _build_formula(lhs, new_terms, no_intercept0)
                            try:
                                res_full = _fit(new_formula, data, family=family, **fit_kwargs)
                                # Manual LR test for GLM: LR = 2 * (llf_full - llf_reduced)
                                lr_stat = 2 * (res_full.llf - fit.llf)
                                df_diff = res_full.df_model - fit.df_model
                                from scipy import stats
                                pval = 1 - stats.chi2.cdf(lr_stat, df_diff) if df_diff > 0 else 1.0
                                aic_val = _aic_k(res_full, 2.0)
                                rows.append(("+", t, pval, aic_val))
                                if pval < alpha_enter and pval < best_p:
                                    best_p = pval
                                    chosen = (f"+ {t}", res_full, np.nan, aic_val, new_terms)
                            except Exception as e:
                                rows.append(("+", t, np.nan, np.nan))
                                warnings.warn(f"Add '{t}' failed: {e}")

            if rows and trace:
                cand_df = pd.DataFrame(rows, columns=["Op", "Term", "p-value", "AIC"]).sort_values(
                    ["p-value"], na_position="last"
                )
                print(cand_df.to_string(index=False))

            if chosen is None:
                break

            label, best_model, best_score, best_aic_for_path, new_best_terms = chosen
            best_change = label
            best_deviance = _my_deviance(best_model)
            best_df_resid = int(best_model.df_resid)

        else:
            # Numeric criteria
            # Backward
            if backward_allowed and drops:
                for t in drops:
                    new_terms = [x for x in current_terms if x != t]
                    new_formula = _build_formula(lhs, new_terms, no_intercept0)
                    try:
                        res = _fit(new_formula, data, family=family, **fit_kwargs)
                        score_val = _score(res, criterion, k=aic_k)
                        aic_val = _aic_k(res, 2.0 if criterion != "bic" else np.log(int(res.nobs)))
                        rows.append(("-", t, score_val, aic_val))
                        if best_change is None or score_val + tol < best_score:
                            best_change = f"- {t}"
                            best_model = res
                            best_score = score_val
                            best_aic_for_path = aic_val
                            best_deviance = _my_deviance(res)
                            best_df_resid = int(res.df_resid)
                            new_best_terms = new_terms
                    except Exception as e:
                        rows.append(("-", t, np.nan, np.nan))
                        warnings.warn(f"Drop '{t}' failed: {e}")

            # Forward
            if forward_allowed and adds:
                for t in adds:
                    new_terms = current_terms + [t]
                    new_formula = _build_formula(lhs, new_terms, no_intercept0)
                    try:
                        res = _fit(new_formula, data, family=family, **fit_kwargs)
                        score_val = _score(res, criterion, k=aic_k)
                        aic_val = _aic_k(res, 2.0 if criterion != "bic" else np.log(int(res.nobs)))
                        rows.append(("+", t, score_val, aic_val))
                        if best_change is None or score_val + tol < best_score:
                            best_change = f"+ {t}"
                            best_model = res
                            best_score = score_val
                            best_aic_for_path = aic_val
                            best_deviance = _my_deviance(res)
                            best_df_resid = int(res.df_resid)
                            new_best_terms = new_terms
                    except Exception as e:
                        rows.append(("+", t, np.nan, np.nan))
                        warnings.warn(f"Add '{t}' failed: {e}")

            if not rows:
                break

            if trace:
                colname = criterion.upper()
                # Avoid duplicate column names when criterion is AIC
                if colname == "AIC":
                    colname = "Score"
                cand_df = pd.DataFrame(rows, columns=["Op", "Term", colname, "AIC"]).sort_values(
                    colname, na_position="last"
                )
                print(cand_df.to_string(index=False))

            if best_change is None or not np.isfinite(best_score) or not (best_score + tol < base_score):
                break

        # Improve and continue
        fit = best_model
        current_terms = new_best_terms
        base_score = best_score
        base_aic = best_aic_for_path

        nobs_new = int(fit.nobs)
        if nobs_new != nobs0:
            warnings.warn(
                f"Number of observations changed from {nobs0} to {nobs_new}. "
                "This typically means missing values differ across models."
            )

        if trace:
            print(f"\nStep:  AIC={base_aic:.3f}")
            print(_build_formula(lhs, current_terms, no_intercept0), "\n")

        models_path.append({
            "change": best_change,
            "deviance": best_deviance,
            "df.resid": best_df_resid,
            "AIC": base_aic
        })
        if keep is not None:
            keep_records.append(keep(fit, base_score))

    # Build path table
    rd = [m["deviance"] for m in models_path]
    rdf = [m["df.resid"] for m in models_path]
    dd = [np.nan] + [abs(rd[i] - rd[i - 1]) if np.isfinite(rd[i]) and np.isfinite(rd[i - 1]) else np.nan
                     for i in range(1, len(rd))]
    ddf = [np.nan] + [abs(rdf[i] - rdf[i - 1]) if np.isfinite(rdf[i]) and np.isfinite(rdf[i - 1]) else np.nan
                      for i in range(1, len(rdf))]
    path = pd.DataFrame({
        "Step": [m["change"] for m in models_path],
        "Df": ddf,
        "Deviance": dd,
        "Resid. Df": rdf,
        "Resid. Dev": rd,
        "AIC": [m["AIC"] for m in models_path],
    })

    keep_df = None
    if keep_records:
        keep_df = pd.DataFrame(keep_records)

    return StepwiseResult(model=fit, anova=path, keep=keep_df)


def step_criterion(
    data: pd.DataFrame,
    initial: str,
    scope: Optional[Union[str, Dict[str, str]]] = None,
    *,
    direction: str = "both",
    criterion: str = "aic",
    trace: int = 1,
    keep: Optional[Callable[[object, float], dict]] = None,
    steps: int = 1000,
    family=None,
    fit_kwargs: Optional[dict] = None,
    alpha_enter: float = 0.05,
    alpha_exit: float = 0.10,
    glm_test: str = "lr",
) -> StepwiseResult:
    """Public API: stepwise selection with multiple criteria.

    Note: For GLM with criterion='p-value', glm_test may be one of 'lr', 'wald', 'score', 'gradient'.
    'score' and 'gradient' currently fall back to LR with a warning.
    """
    direction = direction.lower()
    if direction not in {"both", "backward", "forward"}:
        raise ValueError("direction must be 'both', 'backward', or 'forward'.")

    criterion = criterion.lower()
    if criterion not in {"aic", "bic", "adjr2", "p-value"}:
        raise ValueError("criterion must be one of 'aic', 'bic', 'adjr2', 'p-value'.")

    if criterion == "adjr2" and family is not None:
        raise ValueError("criterion='adjr2' is only supported for OLS (family=None).")

    glm_test = glm_test.lower()
    if glm_test not in {"lr", "wald", "score", "gradient"}:
        raise ValueError("glm_test must be one of 'lr', 'wald', 'score', 'gradient'.")

    # Capture and suppress specific warnings during stepwise selection
    collected_warnings = []
    
    with warnings.catch_warnings(record=True) as w:
        warnings.filterwarnings("ignore", 
                              message=".*only valid for n>=20.*continuing anyway.*",
                              category=UserWarning,
                              module="scipy.stats.*")
        warnings.filterwarnings("ignore", 
                              message="The behavior of wald_test will change after 0.14.*",
                              category=FutureWarning,
                              module="statsmodels.*")
        
        result = _step_core(
            data=data,
            initial=initial,
            scope=scope,
            direction=direction,
            criterion=criterion,
            trace=trace,
            keep=keep,
            steps=steps,
            family=family,
            fit_kwargs=fit_kwargs,
            alpha_enter=alpha_enter,
            alpha_exit=alpha_exit,
            glm_test=glm_test,
            aic_k=2.0,
        )
        
        # Collect any other warnings that weren't filtered
        for warning in w:
            if not any(pattern in str(warning.message) for pattern in [
                "only valid for n>=20", 
                "behavior of wald_test will change"
            ]):
                collected_warnings.append(str(warning.message))
    
    # Print collected warnings at the end if any
    if collected_warnings and trace > 0:
        print("\nNote: Some warnings were encountered during stepwise selection:")
        for msg in collected_warnings[:5]:  # Limit to first 5 unique warnings
            print(f"  - {msg}")
        if len(collected_warnings) > 5:
            print(f"  ... and {len(collected_warnings) - 5} more warnings")
    
    return result


def step_aic(
    data: pd.DataFrame,
    initial: str,
    scope: Optional[Union[str, Dict[str, str]]] = None,
    *,
    direction: str = "both",
    trace: int = 1,
    keep: Optional[Callable[[object, float], dict]] = None,
    steps: int = 1000,
    k: float = 2.0,
    family=None,
    fit_kwargs: Optional[dict] = None,
) -> StepwiseResult:
    """AIC-based selection. k controls the AIC penalty (default 2.0)."""
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", 
                              message=".*only valid for n>=20.*continuing anyway.*",
                              category=UserWarning,
                              module="scipy.stats.*")
        warnings.filterwarnings("ignore", 
                              message="The behavior of wald_test will change after 0.14.*",
                              category=FutureWarning,
                              module="statsmodels.*")
        
        return _step_core(
            data=data,
            initial=initial,
            scope=scope,
            direction=direction,
            criterion="aic",
            trace=trace,
            keep=keep,
            steps=steps,
            family=family,
            fit_kwargs=fit_kwargs,
            alpha_enter=0.05,
            alpha_exit=0.10,
            glm_test="lr",
            aic_k=k,
        )


def step_bic(
    data: pd.DataFrame,
    initial: str,
    scope: Optional[Union[str, Dict[str, str]]] = None,
    *,
    direction: str = "both",
    trace: int = 1,
    keep: Optional[Callable[[object, float], dict]] = None,
    steps: int = 1000,
    family=None,
    fit_kwargs: Optional[dict] = None,
) -> StepwiseResult:
    """BIC-based selection (penalty is log(n))."""
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", 
                              message=".*only valid for n>=20.*continuing anyway.*",
                              category=UserWarning,
                              module="scipy.stats.*")
        warnings.filterwarnings("ignore", 
                              message="The behavior of wald_test will change after 0.14.*",
                              category=FutureWarning,
                              module="statsmodels.*")
        
        return _step_core(
            data=data,
            initial=initial,
            scope=scope,
            direction=direction,
            criterion="bic",
            trace=trace,
            keep=keep,
            steps=steps,
            family=family,
            fit_kwargs=fit_kwargs,
            alpha_enter=0.05,
            alpha_exit=0.10,
            glm_test="lr",
            aic_k=2.0,
        )


def step_adjr2(
    data: pd.DataFrame,
    initial: str,
    scope: Optional[Union[str, Dict[str, str]]] = None,
    *,
    direction: str = "both",
    trace: int = 1,
    keep: Optional[Callable[[object, float], dict]] = None,
    steps: int = 1000,
    fit_kwargs: Optional[dict] = None,
) -> StepwiseResult:
    """Adjusted R^2-based selection (OLS only)."""
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", 
                              message=".*only valid for n>=20.*continuing anyway.*",
                              category=UserWarning,
                              module="scipy.stats.*")
        warnings.filterwarnings("ignore", 
                              message="The behavior of wald_test will change after 0.14.*",
                              category=FutureWarning,
                              module="statsmodels.*")
        
        return _step_core(
            data=data,
            initial=initial,
            scope=scope,
            direction=direction,
            criterion="adjr2",
            trace=trace,
            keep=keep,
            steps=steps,
            family=None,
            fit_kwargs=fit_kwargs,
            alpha_enter=0.05,
            alpha_exit=0.10,
            glm_test="lr",
            aic_k=2.0,
        )


def step_pvalue(
    data: pd.DataFrame,
    initial: str,
    scope: Optional[Union[str, Dict[str, str]]] = None,
    *,
    direction: str = "both",
    trace: int = 1,
    keep: Optional[Callable[[object, float], dict]] = None,
    steps: int = 1000,
    family=None,
    fit_kwargs: Optional[dict] = None,
    alpha_enter: float = 0.05,
    alpha_exit: float = 0.10,
    glm_test: str = "lr",
) -> StepwiseResult:
    """P-value based selection (OLS uses F-tests; GLM supports 'lr' and 'wald')."""
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", 
                              message=".*only valid for n>=20.*continuing anyway.*",
                              category=UserWarning,
                              module="scipy.stats.*")
        warnings.filterwarnings("ignore", 
                              message="The behavior of wald_test will change after 0.14.*",
                              category=FutureWarning,
                              module="statsmodels.*")
        
        return _step_core(
            data=data,
            initial=initial,
            scope=scope,
            direction=direction,
            criterion="p-value",
            trace=trace,
            keep=keep,
            steps=steps,
            family=family,
            fit_kwargs=fit_kwargs,
            alpha_enter=alpha_enter,
            alpha_exit=alpha_exit,
            glm_test=glm_test,
            aic_k=2.0,
        )
