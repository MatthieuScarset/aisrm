"""Data preprocessing module for the AISRM project.

This module contains functions to clean, transform, and prepare sales data
for analysis and modeling.
"""

import pandas as pd
import unidecode

from src.config import RAW_DATA_PATH, PROCESSED_DATA_PATH


def classify_opportunity(row):
    """Classify opportunity status based on engagement and close dates."""
    if pd.isna(row["engage_date"]):
        return "initial"
    if pd.isna(row["close_date"]):
        return "in_progress"
    return "completed"


def _opportunity_status_binary(value):
    """Convert opportunity status to binary (1 for completed, 0 otherwise)."""
    return int(1 if value.lower() == "completed" else 0)


def _clean_string(value):
    """Helper method to clean a given string"""
    return (
        unidecode.unidecode(value.strip().lower()) if isinstance(value, str) else value
    )


def clean_string_columns(df, columns):
    """
    Clean string columns in a DataFrame:
    - Strip whitespace
    - Convert to lowercase
    - Remove accents/special characters
    """
    for col in columns:
        if col in df.columns:
            df[col] = df[col].apply(_clean_string)

    return df


def preprocess():
    """Main preprocessing function to clean and transform sales data."""
    df_accounts = pd.read_csv(RAW_DATA_PATH + "/accounts.csv")
    df_products = pd.read_csv(RAW_DATA_PATH + "/products.csv")
    df_teams = pd.read_csv(RAW_DATA_PATH + "/sales_teams.csv")
    df_sales = pd.read_csv(RAW_DATA_PATH + "/sales_pipeline.csv")

    df = df_sales.copy()

    # Do not remove NaN for now.
    # Cleaner to do this directly within the data pipeline.
    # @see https://shorturl.at/B0Abu
    # df.dropna(subset=["close_value", "account"], inplace=True)

    # Better status of the sale, based on dates.
    df["opportunity_status"] = df.apply(classify_opportunity, axis=1)
    df["won"] = df["opportunity_status"].apply(_opportunity_status_binary)
    df["won"] = pd.to_numeric(df["won"], downcast="integer")

    # Get the duration
    df["engage_date"] = pd.to_datetime(df["engage_date"])
    df["close_date"] = pd.to_datetime(df["close_date"])
    df["duration"] = (df["close_date"] - df["engage_date"]).dt.days
    df["duration"] = pd.to_numeric(df["duration"], downcast="integer")

    # Merge information about Sale agent.
    columns = ["sales_agent", "manager", "regional_office"]
    if "manager" not in df.columns:
        df = pd.merge(df, df_teams[columns], on="sales_agent", how="left")

    # Merge information about Account (i.e. clients).
    columns = ["account", "sector", "revenue", "office_location"]
    if "sector" not in df.columns:
        df = pd.merge(df, df_accounts[columns], on="account", how="left")

    # Merge information about Product (i.e. catalog).
    columns = ["product", "series", "sales_price"]
    if "series" not in df.columns:
        df = pd.merge(df, df_products[columns], on="product", how="left")

    # Reorder columns.
    cols = list(df.columns)
    cols.remove("product")
    cols.remove("series")
    cols.remove("sales_price")
    cols.remove("duration")
    cols.remove("won")
    cols.remove("close_value")

    cols.append("product")
    cols.append("series")
    cols.append("sales_price")
    cols.append("duration")
    cols.append("won")
    cols.append("close_value")
    df = df[cols]

    # Remove useless columns.
    for col in ["opportunity_id", "engage_date", "close_date", "deal_stage"]:
        if col in df.columns:
            df.drop(columns=[col], inplace=True)

    # All object columns are just text.
    for col in (df.select_dtypes(include=["object"])).columns:
        df[col] = df[col].astype("string")

    string_columns = df.select_dtypes(include=["string"])
    df = clean_string_columns(df, list(string_columns))

    # Our target is a number.
    df["close_value"] = pd.to_numeric(df["close_value"], downcast="integer")

    target_file = PROCESSED_DATA_PATH + "/dataset.csv"
    df.to_csv(target_file)
    print(f"🤝 Preprocessed dataset exported: {target_file}")


def main():
    """Main method of this module"""
    preprocess()


if __name__ == "__main__":
    main()
