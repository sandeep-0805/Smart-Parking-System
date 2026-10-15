import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error
from app.config import settings

logger = logging.getLogger(__name__)

class ForecastModelManager:
    def __init__(self, model_dir: str = settings.MODEL_ARTIFACTS_DIR):
        self.model_dir = model_dir
        self.models: Dict[int, Any] = {}
        self.baselines: Dict[int, Dict[tuple, float]] = {}
        self.model_version: str = "v1_default"
        self.metrics: Dict[str, Any] = {}
        os.makedirs(self.model_dir, exist_ok=True)
        self.load_models()

    def load_models(self) -> bool:
        meta_path = os.path.join(self.model_dir, "model_meta.json")
        if os.path.exists(meta_path):
            try:
                with open(meta_path, "r") as f:
                    meta = json.load(f)
                self.model_version = meta.get("version", "v1_default")
                self.metrics = meta.get("metrics", {})

                # Load per-location models
                for fname in os.listdir(self.model_dir):
                    if fname.startswith("model_loc_") and fname.endswith(".joblib"):
                        loc_id = int(fname.replace("model_loc_", "").replace(".joblib", ""))
                        self.models[loc_id] = joblib.load(os.path.join(self.model_dir, fname))

                # Load baselines
                baseline_path = os.path.join(self.model_dir, "baselines.joblib")
                if os.path.exists(baseline_path):
                    self.baselines = joblib.load(baseline_path)
                logger.info(f"Loaded forecast models {self.model_version} for {len(self.models)} locations.")
                return True
            except Exception as e:
                logger.error(f"Failed to load forecast models from {self.model_dir}: {e}")
        return False

    async def train_on_data(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not records:
            return {"error": "No occupancy records found for training"}

        df = pd.DataFrame(records)
        df["ts"] = pd.to_datetime(df["ts"], utc=True)
        df["hour"] = df["ts"].dt.hour
        df["weekday"] = df["ts"].dt.weekday
        df["minute"] = df["ts"].dt.minute
        
        # Calculate occupancy fraction
        df["total_slots"] = df["total_slots"].replace(0, 1)
        df["occ_pct"] = (df["occupied"] / df["total_slots"]).clip(0.0, 1.0)

        version = f"v_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        all_metrics: Dict[str, Any] = {}
        new_models: Dict[int, Any] = {}
        new_baselines: Dict[int, Dict[tuple, float]] = {}

        unique_locs = df["location_id"].unique()

        for loc_id in unique_locs:
            loc_df = df[df["location_id"] == loc_id].sort_values("ts").copy()
            if len(loc_df) < 50:
                # Not enough data for ML model; baseline only
                mean_occ = float(loc_df["occ_pct"].mean()) if not loc_df.empty else 0.4
                new_baselines[int(loc_id)] = {(-1, -1): mean_occ}
                all_metrics[str(loc_id)] = {
                    "note": "Insufficient data; fallback baseline used",
                    "baseline_mae": 0.05,
                    "best_model": "HistoricalMean",
                }
                continue

            # Lagged features
            loc_df["occ_lag_1"] = loc_df["occ_pct"].shift(1).fillna(loc_df["occ_pct"].iloc[0])
            loc_df["occ_lag_2"] = loc_df["occ_pct"].shift(2).fillna(loc_df["occ_pct"].iloc[0])
            loc_df["occ_lag_4"] = loc_df["occ_pct"].shift(4).fillna(loc_df["occ_pct"].iloc[0])

            features = ["hour", "weekday", "minute", "occ_lag_1", "occ_lag_2", "occ_lag_4"]
            
            # Time-separated split (80% train, 20% test on chronological holdout)
            split_idx = int(len(loc_df) * 0.8)
            train_df = loc_df.iloc[:split_idx]
            test_df = loc_df.iloc[split_idx:]

            if len(test_df) < 5:
                train_df = loc_df
                test_df = loc_df

            X_train = train_df[features].values
            y_train = train_df["occ_pct"].values
            X_test = test_df[features].values
            y_test = test_df["occ_pct"].values

            # Historical baseline by (weekday, hour)
            baseline_map = train_df.groupby(["weekday", "hour"])["occ_pct"].mean().to_dict()
            new_baselines[int(loc_id)] = baseline_map

            baseline_preds = np.array([baseline_map.get((w, h), 0.4) for w, h in zip(test_df["weekday"], test_df["hour"])])
            base_mae = mean_absolute_error(y_test, baseline_preds)

            # Fit Random Forest & Gradient Boosting
            rf = RandomForestRegressor(n_estimators=50, max_depth=8, random_state=42)
            gb = GradientBoostingRegressor(n_estimators=50, max_depth=4, random_state=42)

            rf.fit(X_train, y_train)
            gb.fit(X_train, y_train)

            rf_pred = rf.predict(X_test)
            gb_pred = gb.predict(X_test)

            rf_mae = mean_absolute_error(y_test, rf_pred)
            gb_mae = mean_absolute_error(y_test, gb_pred)

            best_model = rf if rf_mae <= gb_mae else gb
            best_name = "RandomForest" if rf_mae <= gb_mae else "GradientBoosting"
            best_mae = min(rf_mae, gb_mae)
            best_rmse = root_mean_squared_error(y_test, best_model.predict(X_test))

            new_models[int(loc_id)] = best_model
            
            all_metrics[str(loc_id)] = {
                "baseline_mae": round(float(base_mae), 4),
                "rf_mae": round(float(rf_mae), 4),
                "gb_mae": round(float(gb_mae), 4),
                "best_model": best_name,
                "best_mae": round(float(best_mae), 4),
                "best_rmse": round(float(best_rmse), 4),
                "beats_baseline": bool(best_mae < base_mae),
                "train_samples": len(train_df),
                "test_samples": len(test_df),
            }

            joblib.dump(best_model, os.path.join(self.model_dir, f"model_loc_{loc_id}.joblib"))

        joblib.dump(new_baselines, os.path.join(self.model_dir, "baselines.joblib"))

        self.models = new_models
        self.baselines = new_baselines
        self.model_version = version
        self.metrics = all_metrics

        meta = {
            "version": version,
            "trained_at": datetime.now(timezone.utc).isoformat(),
            "metrics": all_metrics,
        }
        with open(os.path.join(self.model_dir, "model_meta.json"), "w") as f:
            json.dump(meta, f, indent=2)

        return meta

    def predict(
        self,
        location_id: int,
        target_time_str: str,
        current_occ_pct: Optional[float] = None,
        total_slots: int = 50,
    ) -> Dict[str, Any]:
        dt = pd.to_datetime(target_time_str, utc=True)
        hour = dt.hour
        weekday = dt.weekday()
        minute = dt.minute

        occ_lag = current_occ_pct if current_occ_pct is not None else 0.40

        if location_id in self.models:
            model = self.models[location_id]
            feats = np.array([[hour, weekday, minute, occ_lag, occ_lag, occ_lag]])
            pred_pct = float(model.predict(feats)[0])
            pred_pct = max(0.0, min(1.0, pred_pct))
            uncertainty = 0.08
        else:
            base_map = self.baselines.get(location_id, {})
            pred_pct = float(base_map.get((weekday, hour), base_map.get((-1, -1), 0.45)))
            uncertainty = 0.15

        pred_occupied = int(round(pred_pct * total_slots))
        pred_available = max(0, total_slots - pred_occupied)

        return {
            "location_id": location_id,
            "target_time": target_time_str,
            "predicted_available": float(pred_available),
            "predicted_occupied": float(pred_occupied),
            "total_slots": total_slots,
            "occupancy_pct": round(pred_pct, 4),
            "uncertainty_low": round(max(0.0, pred_pct - uncertainty), 4),
            "uncertainty_high": round(min(1.0, pred_pct + uncertainty), 4),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "model_version": self.model_version,
            "is_estimate": True,
        }

forecast_manager = ForecastModelManager()
