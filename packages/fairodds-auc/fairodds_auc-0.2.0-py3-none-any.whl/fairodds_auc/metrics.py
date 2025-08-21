from __future__ import annotations

from typing import Any, Optional, Sequence, Union, Mapping

import numpy as np
from sklearn.metrics import roc_auc_score

from .fairness import generalized_equalized_odds


def _as_numpy_float(array: Sequence[Any]) -> np.ndarray:
	if isinstance(array, np.ndarray):
		return array.astype(float, copy=False)
	return np.asarray(list(array), dtype=float)


def _as_numpy_int(array: Sequence[Any]) -> np.ndarray:
	if isinstance(array, np.ndarray):
		return array.astype(int, copy=False)
	return np.asarray(list(array), dtype=int)


def _safe_auroc(y_true: Sequence[int], y_score: Sequence[float]) -> float:
	try:
		return float(roc_auc_score(y_true, y_score))
	except Exception:
		# Undefined AUROC (e.g., single-class y_true). Use 0.5 by convention.
		return 0.5


def fair_odds_auc(
	*,
	y_true: Sequence[int],
	y_score: Sequence[float],
	sensitive_features: Optional[Union[Sequence[Any], Mapping[str, Sequence[Any]]]] = None,
	lambda_: float = 1.0,
	threshold: float = 0.5,
	method: str = "between_groups",
	agg: str = "mean",
	sample_weight: Optional[Sequence[float]] = None,
) -> float:
	"""
	Compute FairOdds-AUC = AUROC / (1 + lambda * GEO).

	GEO is the sum of equalized odds differences across provided sensitive features.
	`sensitive_features` accepts either a single array-like, or a dict of name->array-like.
	EO is computed from hard predictions derived by thresholding scores at `threshold`.
	"""
	if lambda_ < 0:
		raise ValueError("lambda_ must be nonnegative")

	y_true_np = _as_numpy_int(y_true)
	y_score_np = _as_numpy_float(y_score)

	if y_true_np.shape[0] != y_score_np.shape[0]:
		raise ValueError("y_true and y_score must have the same length")

	auroc = _safe_auroc(y_true_np, y_score_np)
	y_pred_np = (y_score_np >= float(threshold)).astype(int)

	geo = 0.0
	if sensitive_features is not None:
		_, geo = generalized_equalized_odds(
			y_true_np,
			y_pred_np,
			sensitive_features=sensitive_features,
			method=method,
			agg=agg,
			sample_weight=sample_weight,
		)

	denom = 1.0 + float(lambda_) * float(geo)
	score = float(auroc) / denom
	return max(0.0, min(1.0, score))
