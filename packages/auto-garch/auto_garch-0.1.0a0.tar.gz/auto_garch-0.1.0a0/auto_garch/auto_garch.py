"""
Auto-Garch: Regime-aware volatility modeling
--------------------------------------------
- Strict CSV load (datetime index + numeric column)
- Feature build (returns, rolling vol, rolling skews)
- HMM (k=2 by default) for regimes
- Auto-spec & fit GARCH variants per regime + baseline
- Reporting/visualization with R2 attribution & diagnostics

Entry:
    pipeline = AutoGarch(config=Config())
    result = pipeline.run(csv_path, column, date_col)
"""
from __future__ import annotations

import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, Tuple, Optional, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import r2_score
from hmmlearn.hmm import GaussianHMM
from arch import arch_model

warnings.filterwarnings("ignore")

# -----------------------------
# Config
# -----------------------------
@dataclass(frozen=True)
class Config:
    vol_window: int = 20
    skew_window: int = 200
    vol_min_periods: Optional[int] = None
    skew_min_periods: Optional[int] = None
    train_frac: float = 0.7
    n_states: int = 2
    random_state: int = 42
    
# -----------------------------
# Pipeline
# -----------------------------
class AutoGarch:
    # in-memory cache keyed by (absolute_path, date_col)
    _IO_CACHE: Dict[Tuple[str, Optional[str]], pd.DataFrame] = {}

    def __init__(self, config: Config):
        self.config = config

    # I/O
    @classmethod
    def _load_dataframe(cls, csv_path: Union[str, Path], date_col: Optional[str]) -> pd.DataFrame:
        path = Path(csv_path)
        if not path.exists():
            raise FileNotFoundError(f"CSV file not found: {path.resolve()}")

        key = (str(path.resolve()), date_col)
        if key in cls._IO_CACHE:
            return cls._IO_CACHE[key].copy()

        if date_col:
            df = pd.read_csv(path, parse_dates=[date_col], index_col=date_col)
            if not isinstance(df.index, pd.DatetimeIndex):
                raise ValueError(f"Parsed index from '{date_col}' is not DatetimeIndex.")
        else:
            df = pd.read_csv(path)

        cls._IO_CACHE[key] = df.copy()
        return df.copy()

    @classmethod
    def load_series(cls, csv_path: Union[str, Path], column: str, date_col: str) -> pd.Series:
        df = cls._load_dataframe(csv_path, date_col=date_col)
        if column not in df.columns:
            raise KeyError(f"Column '{column}' not found. Available: {list(df.columns)}")
        series = df[column].dropna()
        try:
            series = series.astype(float)
        except Exception as e:
            raise ValueError(f"Column '{column}' could not be cast to float: {e}") from e
        if not isinstance(series.index, pd.DatetimeIndex):
            raise ValueError(f"Index is not DatetimeIndex after parsing '{date_col}'.")
        return series

    # =========================
    # Feature Engineering
    # =========================
    @staticmethod
    def _resolve_min_periods(window: int, min_periods: Optional[int]) -> int:
        return window if min_periods is None else min_periods

    @classmethod
    def compute_returns(cls, series: pd.Series) -> pd.Series:
        rets = series.pct_change().dropna()
        if rets.empty:
            raise ValueError("Need at least 2 observations to compute returns.")
        return rets

    @classmethod
    def compute_volatility(cls, returns: pd.Series, window: int, min_periods: Optional[int]) -> pd.Series:
        resolved = cls._resolve_min_periods(window, min_periods)
        return returns.rolling(window=window, min_periods=resolved).std()

    @classmethod
    def compute_skew_returns(cls, returns: pd.Series, window: int, min_periods: Optional[int]) -> pd.Series:
        resolved = cls._resolve_min_periods(window, min_periods)
        return returns.rolling(window=window, min_periods=resolved).skew()

    @classmethod
    def compute_skew_volatility(cls, volatility: pd.Series, window: int, min_periods: Optional[int]) -> pd.Series:
        resolved = cls._resolve_min_periods(window, min_periods)
        return volatility.rolling(window=window, min_periods=resolved).skew()

    def compute_metrics(self, series: pd.Series) -> Tuple[pd.Series, pd.Series, pd.Series, pd.Series]:
        c = self.config
        rets = self.compute_returns(series)
        vols = self.compute_volatility(rets, c.vol_window, c.vol_min_periods)
        skew_rets = self.compute_skew_returns(rets, c.skew_window, c.skew_min_periods)
        skew_vol = self.compute_skew_volatility(vols, c.skew_window, c.skew_min_periods)
        return rets, vols, skew_rets, skew_vol

    def build_base_features(self, series: pd.Series) -> Tuple[pd.Series, pd.Series, pd.Series, pd.Series, pd.DataFrame]:
        rets, vols, skew_returns, skew_volatility = self.compute_metrics(series)
        feat = pd.concat([
            rets.rename("return"),
            vols.rename("volatility"),
            skew_returns.rename("skew_returns"),
            skew_volatility.rename("skew_volatility"),
        ], axis=1).dropna()
        return rets, vols, skew_returns, skew_volatility, feat

    # =========================
    # Summary utilities
    # =========================
    @staticmethod
    def _safe_mean(series: pd.Series) -> Tuple[float, Optional[str]]:
        clean = series.dropna()
        if clean.empty:
            return np.nan, f"mean: empty after dropna (orig len={len(series)})"
        if clean.nunique() <= 1:
            return np.nan, f"mean: constant series (unique={clean.nunique()})"
        return clean.mean(), None

    @staticmethod
    def _safe_skew(series: pd.Series, min_count: int = 2) -> Tuple[float, Optional[str]]:
        clean = series.dropna()
        if clean.empty:
            return np.nan, f"skew: empty after dropna (orig len={len(series)})"
        if len(clean) < min_count:
            return np.nan, f"skew: insufficient data (n={len(clean)} < min_count={min_count})"
        if clean.nunique() <= 1:
            return np.nan, f"skew: constant series (unique={clean.nunique()})"
        return clean.skew(), None

    @staticmethod
    def _add_issue(diagnostics: Dict[str, Any], msg: str) -> None:
        diagnostics.setdefault("summary_diagnostics", {"issues": []})
        diagnostics["summary_diagnostics"].setdefault("issues", [])
        diagnostics["summary_diagnostics"]["issues"].append(msg)

    def build_summary_from_metrics(
        self,
        rets: pd.Series,
        vols: pd.Series,
        skew_returns: pd.Series,
        skew_volatility: pd.Series,
        garch_result: Optional[Any] = None,
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        diagnostics: Dict[str, Any] = {"summary_diagnostics": {"issues": []}}

        avg_return, diag = self._safe_mean(rets)
        if diag:
            self._add_issue(diagnostics, f"returns_avg: {diag}")

        skew_ret_val, diag = self._safe_skew(skew_returns)
        if diag:
            self._add_issue(diagnostics, f"skew_return: {diag}")

        avg_volatility, diag = self._safe_mean(vols)
        if diag:
            self._add_issue(diagnostics, f"volatility_avg: {diag}")

        skew_vol_val, diag = self._safe_skew(skew_volatility)
        if diag:
            self._add_issue(diagnostics, f"skew_volatility: {diag}")

        summary_df = pd.DataFrame([{
            "avg_return": avg_return,
            "skew_returns": skew_ret_val,
            "avg_volatility": avg_volatility,
            "skew_volatility": skew_vol_val
        }])

        diagnostics.update({
            "returns_length": len(rets),
            "volatility_length": len(vols),
            "skew_return_length": len(skew_returns),
            "skew_volatility_length": len(skew_volatility),
            "returns_sample": rets.dropna().head(5).tolist(),
            "volatility_sample": vols.dropna().head(5).tolist(),
            "skew_return_sample": skew_returns.dropna().head(5).tolist(),
            "skew_volatility_sample": skew_volatility.dropna().head(5).tolist(),
            "returns_unique": rets.dropna().nunique(),
            "volatility_unique": vols.dropna().nunique(),
            "skew_return_unique": skew_returns.dropna().nunique(),
            "skew_volatility_unique": skew_volatility.dropna().nunique(),
        })

        if garch_result is not None:
            try:
                diagnostics["library_summary"] = garch_result.summary().as_text()
            except Exception:
                diagnostics["library_summary"] = "could not retrieve library summary"

            params = getattr(garch_result, "params", {})
            intercept = None
            persistence: Dict[str, Any] = {}
            if isinstance(params, pd.Series):
                intercept = params.get("omega", None)
                persistence["alpha[1]"] = params.get("alpha[1]", None)
                persistence["beta[1]"] = params.get("beta[1]", None)

            diagnostics["model_params"] = params if isinstance(params, (dict, pd.Series)) else {}
            diagnostics["intercept"] = intercept
            diagnostics["persistence"] = persistence

            try:
                resid = garch_result.resid.dropna()
                std_resid = resid / (resid.std() if resid.std() != 0 else 1)
                diagnostics["standardized_residuals_sample"] = std_resid.dropna().head(5).tolist()
            except Exception:
                diagnostics["standardized_residuals_sample"] = []

        return summary_df, diagnostics

    def summarize_by_regime(
        self,
        regimes: pd.Series,
        rets: pd.Series,
        vols: pd.Series,
        skew_returns: pd.Series,
        skew_volatility: pd.Series,
        min_regime_length: int = 1,
    ) -> Tuple[pd.DataFrame, Dict[int, Dict[str, Any]], pd.DataFrame]:
        regimes_aligned = regimes.reindex(rets.index)
        valid_mask = regimes_aligned.notna()
        if valid_mask.sum() == 0:
            raise ValueError("No valid regime labels after alignment; cannot summarize by regime.")

        regimes_clean = regimes_aligned[valid_mask].astype(int)
        merged = pd.DataFrame({
            "return": rets[valid_mask],
            "volatility": vols[valid_mask],
            "skew_returns": skew_returns[valid_mask],
            "skew_volatility": skew_volatility[valid_mask],
            "regime": regimes_clean
        })

        rows, diags = [], {}
        for rid, g in merged.groupby("regime"):
            sm, d = self.build_summary_from_metrics(
                g["return"], g["volatility"], g["skew_returns"], g["skew_volatility"], None
            )
            count = len(g)
            if count < min_regime_length:
                self._add_issue(d, f"regime length {count} < min_regime_length {min_regime_length}")
            rows.append({
                "regime": rid,
                "avg_return": sm.iloc[0]["avg_return"],
                "skew_returns": sm.iloc[0]["skew_returns"],
                "avg_volatility": sm.iloc[0]["avg_volatility"],
                "skew_volatility": sm.iloc[0]["skew_volatility"],
                "count": count
            })
            diags[rid] = d

        summary_df = pd.DataFrame(rows).set_index("regime")[["avg_return", "skew_returns", "avg_volatility", "skew_volatility", "count"]]
        return summary_df, diags, merged

    # =========================
    # HMM
    # =========================
    def prepare_features(self, series: pd.Series) -> pd.DataFrame:
        _, _, _, _, feat = self.build_base_features(series)
        return feat

    def train_test_hmm(
        self, feat: pd.DataFrame
    ) -> Tuple[GaussianHMM, np.ndarray, np.ndarray, np.ndarray, pd.DatetimeIndex, pd.DatetimeIndex]:
        if not {"return", "volatility"}.issubset(feat.columns):
            raise ValueError("Feature DataFrame must contain 'return' and 'volatility'.")

        X_full = feat[["return", "volatility"]].values
        n = len(X_full)
        if n == 0:
            raise ValueError("Feature DataFrame is empty; cannot train HMM.")

        c = self.config
        split = int(n * c.train_frac)
        if split < 1:
            raise ValueError(f"Train fraction {c.train_frac} too small for series length {n}.")
        if split >= n:
            raise ValueError(f"Train fraction {c.train_frac} leaves no test data for length {n}.")

        train_dates = feat.index[:split]
        test_dates = feat.index[split:]
        X_train = X_full[:split]
        X_test = X_full[split:]

        model = GaussianHMM(
            n_components=c.n_states,
            covariance_type="full",
            n_iter=200,
            random_state=c.random_state,
            verbose=False,
        )
        model.fit(X_train)
        regimes_train = model.predict(X_train)
        regimes_test = model.predict(X_test)

        regimes_full = np.empty(n, dtype=int)
        regimes_full[:split] = regimes_train
        regimes_full[split:] = regimes_test

        return model, regimes_train, regimes_test, regimes_full, train_dates, test_dates

    def summarize_test_regimes(
        self,
        regimes_test: np.ndarray,
        test_rets: pd.Series,
        test_vols: pd.Series,
        skew_window: int = 200
    ) -> Tuple[pd.DataFrame, Dict[int, Dict[str, Any]]]:
        idx = test_rets.index.intersection(test_vols.index)
        n = min(len(idx), len(regimes_test))
        if n == 0:
            raise ValueError("No overlapping test data to summarize.")
        idx = idx[:n]
        rtest = regimes_test[:n]

        df = pd.DataFrame({
            "return": test_rets.loc[idx],
            "volatility": test_vols.loc[idx],
            "regime": pd.Series(rtest, index=idx)
        }).dropna()

        rows, diags = [], {}
        for rid, g in df.groupby("regime"):
            skew_r = g["return"].rolling(skew_window, min_periods=2).skew()
            skew_v = g["volatility"].rolling(skew_window, min_periods=2).skew()
            sm, d = self.build_summary_from_metrics(g["return"], g["volatility"], skew_r, skew_v, None)
            rows.append({"regime": rid, **sm.iloc[0].to_dict(), "count": len(g)})
            diags[rid] = d

        return pd.DataFrame(rows).set_index("regime"), diags

    # =========================
    # GARCH Selections & Fitting
    # =========================
    def select_garch_specs(self, summary: pd.DataFrame) -> Tuple[Dict[int, Dict[str, Any]], Dict[int, Dict[str, Any]]]:
        specs: Dict[int, Dict[str, Any]] = {}
        diagnostics: Dict[int, Dict[str, Any]] = {}

        def median_with_fallback(name: str, series: pd.Series, fallback):
            med = series.dropna().median()
            if pd.isna(med):
                for rid in summary.index:
                    diagnostics.setdefault(rid, {"summary_diagnostics": {"issues": []}})
                    self._add_issue(diagnostics[rid], f"{name} median was NaN; using fallback {fallback}")
                return fallback
            return med

        vol_med = median_with_fallback("avg_volatility", summary["avg_volatility"], 0.01)
        low_vol_thr = 0.5 * vol_med
        high_vol_thr = 1.5 * vol_med

        skew_ret_med = median_with_fallback("skew_returns", summary["skew_returns"], 0.0)
        skew_vol_med = median_with_fallback("skew_volatility", summary["skew_volatility"], 0.0)
        ret_med = median_with_fallback("avg_return", summary["avg_return"], 0.0)

        def safe_scalar(val, fallback, name: str, rid: int):
            if pd.isna(val):
                diagnostics.setdefault(rid, {"summary_diagnostics": {"issues": []}})
                self._add_issue(diagnostics[rid], f"{name} was NaN; using fallback {fallback}")
                return fallback
            return val

        for rid, row in summary.iterrows():
            diagnostics.setdefault(rid, {"summary_diagnostics": {"issues": []}})

            avg_vol = safe_scalar(row.get("avg_volatility", np.nan), vol_med, "avg_volatility", rid)
            skew_ret = safe_scalar(row.get("skew_returns", np.nan), skew_ret_med, "skew_returns", rid)
            skew_vol = safe_scalar(row.get("skew_volatility", np.nan), skew_vol_med, "skew_volatility", rid)
            avg_ret = safe_scalar(row.get("avg_return", np.nan), ret_med, "avg_return", rid)

            # Volatility model selection
            if avg_vol < low_vol_thr:
                vol_model = "ARCH";   p, o, q = 1, 0, 0
                rationale = "low volatility → ARCH(1)"
            elif avg_vol < vol_med:
                vol_model = "FIGARCH"; p, o, q = 1, 0, 1
                rationale = "moderate-low volatility → FIGARCH (long memory)"
            elif avg_vol < high_vol_thr:
                if skew_vol > skew_vol_med:
                    vol_model = "APARCH"; p, o, q = 1, 1, 1
                    rationale = "mid volatility + high volatility skew → APARCH"
                else:
                    vol_model = "GARCH";  p, o, q = 1, 0, 1
                    rationale = "mid volatility + low volatility skew → GARCH"
            else:
                if skew_ret < skew_ret_med:
                    vol_model = "EGARCH"; p, o, q = 1, 1, 1
                    rationale = "high volatility + negative/low return skew → EGARCH"
                else:
                    vol_model = "APARCH"; p, o, q = 1, 1, 1
                    rationale = "high volatility + positive return skew → APARCH"

            # Distribution
            if pd.isna(skew_vol):
                dist = "t"
                self._add_issue(diagnostics[rid], "skew_vol is NaN; defaulting distribution to 't'")
            else:
                dist = "t" if skew_vol < skew_vol_med else "skewt"

            # Mean
            if abs(avg_ret) < 1e-6:
                mean = "Zero"
            elif abs(avg_ret) > abs(ret_med) and abs(skew_ret) > skew_ret_med:
                mean = "AR"
            else:
                mean = "Constant"

            lags = 1 if mean == "AR" else 0  # ensure AR has a lag

            specs[rid] = {
                "vol": vol_model, "mean": mean, "lags": lags, "dist": dist,
                "p": p, "o": o, "q": q,
                "rationale": rationale,
                "raw_metrics": {
                    "avg_return": avg_ret,
                    "skew_returns": skew_ret,
                    "avg_volatility": avg_vol,
                    "skew_volatility": skew_vol,
                },
            }

        return specs, diagnostics

    def fit_baseline_garch(
        self,
        series: pd.Series,
        mean: str = "Constant",
        vol: str = "GARCH",
        p: int = 1,
        o: int = 0,
        q: int = 1,
        dist: str = "t",
    ) -> Tuple[Any, float, Dict[str, Any]]:
        rets, vols, skew_returns, skew_volatility, _ = self.build_base_features(series)
        rets_pct = rets * 100
        if rets_pct.empty:
            raise ValueError("Series too short to compute returns for baseline GARCH.")
        min_obs = max(p + o + q + 1, 2)
        if len(rets_pct) < min_obs:
            raise ValueError(f"Not enough observations ({len(rets_pct)}) for GARCH({p},{o},{q}).")

        am = arch_model(rets_pct, mean=mean, vol=vol, p=p, o=o, q=q, dist=dist)
        res = am.fit(disp="off")

        # Safe R2: forecasted mean
        r2_type, r2 = "true", np.nan
        y_true = rets_pct
        try:
            fc = res.forecast(horizon=1, reindex=True)
            if hasattr(fc, "mean") and not fc.mean.empty:
                if isinstance(fc.mean, pd.DataFrame):
                    y_pred = fc.mean.iloc[:, 0].dropna().reindex(y_true.index)
                else:
                    y_pred = fc.mean.dropna().reindex(y_true.index)
                if y_pred.notna().sum() > 3:
                    r2 = r2_score(y_true.loc[y_pred.index], y_pred)
        except Exception:
            pass

        summary_df, summary_diag = self.build_summary_from_metrics(
            rets, vols, skew_returns, skew_volatility, garch_result=res
        )

        params = summary_diag.get("model_params", {})
        intercept = summary_diag.get("intercept")
        persistence = summary_diag.get("persistence", {})

        try:
            resid_full = res.resid.dropna()
            denom = resid_full.std()
            if denom == 0:
                denom = 1
            std_resid_list = (resid_full / denom).tolist()
        except Exception:
            std_resid_list = []

        fit_info = {
            "rationale": "vanilla",
            "summary": summary_df.iloc[0].to_dict(),
            "summary_diagnostics": summary_diag.get("summary_diagnostics", {"issues": []}),
            "feature_diagnostics": {k: v for k, v in summary_diag.items() if k != "summary_diagnostics"},
            "library_summary": summary_diag.get("library_summary", ""),
            "model_params": params if isinstance(params, (dict, pd.Series)) else {},
            "intercept": intercept,
            "persistence": persistence,
            "standardized_residuals": std_resid_list,
            "scale": "percent",
            "mean": mean, "vol": vol, "dist": dist, "p": p, "o": o, "q": q,
            "r2": r2, "r2_type": r2_type
        }
        return res, r2, fit_info

    def fit_regime_garch(
        self,
        series: pd.Series,
        regimes: pd.Series,
        min_regime_length: int = 10
    ) -> Tuple[Dict[int, Any], Dict[int, float], Dict[int, Dict[str, Any]], Dict[str, Any]]:
        rets, vols, skew_returns, skew_volatility, _ = self.build_base_features(series)

        summary_df, per_regime_summary_diag, merged = self.summarize_by_regime(
            regimes, rets, vols, skew_returns, skew_volatility, min_regime_length=min_regime_length
        )

        specs, spec_selection_diag = self.select_garch_specs(summary_df)

        models: Dict[int, Any] = {}
        r2_scores: Dict[int, float] = {}
        fit_info: Dict[int, Dict[str, Any]] = {}

        for rid, spec in specs.items():
            g = merged[merged["regime"] == rid]
            ret_series = g["return"]
            vol_series = g["volatility"]
            skew_ret_series = g["skew_returns"]
            skew_vol_series = g["skew_volatility"]

            base_entry = {
                "rationale": spec.get("rationale", ""),
                "mean": spec.get("mean"),
                "vol": spec.get("vol"),
                "dist": spec.get("dist"),
                "p": spec.get("p"),
                "o": spec.get("o"),
                "q": spec.get("q"),
                "lags": spec.get("lags", 0),
            }

            count = len(ret_series)
            if count < min_regime_length:
                fit_info[rid] = {**base_entry, "r2": np.nan, "r2_type": None, "skipped": True,
                                 "skip_reason": f"too short ({count} < {min_regime_length})"}
                continue

            rets_r = ret_series * 100
            try:
                am = arch_model(
                    rets_r,
                    mean=spec["mean"],
                    lags=spec.get("lags", 0),
                    vol=spec["vol"],
                    p=spec["p"], o=spec["o"], q=spec["q"],
                    dist=spec["dist"]
                )
                res = am.fit(disp="off")

                r2_type, r2 = "true", np.nan
                try:
                    fc = res.forecast(horizon=1, reindex=True)
                    if hasattr(fc, "mean") and not fc.mean.empty:
                        if isinstance(fc.mean, pd.DataFrame):
                            y_pred = fc.mean.iloc[:, 0].dropna().reindex(rets_r.index)
                        else:
                            y_pred = fc.mean.dropna().reindex(rets_r.index)
                        if y_pred.notna().sum() > 3:
                            r2 = r2_score(rets_r.loc[y_pred.index], y_pred)
                except Exception:
                    pass

                sm_r, diag_r = self.build_summary_from_metrics(
                    ret_series, vol_series, skew_ret_series, skew_vol_series, garch_result=res
                )

                fit_info[rid] = {
                    **base_entry,
                    "r2": r2, "r2_type": r2_type, "skipped": False,
                    "model_params": diag_r.get("model_params", {}),
                    "intercept": diag_r.get("intercept"),
                    "persistence": diag_r.get("persistence", {}),
                    "library_summary": diag_r.get("library_summary", ""),
                    "standardized_residuals_sample": diag_r.get("standardized_residuals_sample", []),
                    "summary": sm_r.iloc[0].to_dict(),
                    "summary_diagnostics": diag_r.get("summary_diagnostics", {"issues": []}),
                }
                models[rid] = res
                r2_scores[rid] = r2

            except Exception as e:
                fit_info[rid] = {**base_entry, "r2": np.nan, "r2_type": None, "skipped": True,
                                 "skip_reason": f"fit error: {e}"}

        combined_diagnostics = {"summary": per_regime_summary_diag, "spec_selection": spec_selection_diag}
        return models, r2_scores, fit_info, combined_diagnostics
    
    # =========================
    # Summary Reporting
    # =========================
    @staticmethod
    def flatten_fit_info(
        fit_info: Dict[str, Any],
        model_label: str,
        regime_id: Optional[Union[int, str]] = None,
        extra_diagnostics: Optional[Dict[str, Any]] = None
    ) -> pd.DataFrame:
        row: Dict[str, Any] = {
            "model_label": model_label,
            "regime_id": regime_id if regime_id is not None else "baseline",
            "rationale": fit_info.get("rationale", ""),
            "mean": fit_info.get("mean"),
            "vol": fit_info.get("vol"),
            "dist": fit_info.get("dist"),
            "p": fit_info.get("p"),
            "o": fit_info.get("o"),
            "q": fit_info.get("q"),
            "r2": fit_info.get("r2"),
            "r2_type": fit_info.get("r2_type", "variance"),
            "intercept": fit_info.get("intercept"),
            "persistence": fit_info.get("persistence"),
        }

        if fit_info.get("raw_metrics") is not None:
            row["raw_metrics"] = fit_info.get("raw_metrics")

        diagnostics: Dict[str, Any] = {}
        if "summary_diagnostics" in fit_info:
            diagnostics["summary"] = fit_info["summary_diagnostics"]
        for key in ("spec_selection", "fallbacks"):
            if key in fit_info:
                diagnostics[key] = fit_info[key]
        if extra_diagnostics:
            diagnostics.update(extra_diagnostics)
        if diagnostics:
            row["diagnostics"] = diagnostics

        return pd.DataFrame([row]).set_index("model_label")

    def report_baseline_garch(
        self,
        series: pd.Series,
        fit_result: Any,
        fit_info: Dict[str, Any],
        show: bool = True
    ) -> Tuple[Any, pd.DataFrame]:
        rets, _, _, _ = self.compute_metrics(series)
        returns_pct = rets * 100

        meta = self.flatten_fit_info(
            fit_info, model_label="Vanilla", regime_id="vanilla",
            extra_diagnostics=fit_info.get("summary_diagnostics", {})
        )

        try:
            resid = fit_result.resid.dropna()
        except Exception:
            resid = pd.Series(dtype=float)

        denom = resid.std()
        if denom == 0 or np.isnan(denom):
            denom = 1.0
        std_resid = resid / denom

        try:
            cond_vol = fit_result.conditional_volatility
        except AttributeError:
            cond_vol = resid.rolling(20, min_periods=1).std()

        fig = plt.figure(constrained_layout=True, figsize=(14, 10))
        gs = fig.add_gridspec(3, 1, height_ratios=[1, 1, 0.5])

        ax_ret = fig.add_subplot(gs[0, 0])
        ax_ret.plot(returns_pct.index, returns_pct.values, label="Returns", linewidth=1)
        ax_ret.set_title("Vanilla GARCH: Returns")
        ax_ret.legend()

        ax_resid = fig.add_subplot(gs[1, 0], sharex=ax_ret)
        ax_resid.plot(std_resid.index, std_resid.values, label="Std Residuals")
        ax_resid.axhline(0, linestyle="--", alpha=0.6)
        ax_resid.set_title("Vanilla GARCH: Standardized Residuals")
        ax_resid.legend()

        ax_vol = fig.add_subplot(gs[2, 0])
        ax_vol.plot(cond_vol.index, cond_vol.values, label="Cond Vol")
        ax_vol.set_title("Vanilla GARCH: Conditional Volatility")
        ax_vol.legend()

        table_text = meta.to_string(float_format=lambda x: f"{x:.4f}")
        fig.text(0.01, 0.98, "Model comparison:\n" + table_text,
                 fontfamily="monospace", fontsize=8, va="top")

        fig.suptitle("Vanilla GARCH Summary", fontsize=16, weight="bold", y=0.99)

        if show:
            plt.show()
        return fig, meta

    def compare_baseline_vs_regime(
        self,
        result: Dict[str, Any],
        csv_path: str,
        column: str,
        date_col: str,
        regime_id: int,
        precomputed_returns: Optional[pd.Series] = None,
        show: bool = True
    ) -> Tuple[Any, pd.DataFrame]:
        if precomputed_returns is None:
            series = self.load_series(csv_path, column, date_col=date_col)
            returns_pct = self.compute_returns(series) * 100
        else:
            returns_pct = precomputed_returns * 100
            series = self.load_series(csv_path, column, date_col=date_col)

        feat = self.prepare_features(series)

        baseline_entry = result["baseline"]
        baseline_res = baseline_entry["result"]
        baseline_info = baseline_entry["info"]
        baseline_diag = baseline_entry.get("diagnostics", {})

        regime_res = result["regime_models"].get(regime_id)
        regime_info = result["regime_fit_info"].get(regime_id)
        if regime_res is None or regime_info is None:
            raise ValueError(f"Regime {regime_id} not found in result.")

        # regimes align to features, then reindex to returns for plotting mask
        full_regimes = pd.Series(result["regimes_full"], index=feat.index)
        regime_mask = (full_regimes == regime_id)
        mask_aligned = regime_mask.reindex(returns_pct.index).fillna(False).values

        meta_baseline = self.flatten_fit_info(
            baseline_info, model_label="Baseline", regime_id="baseline", extra_diagnostics=baseline_diag
        )

        extra_regime_diag: Dict[str, Any] = {}
        regime_fit_diagnostics = result.get("regime_fit_diagnostics", {})
        if isinstance(regime_fit_diagnostics, dict):
            if "summary" in regime_fit_diagnostics and regime_id in regime_fit_diagnostics["summary"]:
                extra_regime_diag["summary"] = regime_fit_diagnostics["summary"][regime_id].get("issues", {})
            if "spec_selection" in regime_fit_diagnostics and regime_id in regime_fit_diagnostics["spec_selection"]:
                extra_regime_diag["spec_selection"] = regime_fit_diagnostics["spec_selection"][regime_id]

        meta_regime = self.flatten_fit_info(
            regime_info, model_label=f"Regime {regime_id}", regime_id=regime_id,
            extra_diagnostics=extra_regime_diag if extra_regime_diag else None
        )

        meta_combined = pd.concat([meta_baseline, meta_regime])

        def standardize_resid(model_res: Any) -> pd.Series:
            try:
                resid_ = model_res.resid.dropna()
            except Exception:
                return pd.Series(dtype=float)
            d = resid_.std()
            if d == 0 or np.isnan(d):
                d = 1.0
            return resid_ / d

        std_base = standardize_resid(baseline_res)
        std_regime = standardize_resid(regime_res)

        try:
            cond_vol_base = baseline_res.conditional_volatility
        except AttributeError:
            cond_vol_base = baseline_res.resid.dropna().rolling(20, min_periods=1).std()
        try:
            cond_vol_regime = regime_res.conditional_volatility
        except AttributeError:
            cond_vol_regime = regime_res.resid.dropna().rolling(20, min_periods=1).std()

        fig = plt.figure(constrained_layout=True, figsize=(14, 10))
        gs = fig.add_gridspec(3, 2, height_ratios=[1, 1, 0.5])

        ax_ret_base = fig.add_subplot(gs[0, 0])
        ax_ret_regime = fig.add_subplot(gs[0, 1], sharey=ax_ret_base)
        ax_ret_base.plot(returns_pct.index, returns_pct.values, label="Returns", linewidth=1)
        ax_ret_base.set_title("Baseline: Returns")
        ax_ret_base.legend()

        ax_ret_regime.plot(returns_pct.index, returns_pct.values, label="Returns", linewidth=1)
        ax_ret_regime.fill_between(
            returns_pct.index,
            np.nanmin(returns_pct.values),
            np.nanmax(returns_pct.values),
            where=mask_aligned,
            alpha=0.15,
            label=f"Regime {regime_id} active"
        )
        ax_ret_regime.set_title(f"Regime {regime_id}: Returns with Regime Highlight")
        ax_ret_regime.legend()

        ax_resid_base = fig.add_subplot(gs[1, 0], sharex=ax_ret_base)
        ax_resid_regime = fig.add_subplot(gs[1, 1], sharex=ax_ret_regime)
        ax_resid_base.plot(std_base.index, std_base.values, label="Std Residuals")
        ax_resid_base.axhline(0, linestyle="--", alpha=0.6)
        ax_resid_base.set_title("Baseline: Standardized Residuals")
        ax_resid_base.legend()

        ax_resid_regime.plot(std_regime.index, std_regime.values, label="Std Residuals")
        ax_resid_regime.axhline(0, linestyle="--", alpha=0.6)
        ax_resid_regime.set_title(f"Regime {regime_id}: Standardized Residuals")
        ax_resid_regime.legend()

        ax_vol_base = fig.add_subplot(gs[2, 0])
        ax_vol_regime = fig.add_subplot(gs[2, 1])
        ax_vol_base.plot(cond_vol_base.index, cond_vol_base.values, label="Cond Vol")
        ax_vol_base.set_title("Baseline: Conditional Volatility")
        ax_vol_base.legend()

        ax_vol_regime.plot(cond_vol_regime.index, cond_vol_regime.values, label="Cond Vol")
        base_overlay = cond_vol_base.reindex(cond_vol_regime.index)
        ax_vol_regime.plot(base_overlay.index, base_overlay.values, label="Baseline Vol Overlay", linestyle="--", alpha=0.7)
        ax_vol_regime.set_title(f"Regime {regime_id}: Cond Vol (vs Baseline)")
        ax_vol_regime.legend()

        # Render comparison table as text (avoid overlapping subplots)
        table_text = meta_combined.to_string(float_format=lambda x: f"{x:.4f}")
        fig.text(0.01, 0.98, "Model comparison:\n" + table_text,
                 fontfamily="monospace", fontsize=9, va="top")

        subtitle_parts = []
        if baseline_diag:
            subtitle_parts.append(f"Baseline issues: {baseline_diag}")
        if extra_regime_diag:
            subtitle_parts.append(f"Regime {regime_id} issues: {extra_regime_diag}")
        subtitle = " | ".join(subtitle_parts)

        fig.suptitle(
            f"Baseline vs Regime {regime_id} — R² & Rationale\n{subtitle}",
            fontsize=16, weight="bold", y=0.99
        )

        if show:
            plt.show()
        return fig, meta_combined

    # =========================
    # Orchestration
    # =========================
    def run(self, csv_path: str, column: str, date_col: str) -> Dict[str, Any]:
        if self.config is None:
            raise ValueError("Config must be provided.")
        if not all([csv_path, column, date_col]):
            raise ValueError("csv_path, column, and date_col must all be provided.")

        series = self.load_series(csv_path, column, date_col=date_col)

        # 1) Features
        feat = self.prepare_features(series)

        # 2) HMM training + regimes
        try:
            hmm_model, regimes_train, regimes_test, regimes_full, train_dates, test_dates = self.train_test_hmm(feat)
        except Exception as e:
            raise RuntimeError(f"HMM training/inference failed: {e}") from e

        # 3) Holdout regime summary
        test_rets = feat["return"].loc[test_dates]
        test_vols = feat["volatility"].loc[test_dates]
        holdout_summary, holdout_diagnostics = self.summarize_test_regimes(regimes_test, test_rets, test_vols)

        # 4) Baseline vanilla GARCH fits
        base_model, base_r2, base_fit_info = self.fit_baseline_garch(series)
        base_fit_info.setdefault("r2_type", "variance")

        baseline_diagnostics = {
            "summary": base_fit_info.get("summary_diagnostics", {"issues": []}),
            "spec_selection": [],
        }

        # 5) Regime-specific GARCH fits
        regimes_series = pd.Series(regimes_full, index=feat.index)
        regime_models, regime_r2, regime_fit_info, regime_fit_diagnostics = self.fit_regime_garch(
            series, regimes_series
        )

        # 6) Unified summaries
        model_summaries: list[pd.DataFrame] = []
        baseline_flat = self.flatten_fit_info(
            base_fit_info, model_label="Baseline", regime_id="baseline", extra_diagnostics=baseline_diagnostics
        )
        model_summaries.append(baseline_flat)

        for rid, info in regime_fit_info.items():
            extra_diag: Dict[str, Any] = {}
            if isinstance(regime_fit_diagnostics, dict):
                if "summary" in regime_fit_diagnostics and rid in regime_fit_diagnostics["summary"]:
                    extra_diag["summary"] = regime_fit_diagnostics["summary"][rid].get("issues", {"issues": []})
                if "spec_selection" in regime_fit_diagnostics and rid in regime_fit_diagnostics["spec_selection"]:
                    extra_diag["spec_selection"] = regime_fit_diagnostics["spec_selection"][rid]
                if "fallbacks" in regime_fit_diagnostics and rid in regime_fit_diagnostics["fallbacks"]:
                    extra_diag["fallbacks"] = regime_fit_diagnostics["fallbacks"][rid]
            flat = self.flatten_fit_info(
                info, model_label=f"Regime {rid}", regime_id=rid, extra_diagnostics=extra_diag if extra_diag else None
            )
            model_summaries.append(flat)

        model_summaries_df = pd.concat(model_summaries)

        # 7) Return API
        return {
            "hmm_model":               hmm_model,
            "regimes_full":            regimes_full,
            "train_dates":             train_dates,
            "test_dates":              test_dates,
            "holdout_summary":         holdout_summary,
            "holdout_diagnostics":     holdout_diagnostics,
            "baseline": {
                "result": base_model,
                "r2": base_r2,
                "info": base_fit_info,
                "diagnostics": baseline_diagnostics
            },
            "regime_models":           regime_models,
            "regime_r2":               regime_r2,
            "regime_fit_info":         regime_fit_info,
            "regime_fit_diagnostics":  regime_fit_diagnostics,
            "get_regime_series":       lambda result, feat_in: pd.Series(result["regimes_full"], index=feat_in.index),
            "model_summaries":         model_summaries_df,
        }