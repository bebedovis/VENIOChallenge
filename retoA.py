import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Union

class Predictor(ABC): 
    def __init__(self, data_path: Path, num_skus = 3) -> None:
        self.df = self._load_data(data_path)
        self.skus = self._get_top_skus(self.df,num_skus)
        self.skus_week_count = self._get_count_by_week(self.df, self.skus) 
        # averae between 8 and 12 jeje
        self.n_weeks_future = 10
        # Cross validation for time series
        self.cv_results = []
    @staticmethod
    def _load_data(data_path: Path): 
        df = pd.read_csv(data_path, parse_dates=["date"], dayfirst = True)
        df = df.drop_duplicates()
        df =df.dropna(subset =["sell_in_quantity","sell_in_amount"])
        df = df[df["sell_in_quantity"] > 0]
        return df

    @staticmethod
    def _get_top_skus(df,n: int):
        """
        Return the skus with the most data to make the challenge a little bit easier jeje 
        """
        return df.groupby("product_name").size().nlargest(n).index.tolist()
    @staticmethod
    def _get_count_by_week(df, skus: list[str]):
        data = {}
        groups = df.set_index("date").groupby("product_name")["sell_in_quantity"].resample("W-SUN").sum()
        for sku in skus:
            subset = groups.loc[sku]
            data[sku] = {
                "week_count": subset,
                "num_weeks": len(subset),
            }
        return data
    @staticmethod
    def wape(actual: np.ndarray, forecast: np.ndarray) -> float:
        return np.abs(actual - forecast).sum() / np.abs(actual).sum()

    def cross_validate(self):
        self.cv_results = {}
        for sku, info in self.skus_week_count.items():
            week_count = info["week_count"]
            num_weeks = info["num_weeks"]
            self.cv_results[sku] = []

            for origin in range(52, num_weeks - self.n_weeks_future, 8):

                train_split= week_count.iloc[:origin].values.astype(float)
                val_split = week_count.iloc[origin: origin + self.n_weeks_future].values
                weeks = np.arange(origin, origin + self.n_weeks_future)

                model = self.fit(train_split)
                pred = self.predict(model, weeks)

                self.cv_results[sku].append({
                    "origin": origin,
                    "wape": self.wape(val_split, pred),
                    "mae": np.abs(val_split- pred).mean(),
                })
    @abstractmethod
    def predict(self,model, weeks) -> np.ndarray:
        pass
    @abstractmethod
    def fit(self,train_split) -> Union[None,LinearRegression]:
        pass

    def forecast(self,sku,week_future):

        # just predicts all data points after the maximum week
        num_weeks = self.skus_week_count[sku]["num_weeks"]
        train_split = self.skus_week_count[sku]["week_count"]
        weeks = np.arange(num_weeks, num_weeks + week_future)
        model =self.fit(train_split)

        return self.predict(model, weeks)
    def process_cv_results(self):
        summary_dict = {}
        for sku, stats in self.cv_results.items():
            wapes = [s["wape"] for s in stats]
            maes = [s["mae"] for s in stats]
            summary_dict[sku] = {
                "num_folds": len(stats),
                "avg_wape": np.mean(wapes),
                "min_wape": np.min(wapes),
                "max_wape": np.max(wapes),
                "avg_mae": np.mean(maes),
                "min_mae": np.min(maes),
                "max_mae": np.max(maes),
            }
        return summary_dict



class Baseline(Predictor):
    def __init__(self, data_path: Path, num_skus=3, n_average=4) -> None:
        super().__init__(data_path, num_skus)
        self.n = n_average

    def predict(self, model, weeks):
        start = max(weeks[0] - self.n, 0)
        return np.full(len(weeks), model[start:weeks[0]].mean())

    def fit(self,train_split): 
        return train_split


class Harmonic(Predictor):
    def __init__(self, data_path: Path, num_skus=3, n_harmonics=2, period=52) -> None:
        super().__init__(data_path, num_skus)
        self.n_harmonics = n_harmonics
        # period poer year
        self.period = period

    def extract_features(self, t: np.ndarray) -> np.ndarray:
        """
        Transform data into t cos/sin(2*pi*k*t/T) 
        """
        features = [t.astype(float)]
        for k in range(1, self.n_harmonics + 1):
            features.append(np.sin(2*np.pi*k*t/self.period))
            features.append(np.cos(2*np.pi*k*t/self.period))
        return np.column_stack(features)

    def fit(self, train_split):
        # just transforming the data into a list opf integers [0,...,week] 
        # then using the count as my target value
        weeks = np.array(range(len(train_split)))
        X_train = self.extract_features(weeks) 
        model = LinearRegression()
        model.fit(X_train, train_split)
        return model

    def predict(self, model, weeks):
        preds = model.predict(self.extract_features(weeks))
        return np.clip(preds, a_min=0, a_max=None) #clipping negative vals, because doesnt make sense



def main():
    data_path = "assets/20260806_prueba_tecnica_dataset.csv"
    models = {
        "Baseline": Baseline(data_path), 
        "Harmonic": Harmonic(data_path)
    }

    summaries = {}
    for name, model in models.items():
        model.cross_validate()
        summaries[name] = model.process_cv_results()

    for sku in models["Baseline"].skus:
        for name in models:
            s = summaries[name][sku]
            print(f"{sku} [{name}]: folds={s['num_folds']}  "
                  f"WAPE avg={s['avg_wape']:.1%} (min={s['min_wape']:.1%}, max={s['max_wape']:.1%})  "
                  f"MAE avg={s['avg_mae']:.1f}")

        chosen_name = min(models, key=lambda name: summaries[name][sku]["avg_wape"])
        chosen_model = models[chosen_name]
        forecast = chosen_model.forecast(sku, chosen_model.n_weeks_future)
        print(f"  -> chosen: {chosen_name}  forecast next {chosen_model.n_weeks_future} weeks: {forecast.round(0)}")
        print()

if __name__=="__main__":
    main()


