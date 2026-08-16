import pandas as pd
import numpy as np
import statsmodels.api as sm
from cleanData import load_data


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
    # Se supone que es constante
    groups["unit_cost"]= groups["cost"]/groups["quantity"]
    groups["bruto_price"] =groups["bruto"]/groups["quantity"]
    return groups.loc[full_weeks.min():full_weeks.max()]
    
def select_largest_variance_sku(weekly_report):
    stats = weekly_report.groupby(level="product_name")["unit_price"].agg(["mean", "std"])
    stats["var_coeff"] = stats["std"] / stats["mean"]
    sku = stats["var_coeff"].idxmax()
    return weekly_report.loc[sku], sku

def simulator(model,df_week,nominal_margin):
    min_price = df_week["unit_price"].min()
    max_price = df_week["unit_price"].max()
    last_product_cost = df_week["unit_cost"].iloc[-1]
    last_week = len(df_week)
    while True:
        raw = input(f"Choose a number between {min_price:.2f} and {max_price:.2f}, press q for quiting: ")
        if raw == "q":
            break
        try:
            price = float(raw)
        except ValueError:
            print("Please input a number")
            continue
        if price<min_price or price>max_price:
            print("Please select a number inside the prices")
            continue
        # same column order as training: [const, log_price, weeks, cos_term]
        X = np.array([[1.0, np.log(price), last_week, np.cos(2*np.pi*last_week/52)]])
        y = model.predict(X)
        quantity = int(np.exp(y[0]))
        ingreso = round(quantity*price,2)
        cost = round(quantity*last_product_cost,2)
        margin = round(ingreso-cost,2)
        margin_percentage = round(margin/ingreso,4)*100
        markup = (price - last_product_cost) / last_product_cost 
        print(f"Expected demand: {quantity} units")
        print(f"Expected ingreso: {ingreso}")
        print(f"Expected cost: {cost}")
        print(f"Expected margin: {margin} {margin_percentage}%")
        print(f"Markup at this price: {markup:.1%}  (SKU's nominal markup: {nominal_margin:.1%})")


def main():
    df = load_data()
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
    print("Calculated elasticity:")
    print(model.params[1],model.conf_int()[1])
    nominal_margin = df.loc[df["product_name"] == sku, "product_margin"].iloc[0]
    simulator(model,df_weekly,nominal_margin)

if __name__ =="__main__":
    main()
