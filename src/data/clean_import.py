import pandas as pd
import calendar


def import_epa_emissions(path):
    """
    Read and clean the EPA emissions file.

    Parameters
    ----------
    path : str or path object
        Path to the epa emissions file

    Returns
    -------
    DataFrame
        Clean dataframe of EPA emissions

    """

    df = pd.read_csv(path, index_col=False)

    df.columns = ((df.columns.str.strip()
                             .str.lower()
                             .str.replace(' ', '_')
                             .str.replace('.', '')
                             .str.replace('-', '')
                             .str.replace('(', '')
                             .str.replace(')', '')))

    df.rename(columns={'facility_id_orispl': 'plant_id'}, inplace=True)

    return df


def import_plant_capacity(path):
    """
    Read and clean the EIA 860 monthly file with capacity data.

    Parameters
    ----------
    path : str or path object
        Path to the EIA 860 monthly file

    Returns
    -------
    DataFrame
        Clean dataframe of plant capacity grouped by facility

    """

    df = pd.read_excel(path, sheet_name='Operable', header=1, na_values=[' '],
                       skipfooter=1)

    df.columns = ((df.columns.str.strip()
                             .str.lower()
                             .str.replace(' ', '_')
                             .str.replace('-', '')
                             .str.replace('(', '')
                             .str.replace(')', '')
                             .str.replace('/', '_')))

    df.rename(columns={'plant_code': 'plant_id'}, inplace=True)

    # Group data to facility level. Use state in the grouping to keep the data.
    df_grouped = df.groupby(['plant_id', 'state'], as_index=False).sum()
    # df_grouped = df_grouped.merge(df['state'], on='plant_id')

    return df_grouped


def import_plant_generation(path):
    """
    Read and clean the EIA 923 file with generation data.

    Parameters
    ----------
    path : str or path object
        Path to the EIA 923 file

    Returns
    -------
    DataFrame
        Clean dataframe of plant generation

    """

    df = pd.read_excel(path, header=5, na_values='.')

    df.columns = ((df.columns.str.strip()
                             .str.lower()
                             .str.replace('\n', ' ')
                             .str.replace(' ', '_')
                             .str.replace('-', '')
                             .str.replace('(', '')
                             .str.replace(')', '')))

    gen_cols = [col for col in df.columns if 'netgen' in col]

    df = (pd.melt(df, id_vars=['plant_id'],
                  value_vars=gen_cols, value_name='net_gen_mwh',
                  var_name='month')
            .groupby(['plant_id', 'month'],
                     as_index=False).sum())

    df['month'] = df.month.str.replace('netgen_', '')

    # Change month from names to integer values and re-sort
    month_map = {month: idx for idx, month in enumerate(calendar.month_name)}
    df['month'] = df.month.str.capitalize().map(month_map)
    df.sort_values(by=['plant_id', 'month'], inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df
