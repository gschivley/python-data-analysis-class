import pandas as pd


def filter_outliers(df, columns, percentile=0.95):
    """
    Remove top 5% of values from each of the selected columns

    Parameters
    ----------
    df : dataframe
    columns : list
        Column names to perform the filter operation on
    percentile : float
        Value from 0 to 1

    Returns
    -------
    DataFrame
        Filtered dataframe
    """
    filtered_df = df.copy()
    for col in columns:
        filter_value = df[col].quantile(percentile)
        filtered_df = filtered_df.loc[filtered_df[col] < filter_value]

    return filtered_df
