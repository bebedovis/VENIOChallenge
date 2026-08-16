import os 
from retoA import Harmonic
from cleanData import load_data
from retoB import aggregate_features_weekly
from sklearn.linear_model import LinearRegression
import numpy as np

def evaluate_promo(model,promo, week):
    pass

def main():
    df = load_data()
    # training a model without combos 
    sku = "Desodorante 150 ml A"
    df = df[df["product_name"] == sku]
    df_nc= df[df["combo"].isna()]

    df_weekly = aggregate_features_weekly(df_nc)
    weeks = np.array(range(len(df_weekly)))

    # I only use one harmonic because of the previous retoB where it seems that theres no statistical evidence for more --> Not a good thing just I am lazy jeje
    features = np.column_stack(
        [weeks.astype(float), np.cos(2*np.pi*weeks/52)]
    )

    model = LinearRegression()
    y = np.log(df_weekly["quantity"].values)
    model.fit(features,y)
    combos = df.dropna(subset=["combo"])




if __name__ =="__main__":
    main()
