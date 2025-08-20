# trustra/validator.py
import pandas as pd
import numpy as np

def validate_data_quality(df: pd.DataFrame, target: str) -> list:
    issues = []
    missing = df.isnull().sum()
    if missing.sum() > 0:
        issues.append(f"Missing values: {missing[missing > 0].to_dict()}")
    dup = df.duplicated().sum()
    if dup > 0:
        issues.append(f"Found {dup} duplicate rows.")
    if df[target].dtype in ['object', 'int'] and df[target].nunique() < 10:
        counts = df[target].value_counts(normalize=True)
        if counts.min() < 0.05:
            issues.append(f"Class imbalance: {counts.to_dict()}")
    return issues

def detect_leakage(df: pd.DataFrame, target: str) -> list:
    if df[target].dtype not in ['float64', 'int64']:
        return []
    corr = df.corr()[target].abs()
    leaks = corr[(corr > 0.95) & (corr.index != target)]
    return [f"Potential data leakage in '{k}' (corr={v:.3f})" for k, v in leaks.items()]