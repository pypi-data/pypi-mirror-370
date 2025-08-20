# trustra/fairness.py
from fairlearn.metrics import demographic_parity_difference, equalized_odds_difference
import pandas as pd

class FairnessAudit:
    def __init__(self, target: str, sensitive_features: list):
        self.target = target
        self.sensitive_features = sensitive_features
        self.report = {}

    def assess(self, df: pd.DataFrame) -> list:
        issues = []
        y = df[self.target]
        X = df.drop(columns=[self.target])

        from sklearn.linear_model import LogisticRegression
        model = LogisticRegression().fit(X, y)
        y_pred = model.predict(X)

        for feat in self.sensitive_features:
            dpd = demographic_parity_difference(y, y_pred, sensitive_features=df[feat])
            eod = equalized_odds_difference(y, y_pred, sensitive_features=df[feat])
            self.report[feat] = {"DPD": dpd, "EOD": eod}
            if dpd > 0.1:
                issues.append(f"High bias in '{feat}': DPD={dpd:.3f}")
        return issues