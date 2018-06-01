import pandas as pd


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
        Clean dataframe of plant capacity

    """

    df = pd.read_excel(path, sheet_name='Operating', header=1, na_values=[' '],
                       skipfooter=1)

    df.columns = ((df.columns.str.strip()
                             .str.lower()
                             .str.replace(' ', '_')
                             .str.replace('-', '')
                             .str.replace('(', '')
                             .str.replace(')', '')))

    return df


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
                  value_vars=gen_cols, value_name='net_gen',
                  var_name='month')
            .groupby(['plant_id', 'month'],
                     as_index=False).sum())

    df['month'] = df.month.str.replace('netgen_', '')

    return df
