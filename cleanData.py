import pandas as pd 

def load_data(): 
    df = pd.read_csv("assets/20260806_prueba_tecnica_dataset.csv", parse_dates=["date"], dayfirst=True)
    df =df.dropna(subset =["sell_in_quantity","sell_in_amount"])
    df =df.drop_duplicates()
    return df[(df["sell_in_quantity"] > 0) &(df["sell_in_amount"]>0)]
