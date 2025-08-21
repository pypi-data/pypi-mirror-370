### FairOdds-AUC

FairOdds-AUC is a fairness-scaled AUROC metric that multiplicatively penalizes equalized-odds gaps across user-specified sensitive attributes. It enables a single, tunable score that balances utility and fairness via a nonnegative temperature parameter λ.

Formula:
- FairOdds-AUC = AUROC / (1 + λ · GEO)
- GEO = sum over sensitive attributes of Equalized Odds differences (per Fairlearn)

When λ = 0, the score reduces to AUROC. Larger λ puts more weight on fairness, discounting models with larger equalized-odds disparities.

### Installation

```bash
pip install fairodds-auc
```

From source (editable):

```bash
pip install -U pip
pip install -e .
```

### Quickstart

```python
import numpy as np
from fairodds_auc import fair_odds_auc

y_true = np.array([0, 1, 0, 1, 0, 1])
y_score = np.array([0.1, 0.9, 0.3, 0.8, 0.2, 0.7])

# any attributes you care about
race = np.array(["A", "A", "B", "B", "A", "B"]) 
sex = np.array(["F", "M", "F", "M", "F", "M"])   

sensitive_features = {"race": race, "sex": sex}

score = fair_odds_auc(
    y_true=y_true,
    y_score=y_score,
    sensitive_features=sensitive_features,
    lambda_=1.0,
    threshold=0.5,
    agg="mean",  # or 'worst_case' to match Fairlearn default
)
print(score)
```

### API

- `fair_odds_auc(y_true, y_score, sensitive_features, lambda_=1.0, threshold=0.5, method='between_groups', agg='mean', sample_weight=None) -> float`
- `equalized_odds_gap(y_true, y_pred, group, method='between_groups', agg='mean', sample_weight=None) -> float`
- `generalized_equalized_odds(y_true, y_pred, sensitive_features, method='between_groups', agg='mean', sample_weight=None) -> (dict, float)`

Notes:
- EO uses hard decisions `y_pred` from thresholding `y_score`.
- EO is computed using `fairlearn.metrics.equalized_odds_difference` under the hood.
- Pass `sensitive_features` as a single array-like or a dict of name->array-like.

### References
- Fong et al. (2022): Bias-penalized AUC (fairAUC)
- Pfohl et al. (2021): Balancing performance and fairness in clinical ML
- Dehdashtian et al. (2024): U-FaTE multi-objective framework

### License
MIT
