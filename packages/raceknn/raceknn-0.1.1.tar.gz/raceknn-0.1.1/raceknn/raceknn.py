# raceknn.py
# Cleaned & optimized implementation of RACER + rule-guided kNN (RACEkNN)
# - Preserves original structure & naming (RACERPreprocessor, RACER, raceknn idea)
# - Adds fit/transform API, boolean features, 1D int labels
# - Removes per-sample KNN refits (uses fast Hamming distance on candidates)
# - Provides a scikit-learn compatible classifier: RACEKNNClassifier

from __future__ import annotations

from typing import Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd

# -------- optional deps (kept optional to ease install) --------
try:
    from sklearn.base import BaseEstimator, ClassifierMixin
    from sklearn.metrics import accuracy_score
    from sklearn.utils.validation import check_is_fitted
    from sklearn.utils.multiclass import unique_labels
    from sklearn.utils import check_array, check_X_y
    from sklearn.preprocessing import LabelEncoder
    SKLEARN_AVAILABLE = True
except Exception:
    BaseEstimator, ClassifierMixin = object, object  # type: ignore
    accuracy_score = None
    check_is_fitted = lambda *a, **k: None
    unique_labels = None
    check_array = lambda x, **k: np.asarray(x)
    check_X_y = lambda X, y, **k: (np.asarray(X), np.asarray(y))
    class LabelEncoder:
        def fit(self, y): 
            self.classes_ = pd.Series(y).astype("category").cat.categories.to_numpy()
            return self
        def transform(self, y):
            return pd.Series(y).astype("category").cat.codes.to_numpy()
        def inverse_transform(self, yi):
            return np.asarray(self.classes_)[np.asarray(yi, dtype=int)]
    SKLEARN_AVAILABLE = False

try:
    from optbinning import MulticlassOptimalBinning as MOB, MDLP
    OPTBIN_AVAILABLE = True
except Exception:
    OPTBIN_AVAILABLE = False


# ============================================================
#  Utilities
# ============================================================

def _as_bool(X: np.ndarray) -> np.ndarray:
    """Ensure contiguous boolean array."""
    if X.dtype != np.bool_:
        X = X.astype(bool, copy=False)
    return np.ascontiguousarray(X)

def _hamming_count_bool(x: np.ndarray, Y: np.ndarray) -> np.ndarray:
    """Hamming distance as count of differing bits for boolean arrays."""
    return np.bitwise_xor(x, Y).sum(axis=1).astype(np.int32)

def _xnor(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """XNOR over boolean arrays; equivalent to (a == b)."""
    return ~(np.bitwise_xor(a, b))


# ============================================================
#  Preprocessing
# ============================================================

class RACERPreprocessor:
    """
    RACER preprocessing:
      - Numeric columns -> discretized bins (optbinning if available; else quantiles/uniform fallback)
      - Categorical columns -> one-hot encoding
      - Output X is boolean np.ndarray
      - y is 1D int labels (LabelEncoder)

    Parameters
    ----------
    target : {'auto','binary','multiclass'}, default 'auto'
    max_n_bins : int, default 32
    max_num_splits : int, default 32
    strategy_if_no_optbin : {'quantile','uniform'}, default 'quantile'
    """

    def __init__(
        self,
        target: str = "auto",
        max_n_bins: int = 32,
        max_num_splits: int = 32,
        strategy_if_no_optbin: str = "quantile",
    ):
        assert target in {"auto", "binary", "multiclass"}
        assert strategy_if_no_optbin in {"quantile", "uniform"}
        self.target = target
        self.max_n_bins = int(max_n_bins)
        self.max_num_splits = int(max_num_splits)
        self.strategy_if_no_optbin = strategy_if_no_optbin

        self._fitted = False
        self._numeric_cols: List[str] = []
        self._cat_cols: List[str] = []
        self._bin_edges: Dict[str, np.ndarray] = {}
        self._cat_levels: Dict[str, List[str]] = {}
        self._y_enc = LabelEncoder()

    def _infer_target(self, y: Union[pd.Series, np.ndarray]) -> str:
        if self.target != "auto":
            return self.target
        n = pd.Series(y).nunique()
        return "binary" if n == 2 else "multiclass"

    def fit(self, X: Union[pd.DataFrame, np.ndarray], y: Union[pd.Series, np.ndarray]):
        X = pd.DataFrame(X).copy()
        y = pd.Series(y).copy()

        self._y_enc.fit(y)
        self.classes_ = getattr(self._y_enc, "classes_", None)

        self._numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
        self._cat_cols = [c for c in X.columns if c not in self._numeric_cols]

        task = self._infer_target(y)
        y_int = self._y_enc.transform(y)

        # Learn bin edges for each numeric column
        for col in self._numeric_cols:
            xcol = X[col].to_numpy()
            if OPTBIN_AVAILABLE:
                if task == "multiclass":
                    qb = MOB(max_n_bins=self.max_n_bins)  # correct param name
                else:
                    qb = MDLP(max_candidates=self.max_num_splits)
                qb.fit(xcol, y_int)
                splits = getattr(qb, "splits", None)
                splits = np.array(splits) if splits is not None else np.array([])
                edges = np.unique(np.concatenate(([xcol.min()-1e-9], splits, [xcol.max()+1e-9])))
            else:
                # Fallback: quantiles or uniform
                if self.strategy_if_no_optbin == "quantile":
                    q = np.linspace(0, 1, num=min(self.max_n_bins, max(2, len(np.unique(xcol)))) + 1)
                    edges = np.unique(np.quantile(xcol, q))
                else:
                    edges = np.linspace(xcol.min()-1e-9, xcol.max()+1e-9, num=self.max_n_bins+1)
                if len(edges) < 2:
                    edges = np.array([xcol.min()-1e-9, xcol.max()+1e-9])
            self._bin_edges[col] = edges

        # Memorize categorical levels (as strings)
        for col in self._cat_cols:
            levels = pd.Series(X[col], dtype="object").astype("string").fillna("").unique().tolist()
            self._cat_levels[col] = sorted(levels)

        self._fitted = True
        return self

    def _transform_X(self, X: Union[pd.DataFrame, np.ndarray]) -> np.ndarray:
        X = pd.DataFrame(X).copy()

        # numeric -> bins
        binned = {}
        for col in self._numeric_cols:
            edges = self._bin_edges[col]
            binned[col] = pd.cut(X[col], bins=edges, include_lowest=True, labels=False).astype("Int64")

        # categorical -> normalized strings, unknown -> "__UNK__"
        cats = {}
        for col in self._cat_cols:
            seen = set(self._cat_levels[col])
            ser = pd.Series(X[col], dtype="object").astype("string").fillna("")
            ser = ser.where(ser.isin(seen), other="__UNK__")
            cats[col] = ser

        Xq = pd.DataFrame({**binned, **cats})
        Xoh = pd.get_dummies(Xq, dummy_na=False, sparse=False)
        return _as_bool(Xoh.to_numpy())

    def transform(
        self,
        X: Union[pd.DataFrame, np.ndarray],
        y: Optional[Union[pd.Series, np.ndarray]] = None
    ) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        assert self._fitted, "Call fit() first."
        Xb = self._transform_X(X)
        yb = None if y is None else self._y_enc.transform(pd.Series(y))
        return Xb, yb

    def fit_transform(
        self,
        X: Union[pd.DataFrame, np.ndarray],
        y: Union[pd.Series, np.ndarray]
    ) -> Tuple[np.ndarray, np.ndarray]:
        return self.fit(X, y).transform(X, y)


# ============================================================
#  RACER (boolean rules)
# ============================================================

class RACER:
    """
    Rule-based classifier over boolean features.
    y is 1D integer labels; internally we use one-hot for rule consequents.
    """

    def __init__(self, alpha: float = 0.9, suppress_warnings: bool = False, benchmark: bool = False):
        self._alpha = float(alpha)
        self._beta = 1.0 - float(alpha)
        self._suppress_warnings = bool(suppress_warnings)
        self._benchmark = bool(benchmark)
        self._has_fit = False

    @staticmethod
    def _covered(X: np.ndarray, rule_if: np.ndarray) -> np.ndarray:
        # Instance is covered if for every bit j: (not x_j) or (x_j and rule_j)
        # -> reduce across features with all/AND
        return ( (~X) | (rule_if & X) ).all(axis=1)

    @staticmethod
    def _onehot(y_int: np.ndarray, n_classes: int) -> np.ndarray:
        oh = np.zeros((len(y_int), n_classes), dtype=bool)
        oh[np.arange(len(y_int)), y_int] = True
        return oh

    def fit(self, X: np.ndarray, y_int: np.ndarray) -> "RACER":
        if self._benchmark:
            from time import perf_counter
            t0 = perf_counter()

        X = _as_bool(X)
        self._X = X
        self._n, self._d = X.shape

        y_int = np.asarray(y_int, dtype=int).ravel()
        self._classes = np.unique(y_int)
        self._n_classes = int(self._classes.max()) + 1 if len(self._classes) else 1
        self._y_oh = RACER._onehot(y_int, self._n_classes)

        # indices per class
        self._class_indices = {c: np.where(y_int == c)[0] for c in self._classes}

        # Initial extants
        self._ext_if = self._X.copy()
        self._ext_then = self._y_oh.copy()
        self._ext_covered = np.zeros(self._n, dtype=bool)
        self._fitness = np.empty(self._n, dtype=float)

        # Precompute fitness
        for i in range(self._n):
            self._fitness[i] = self._fitness_fn(self._ext_if[i], self._ext_then[i])

        # Compose within class
        for c, idxs in self._class_indices.items():
            m = len(idxs)
            for i in range(m):
                for j in range(i + 1, m):
                    self._maybe_compose(idxs[i], idxs[j])

        # Keep non-covered
        keep = ~self._ext_covered
        self._ext_if = self._ext_if[keep]
        self._ext_then = self._ext_then[keep]
        self._fitness = self._fitness[keep]

        # Generalize
        self._generalize_extants()

        # Sort by fitness (desc, stable)
        order = np.argsort(-self._fitness, kind="stable")
        self._final_rules_if = self._ext_if[order]
        self._final_rules_then = self._ext_then[order]
        self._fitness = self._fitness[order]

        # Remove redundant rules
        self._finalize_rules()

        self._has_fit = True
        if self._benchmark:
            from time import perf_counter
            self._bench_time = perf_counter() - t0
        return self

    def _fitness_fn(self, rule_if: np.ndarray, rule_then: np.ndarray) -> float:
        covered = RACER._covered(self._X, rule_if)
        n_cov = covered.sum()
        if n_cov == 0:
            return 0.0
        y_cov = self._y_oh[covered]
        n_ok = (_xnor(y_cov, rule_then).all(axis=1)).sum()
        acc = n_ok / n_cov
        cov = n_cov / self._n
        return float(self._alpha * acc + self._beta * cov)

    def _maybe_compose(self, i: int, j: int):
        if self._ext_covered[i] or self._ext_covered[j]:
            return
        # same label?
        if not _xnor(self._ext_then[i], self._ext_then[j]).all():
            return
        comp = (self._ext_if[i] | self._ext_if[j])
        f = self._fitness_fn(comp, self._ext_then[i])
        if f > max(self._fitness[i], self._fitness[j]):
            # mark covered rules in the same class
            c = int(self._ext_then[i].argmax())
            same = self._class_indices[c]
            cov = RACER._covered(self._ext_if[same], comp)
            self._ext_covered[same[cov]] = True
            # keep composition at i
            self._ext_if[i] = comp
            self._fitness[i] = f
            self._ext_covered[i] = False

    def _generalize_extants(self):
        # Flip zeros to ones when fitness improves
        for i in range(len(self._ext_if)):
            cur = self._ext_if[i].copy()
            best = self._fitness[i]
            for j in range(self._d):
                if not cur[j]:
                    cur[j] = True
                    f = self._fitness_fn(cur, self._ext_then[i])
                    if f > best:
                        best = f
                        self._ext_if[i, j] = True
                        self._fitness[i] = best
                    else:
                        cur[j] = False

    def _finalize_rules(self):
        # Remove rules covered by earlier stronger rules
        temp_if = self._final_rules_if
        temp_then = self._final_rules_then
        temp_fit = self._fitness
        i = 0
        while i < len(temp_if) - 1:
            mask = np.ones(len(temp_if), dtype=bool)
            covered = RACER._covered(temp_if[i + 1:], temp_if[i])
            mask[i + 1:][covered] = False
            temp_if, temp_then, temp_fit = temp_if[mask], temp_then[mask], temp_fit[mask]
            i += 1
        self._final_rules_if, self._final_rules_then, self._fitness = temp_if, temp_then, temp_fit

    # ---------- Inference ----------
    def predict(self, X: np.ndarray, convert_dummies: bool = True) -> np.ndarray:
        assert self._has_fit, "RACER has not been fit yet."
        X = _as_bool(X)
        labels = np.zeros((len(X), self._final_rules_then.shape[1]), dtype=bool)
        found = np.zeros(len(X), dtype=bool)
        for i in range(len(self._final_rules_if)):
            covered = RACER._covered(X, self._final_rules_if[i])
            idx = covered & (~found)
            if idx.any():
                labels[idx] = self._final_rules_then[i]
                found[idx] = True
            if found.all():
                break
        if not found.all():
            # fallback: majority class during training
            majority = self._y_oh.sum(axis=0).argmax()
            labels[~found] = False
            labels[~found, majority] = True
        if convert_dummies:
            labels = labels.argmax(axis=-1)
        return labels

    # ---- RACEkNN helpers (kept close to your originals, but vectorized) ----
    def _closest_match_if(self, x: np.ndarray, gum: float = 0.6) -> np.ndarray:
        """Return indices of rules sorted by mixed score (coverage + fitness)."""
        x = _as_bool(x.reshape(1, -1))[0]
        overlap = ((~x) | (self._final_rules_if & x)).sum(axis=1) / self._final_rules_if.shape[1]
        fit = self._fitness / (self._fitness.max() + 1e-9)
        scores = gum * overlap + (1 - gum) * fit
        return np.argsort(-scores)  # indices sorted descending

    def precompute_rule_train_cover(self, X_train: np.ndarray) -> np.ndarray:
        """Boolean matrix [n_rules, n_train] of which train rows each rule covers."""
        X_train = _as_bool(X_train)
        covers = []
        for i in range(len(self._final_rules_if)):
            covers.append(RACER._covered(X_train, self._final_rules_if[i]))
        return np.stack(covers, axis=0)  # [n_rules, n_train]

    def raceknn(
        self,
        X: np.ndarray,
        X_train: np.ndarray,
        y_train_int: np.ndarray,
        kmeasure: int,
        gum: float = 0.6,
        rule_train_cover: Optional[np.ndarray] = None
    ) -> List[np.ndarray]:
        """
        Original idea: for each X[i], collect training indices covered by rules that cover X[i],
        and if < kmeasure, keep adding closest rules' covers until we have >= kmeasure.
        Returns a list of boolean masks (one per test row) over X_train.
        (Kept for parity with your original loop, but now vectorized and deterministic.)
        """
        assert self._has_fit, "RACER has not been fit yet."
        X = _as_bool(X)
        X_train = _as_bool(X_train)
        y_train_int = np.asarray(y_train_int).ravel()

        if rule_train_cover is None:
            rule_train_cover = self.precompute_rule_train_cover(X_train)

        n_test = len(X)
        masks: List[np.ndarray] = [None] * n_test  # type: ignore

        # Iterate rules once to label & note coverage
        found = np.zeros(n_test, dtype=bool)
        x_rule_mask = np.zeros((n_test, len(self._final_rules_if)), dtype=bool)
        for r in range(len(self._final_rules_if)):
            covered = RACER._covered(X, self._final_rules_if[r])
            x_rule_mask[:, r] = covered
            found |= covered
            if found.all():
                break

        # For each test row, union train covers from matched rules; if not enough, extend with closest rules
        for i in range(n_test):
            matched = np.where(x_rule_mask[i])[0]
            if len(matched) == 0:
                matched = self._closest_match_if(X[i], gum=gum)
            mask = np.zeros(len(X_train), dtype=bool)
            for r in matched:
                mask |= rule_train_cover[r]
                if mask.sum() >= kmeasure:
                    break
            if mask.sum() == 0:
                # Fallback: all train (rare)
                mask[:] = True
            masks[i] = mask
        return masks


# ============================================================
#  A scikit-learn compatible estimator (recommended)
# ============================================================

class RACEKNNClassifier(BaseEstimator, ClassifierMixin):  # type: ignore[misc]
    """
    A hybrid classifier: RACER rules guide a KNN vote (Hamming distance on boolean features).

    Parameters
    ----------
    alpha : float, default 0.9
        Coverage/accuracy trade-off for RACER fitness.
    k : int, default 3
        Number of neighbors for the KNN vote.
    kmin_candidates : int or None, default None
        Minimum candidate pool size per test point (if None, uses k).
    gum : float, default 0.6
        Mix between coverage and rule fitness when searching closest rules.
    target : {'auto','binary','multiclass'}, default 'auto'
        Preprocessor target mode.
    max_n_bins : int, default 32
        Numeric bin upper bound (optbinning or fallback).
    max_num_splits : int, default 32
        MDLP max candidates (binary target).
    strategy_if_no_optbin : {'quantile','uniform'}, default 'quantile'
        Fallback binning strategy when optbinning is unavailable.
    """

    def __init__(
        self,
        alpha: float = 0.9,
        k: int = 3,
        kmin_candidates: Optional[int] = None,
        gum: float = 0.6,
        target: str = "auto",
        max_n_bins: int = 32,
        max_num_splits: int = 32,
        strategy_if_no_optbin: str = "quantile",
    ):
        self.alpha = alpha
        self.k = k
        self.kmin_candidates = kmin_candidates
        self.gum = gum
        self.target = target
        self.max_n_bins = max_n_bins
        self.max_num_splits = max_num_splits
        self.strategy_if_no_optbin = strategy_if_no_optbin

        # set in fit
        self.prep_: Optional[RACERPreprocessor] = None
        self.racer_: Optional[RACER] = None
        self.rule_train_cover_: Optional[np.ndarray] = None
        self.classes_: Optional[np.ndarray] = None
        self.X_train_: Optional[np.ndarray] = None
        self.y_train_int_: Optional[np.ndarray] = None

    # sklearn API
    def fit(self, X: Union[pd.DataFrame, np.ndarray], y: Union[pd.Series, np.ndarray]):
        X, y = check_X_y(X, y, accept_sparse=False, dtype=None)
        self.prep_ = RACERPreprocessor(
            target=self.target,
            max_n_bins=self.max_n_bins,
            max_num_splits=self.max_num_splits,
            strategy_if_no_optbin=self.strategy_if_no_optbin,
        )
        Xb, yi = self.prep_.fit_transform(X, y)
        self.classes_ = getattr(self.prep_._y_enc, "classes_", None)

        self.racer_ = RACER(alpha=self.alpha).fit(Xb, yi)
        self.X_train_ = Xb
        self.y_train_int_ = yi
        self.rule_train_cover_ = self.racer_.precompute_rule_train_cover(self.X_train_)
        return self

    def predict(self, X: Union[pd.DataFrame, np.ndarray]) -> np.ndarray:
        check_is_fitted(self, attributes=["racer_", "prep_", "rule_train_cover_", "X_train_", "y_train_int_"])
        X = check_array(X, accept_sparse=False, dtype=None)
        Xb, _ = self.prep_.transform(X, None)  # type: ignore
        kmin = self.k if self.kmin_candidates is None else max(self.k, self.kmin_candidates)

        # Build candidate masks with the same logic as RACER.raceknn
        masks = self.racer_.raceknn(  # type: ignore
            Xb, self.X_train_, self.y_train_int_, kmeasure=kmin, gum=self.gum, rule_train_cover=self.rule_train_cover_
        )

        # Perform KNN vote with fast Hamming distance on candidates
        y_pred = np.empty(len(Xb), dtype=int)
        for i in range(len(Xb)):
            mask = masks[i]
            cand_X = self.X_train_[mask]
            cand_y = self.y_train_int_[mask]
            d = _hamming_count_bool(Xb[i], cand_X)
            k = min(self.k, len(d))
            if k == 0:
                # fallback: majority class in training set
                vals, counts = np.unique(self.y_train_int_, return_counts=True)
                y_pred[i] = int(vals[counts.argmax()])
                continue
            idx = np.argpartition(d, kth=k-1)[:k]
            idx = idx[np.argsort(d[idx], kind="stable")]
            votes = cand_y[idx]
            vals, counts = np.unique(votes, return_counts=True)
            y_pred[i] = int(vals[counts.argmax()])

        # Map back to original labels if available
        if self.classes_ is not None:
            return np.asarray(self.classes_)[y_pred]
        return y_pred

    def score(self, X: Union[pd.DataFrame, np.ndarray], y: Union[pd.Series, np.ndarray]) -> float:
        if accuracy_score is None:
            raise ImportError("scikit-learn is required to use score().")
        y_pred = self.predict(X)
        return float(accuracy_score(y, y_pred))
