import pandas as pd

def load_data():
    path = "data/raw/crm-sales-opportunities/"
    pipeline = pd.read_csv(path + "sales_pipeline.csv")
    accounts = pd.read_csv(path + "accounts.csv")
    products = pd.read_csv(path + "products.csv")
    # Merge the dataframes on shared keys
    df = pipeline.merge(accounts, on="account", how="left")
    df = df.merge(products, on="product", how="left")
    df.dropna(inplace=True)
    return df

if __name__ == "__main__":
    df = load_data()
    print(df.columns)
