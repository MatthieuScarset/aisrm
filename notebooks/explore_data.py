import pandas as pd

# Load CSVs
df_pipeline = pd.read_csv("crm-sales-opportunities/sales_pipeline.csv")
df_accounts = pd.read_csv("crm-sales-opportunities/accounts.csv")
df_products = pd.read_csv("crm-sales-opportunities/products.csv")
df_teams = pd.read_csv("crm-sales-opportunities/sales_teams.csv")

# Show shape and preview of each dataset
print("Sales Pipeline:")
display(df_pipeline.head())

print("Accounts:")
display(df_accounts.head())

print("Products:")
display(df_products.head())

print("Sales Teams:")
display(df_teams.head())
