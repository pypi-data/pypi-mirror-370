from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple, Union

import numpy as np
from fairlearn.metrics import equalized_odds_difference as fl_equalized_odds_difference

ArrayLike = Sequence[Any]


def _validate_lengths(*arrays: Sequence[Any]) -> None:
	lengths = [len(a) for a in arrays if a is not None]
	if len(set(lengths)) > 1:
		raise ValueError("All input arrays must have the same length.")


def equalized_odds_gap(
	y_true: ArrayLike,
	y_pred: ArrayLike,
	group: ArrayLike,
	*,
	method: str = "between_groups",
	agg: str = "mean",
	sample_weight: Optional[ArrayLike] = None,
) -> float:
	"""
	Wrapper around fairlearn.metrics.equalized_odds_difference to compute EO gap for a single attribute.

	Parameters mirror Fairlearn's API partially. Default agg='mean' matches our original definition
	(average of TPR and FPR differences). Use agg='worst_case' to emulate Fairlearn's default.
	"""
	_validate_lengths(y_true, y_pred, group)
	return float(
		fl_equalized_odds_difference(
			y_true=y_true,
			y_pred=y_pred,
			sensitive_features=group,
			method=method,
			sample_weight=sample_weight,
			agg=agg,
		)
	)


def generalized_equalized_odds(
	y_true: ArrayLike,
	y_pred: ArrayLike,
	*,
	sensitive_features: Union[ArrayLike, Mapping[str, ArrayLike], None] = None,
	method: str = "between_groups",
	agg: str = "mean",
	sample_weight: Optional[ArrayLike] = None,
) -> Tuple[Dict[str, float], float]:
	"""
	Compute EO gaps per sensitive feature and return (per_feature_eo, GEO).

	- If sensitive_features is a 1D array, computes EO for a single unnamed attribute ('attr_0').
	- If a dict mapping names to arrays, computes EO for each and sums to GEO.
	- If None, returns empty dict and GEO=0.
	"""
	if sensitive_features is None:
		return {}, 0.0

	per_feature: Dict[str, float] = {}
	if isinstance(sensitive_features, dict):
		for name, feat in sensitive_features.items():
			_validate_lengths(y_true, y_pred, feat)
			per_feature[name] = equalized_odds_gap(
				y_true, y_pred, feat, method=method, agg=agg, sample_weight=sample_weight
			)
	else:
		per_feature["attr_0"] = equalized_odds_gap(
			y_true, y_pred, sensitive_features, method=method, agg=agg, sample_weight=sample_weight
		)

	geo = float(sum(per_feature.values()))
	# Guard to [0, +inf); typical EO gaps are in [0,1] per feature
	if geo < 0.0:
		geo = 0.0
	return per_feature, geo
