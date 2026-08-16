import os 
from retoA import Harmonic
from cleanData import load_data
from retoB import aggregate_features_weekly
from sklearn.linear_model import LinearRegression
import numpy as np

def evaluate_promo(model,nominal_margin,df_weekly, promo_mask):
    weeks = np.arange(len(df_weekly))
    promo_weeks = weeks[promo_mask]
    features = np.column_stack([promo_weeks,np.cos(2*np.pi*promo_weeks/52)])
    y_pred = model.predict(features)

    qty_pred=np.exp(y_pred)

    actual_qty = df_weekly["quantity"].values[promo_mask]
    unit_cost = df_weekly["unit_cost"].values[promo_mask]

    actual_amount = df_weekly["amount"].values[promo_mask]
    actual_cost = df_weekly["cost"].values[promo_mask]

    pred_margin = (qty_pred*unit_cost*nominal_margin).sum()
    actual_margin = (actual_amount-actual_cost).sum()

    incremented_margin = actual_margin - pred_margin 
    return incremented_margin
def main():
    df = load_data()
    # training a model without combos 
    sku = "Desodorante 150 ml A"
    df = df[df["product_name"] == sku]
    df_weekly = aggregate_features_weekly(df)
    dates = df_weekly.index.get_level_values("date")

    is_promo_week = (
        df.set_index("date")["combo"].notna()
        .resample("W-SUN").max()
        .reindex(dates, fill_value=False)
        .values
    )
    weeks = np.array(range(len(df_weekly)))

    # I only use one harmonic because of the previous retoB where it seems that theres no statistical evidence for more --> Not a good thing just I am lazy jeje
    features = np.column_stack(
        [weeks.astype(float), np.cos(2*np.pi*weeks/52)]
    )

    model = LinearRegression()
    y = np.log(df_weekly["quantity"].values)
    model.fit(features[~is_promo_week],y[~is_promo_week])
    nominal_margin = df["product_margin"].iloc[0]

    for combo_name in df["combo"].dropna().unique():
        combo_dates = df.loc[df["combo"] ==combo_name,"date"]
        in_range = (dates >= combo_dates.min()) & (dates <= combo_dates.max())
        promo_mask = is_promo_week & in_range
        incremented_margin= evaluate_promo(model,nominal_margin,df_weekly, promo_mask)
        print(f"{combo_name} got an increment in margin of {incremented_margin}") 





if __name__ =="__main__":
    main()
