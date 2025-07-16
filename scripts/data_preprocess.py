from scripts.config import RAW_DATA_PATH, PROCESSED_DATA_PATH
import pandas as pd
import unidecode

DATA_FOLDER = "data"

def classify_opportunity(row):
    if pd.isna(row["engage_date"]):
        return "initial"
    elif pd.isna(row["close_date"]):
        return "in_progress"
    else:
        return "completed"

def opportunity_status_binary(value):
    return int(1 if value.lower() == 'completed' else 0)

def clean_string_columns(df, columns):
    """
    Clean string columns in a DataFrame:
    - Strip whitespace
    - Convert to lowercase
    - Remove accents/special characters
    - Skip columns in exclude_columns
    """
    for col in columns:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: unidecode.unidecode(
                x.strip().lower()) if isinstance(x, str) else x)

    return df

def preprocess():
    df_accounts = pd.read_csv(RAW_DATA_PATH + "/accounts.csv")
    df_products = pd.read_csv(RAW_DATA_PATH + "/products.csv")
    df_teams = pd.read_csv(RAW_DATA_PATH + "/sales_teams.csv")
    df_sales = pd.read_csv(RAW_DATA_PATH + "/sales_pipeline.csv")

    df = df_sales.copy()

    # Remove NaN.
    df.dropna(subset=['close_value', 'account'], inplace=True)

    # Better status of the sale, based on dates.
    df['opportunity_status'] = df.apply(classify_opportunity, axis=1)
    df['won'] = df['opportunity_status'].apply(opportunity_status_binary)      
    df['won'] = pd.to_numeric(df['won'], downcast='integer')
    
    # Get the duration
    df['engage_date'] = pd.to_datetime(df['engage_date'])
    df['close_date'] = pd.to_datetime(df['close_date'])
    df['duration'] = (df['close_date'] - df['engage_date']).dt.days
    df['duration'] = pd.to_numeric(df['duration'], downcast='integer')

    # Merge information about Sale agent.
    columns = ['sales_agent', 'manager', 'regional_office']
    if 'manager' not in df.columns:
        df = pd.merge(
            df, df_teams[columns], on='sales_agent', how='left')

    # Merge information about Account (i.e. clients).
    columns = ['account', 'sector', 'revenue', 'office_location']
    if 'sector' not in df.columns:
        df = pd.merge(
            df, df_accounts[columns], on='account', how='left')

    # Merge information about Product (i.e. catalog).
    columns = ['product', 'series', 'sales_price']
    if 'series' not in df.columns:
        df = pd.merge(
            df, df_products[columns], on='product', how='left')

    # Reorder columns.
    cols = list(df.columns)
    cols.remove('product')
    cols.remove('series')
    cols.remove('sales_price')
    cols.remove('duration')
    cols.remove('won')
    cols.remove('close_value')

    cols.append('product')
    cols.append('series')
    cols.append('sales_price')
    cols.append('duration')
    cols.append('won')
    cols.append('close_value')
    df = df[cols]

    # Remove useless columns.
    for col in ['opportunity_id', 'engage_date', 'close_date', 'deal_stage']:
        if col in df.columns:
            df.drop(columns=[col], inplace=True)

    # All object columns are just text.
    for col in (df.select_dtypes(include=['object'])).columns:
        df[col] = df[col].astype('string')

    string_columns = df.select_dtypes(include=['string'])
    df = clean_string_columns(df, list(string_columns))
    
    # Our target is a number.
    df['close_value'] = pd.to_numeric(df['close_value'], downcast='integer')

    target_file = PROCESSED_DATA_PATH + '/dataset.csv'
    df.to_csv(target_file)
    print(f"🤝 Preprocessed dataset exported: {target_file}")

if __name__ == '__main__':
    preprocess()