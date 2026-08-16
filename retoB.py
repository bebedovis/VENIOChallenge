import pandas as pd
import numpy as np
import statsmodels.api as sm


def filter_data(df):
    df =df.dropna(subset =["sell_in_quantity","sell_in_amount"])
    df =df.drop_duplicates()
    return df[(df["sell_in_quantity"] > 0) &(df["sell_in_amount"]>0)]

def aggregate_features_weekly(df):
    df = df.assign(day=df["date"])  # keep a plain column: "date" itself becomes the index below
    groups = df.set_index("date").groupby("product_name").resample("W-SUN").agg(
        quantity =("sell_in_quantity","sum"),
        amount = ("sell_in_amount", "sum"),
        cost = ("product_cost","sum"),
        bruto =("bruto","sum"),
        days_covered=("day","nunique"),
    )
    empty_weeks = groups["days_covered"] == 0
    full_weeks = groups.index[groups["days_covered"] == 7]

    groups.loc[empty_weeks, ["quantity", "amount", "cost", "bruto"]] = np.nan
    groups["unit_price"] = groups["amount"]/groups["quantity"]
    groups["unit_cost"]= groups["cost"]/groups["quantity"]
    groups["bruto_price"] =groups["bruto"]/groups["quantity"]
    return groups.loc[full_weeks.min():full_weeks.max()]
    
def select_largest_variance_sku(weekly_report):
    stats = weekly_report.groupby(level="product_name")["unit_price"].agg(["mean", "std"])
    stats["var_coeff"] = stats["std"] / stats["mean"]
    sku = stats["var_coeff"].idxmax()
    return weekly_report.loc[sku], sku


def main():
    df = pd.read_csv("assets/20260806_prueba_tecnica_dataset.csv", parse_dates=["date"], dayfirst=True)
    df = filter_data(df)
    df_weekly = aggregate_features_weekly(df)
    df_weekly, sku = select_largest_variance_sku(df_weekly)
    # X values

    weeks = np.array(range(len(df_weekly)))
    log_price = np.log(df_weekly["unit_price"].values)
    features = [log_price,weeks.astype(float)]
    # annual expected variance coefficients
    # features.append(np.sin(2*np.pi*weeks/52)) jeje only cosine harmonic pass the p-value
    features.append(np.cos(2*np.pi*weeks/52))

    X = sm.add_constant(np.column_stack(features))
    # target 
    y = np.log(df_weekly["quantity"].values)
    print(X.shape,y.shape)

    model = sm.OLS(y,X).fit()
    print(model.summary())
    print(model.params[1],model.conf_int()[1])

if __name__ =="__main__":
    main()
