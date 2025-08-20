def adjust_sf_df(df):
    # Lowercase column names
    df.columns = [col.lower() for col in df.columns]
    return df
