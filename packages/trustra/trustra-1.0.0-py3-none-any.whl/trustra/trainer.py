# trustra/trainer.py
import optuna
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
import numpy as np

class AutoTrainer:
    def __init__(self, task="classification", timeout=300):
        self.task = task
        self.timeout = timeout
        self.best_model_ = None
        self.best_score_ = 0
        self.best_model_name_ = ""

    def train(self, X, y, X_val=None, y_val=None):
        def objective(trial):
            if self.task == "classification":
                model_name = trial.suggest_categorical("model", ["lr", "rf", "gb"])
                if model_name == "lr":
                    C = trial.suggest_float("C", 1e-3, 1e3, log=True)
                    model = LogisticRegression(C=C, max_iter=2000)
                elif model_name == "rf":
                    n = trial.suggest_int("n_estimators", 50, 200)
                    d = trial.suggest_int("max_depth", 3, 10)
                    model = RandomForestClassifier(n_estimators=n, max_depth=d)
                elif model_name == "gb":
                    n = trial.suggest_int("n_estimators", 50, 200)
                    lr = trial.suggest_float("lr", 0.01, 0.3)
                    model = GradientBoostingClassifier(n_estimators=n, learning_rate=lr)
                return cross_val_score(model, X, y, cv=3, scoring="roc_auc").mean()
            return 0.0

        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=10, n_jobs=1)

        self.best_score_ = study.best_value
        params = study.best_params
        self.best_model_name_ = params.pop("model")

        if self.best_model_name_ == "lr":
            self.best_model_ = LogisticRegression(C=params['C'], max_iter=2000)
        elif self.best_model_name_ == "rf":
            self.best_model_ = RandomForestClassifier(
                n_estimators=params['n_estimators'],
                max_depth=params['max_depth']
            )
        elif self.best_model_name_ == "gb":
            self.best_model_ = GradientBoostingClassifier(
                n_estimators=params['n_estimators'],
                learning_rate=params['lr']
            )

        self.best_model_.fit(X, y)
        return self.best_model_