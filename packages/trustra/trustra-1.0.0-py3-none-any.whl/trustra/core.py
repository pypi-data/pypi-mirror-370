# trustra/core.py
import pandas as pd
from typing import Optional
import logging

from .validator import validate_data_quality, detect_leakage
from .fairness import FairnessAudit
from .trainer import AutoTrainer
from .reporter import TrustReport

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrustRA:
    """
    TrustRA: Trust-First Automated Machine Learning.
    One fit(). Full trust.
    """

    def __init__(
        self,
        target: str,
        sensitive_features: list = None,
        task: str = None,
        timeout: int = 300
    ):
        self.target = target
        self.sensitive_features = sensitive_features or []
        self.task = task
        self.timeout = timeout
        self.trainer_ = None
        self.fairness_ = None
        self.report_ = None
        self.best_model_ = None
        self.issues = []

    def fit(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: pd.DataFrame = None,
        y_val: pd.Series = None
    ):
        logger.info("🚀 Starting TrustRA Pipeline...")

        # Step 1: Combine data
        train_data = X_train.copy()
        train_data[self.target] = y_train.values

        val_data = None
        if X_val is not None:
            val_data = X_val.copy()
            val_data[self.target] = y_val.values

        # Step 2: Data Quality
        logger.info("🔍 Checking data quality...")
        self.issues.extend(validate_data_quality(train_data, self.target))
        self.issues.extend(detect_leakage(train_data, self.target))

        if X_val is not None:
            from scipy.stats import ks_2samp
            for col in X_train.columns:
                p = ks_2samp(X_train[col].dropna(), X_val[col].dropna()).pvalue
                if p < 0.05:
                    self.issues.append(f"Drift detected in '{col}' (p={p:.2e})")

        # Step 3: Fairness
        if self.sensitive_features:
            logger.info("⚖️  Auditing fairness...")
            self.fairness_ = FairnessAudit(self.target, self.sensitive_features)
            fairness_issues = self.fairness_.assess(train_data)
            self.issues.extend(fairness_issues)

        # Step 4: Task inference
        if self.task is None:
            self.task = "classification" if y_train.nunique() < 20 else "regression"

        # Step 5: Train model
        logger.info("🧠 Training best model...")
        self.trainer_ = AutoTrainer(task=self.task, timeout=self.timeout)
        self.best_model_ = self.trainer_.train(X_train, y_train, X_val, y_val)

        # Step 6: Generate report
        logger.info("📊 Generating trust report...")
        self.report_ = TrustReport(
            issues=self.issues,
            cv_score=self.trainer_.best_score_,
            model_type=self.trainer_.best_model_name_,
            task=self.task,
            fairness_report=getattr(self.fairness_, "report", None)
        ).generate()

        # Loud metrics for your resume
        print("\n" + "="*50)
        print("✅ TRUSTRA PIPELINE COMPLETE")
        print(f"📈 Accuracy (CV AUC): {self.trainer_.best_score_:.3f}")
        print(f"⚖️  Fairness Issues: {len([i for i in self.issues if 'bias' in i.lower()])}")
        print(f"🔍 Total Issues Found: {len(self.issues)}")
        print(f"📄 Trust Report: {self.report_}")
        print("="*50)

        return self

    def predict(self, X):
        return self.best_model_.predict(X)

    def predict_proba(self, X):
        return self.best_model_.predict_proba(X)