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


def find_max_tech_capacity(df):

    max_tech = {}

    for plant in capacity['plant_id'].unique():
        tech = sum_cap.loc[plant, 'nameplate_capacity_mw'].idxmax()

        max_tech[plant] = tech

    return max_tech


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

    # Add the technology of maximum capacity for each plant
    max_capacity_tech = find_max_tech_capacity(df, 'plant_id')
    
    df_grouped['technology'] = df_grouped['plant_id'].map(max_capacity_tech)

    return final_df


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
        Clean dataframe of plant generation and primary generation fuel

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

    # Melt generation data so it is stacked vertically rather than in columns
    # Keep generation by plant and fuel type to find the primary fuel
    df_tidy = pd.melt(df, id_vars=['plant_id', 'aer_fuel_type_code'],
                      value_vars=gen_cols, value_name='net_gen_mwh',
                      var_name='month')

    # Find primary fuel, group tidy data to plant level, merge in primary fuel
    primary_fuel = find_primary_gen_fuel(df_tidy)
    df_tidy = df_tidy.groupby(['plant_id', 'month'], as_index=False).sum()
    df_tidy = df_tidy.merge(primary_fuel, on='plant_id')

    df_tidy['month'] = df_tidy.month.str.replace('netgen_', '')

    # Change month from names to integer values and re-sort
    month_map = {month: idx for idx, month in enumerate(calendar.month_name)}
    df_tidy['month'] = df_tidy.month.str.capitalize().map(month_map)
    df_tidy.sort_values(by=['plant_id', 'month'], inplace=True)
    df_tidy.reset_index(drop=True, inplace=True)

    return df_tidy


def find_primary_gen_fuel(df):
    """
    Determine which fuel generated the most electricity at each power plant
    in 2016

    Parameters
    ----------
    df : dataframe
        Dataframe with monthly generation by facility and fuel type

    Returns
    -------
    DataFrame
        Clean dataframe of primary generation fuel at each plant
    """
    # Sum the generation for each plant by fuel across the entire year
    df_fuel = (df.groupby(['plant_id', 'aer_fuel_type_code'], as_index=False)
                 .sum())

    # Find the dataframe index for the fuel with the most gen at each plant
    # Use this to slice the dataframe and return plant code and primary fuel
    primary_fuel_idx = df_fuel.groupby('plant_id')['net_gen_mwh'].idxmax()
    primary_fuel = df_fuel.loc[primary_fuel_idx,
                               ['aer_fuel_type_code', 'plant_id']]

    primary_fuel.rename(columns={'aer_fuel_type_code': 'primary_gen_fuel'},
                        inplace=True)

    return primary_fuel
