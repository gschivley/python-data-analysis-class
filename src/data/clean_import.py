import pandas as pd
import calendar
from data.convert_units import unit_conversion


def clean_columns(columns):
    'Remove special characters and convert to snake case'
    clean = (columns.str.lower()
                    .str.replace('[^0-9a-zA-Z\-]+', ' ')
                    .str.replace('-', '')
                    .str.strip()
                    .str.replace(' ', '_'))
    return clean


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

    df.columns = clean_columns(df.columns)

    df.rename(columns={'facility_id_orispl': 'plant_id'}, inplace=True)

    # Convert from tons to kg and drop old columns
    emiss_cols = ['so2_tons', 'nox_tons', 'co2_short_tons']
    emiss_names = ['so2', 'nox', 'co2']
    for name, col in zip(emiss_names, emiss_cols):
        metric_col = '{}_kg'.format(name)
        df[metric_col] = unit_conversion(value=df[col],
                                         start_unit='tons',
                                         final_unit='kg')
    df.drop(columns=emiss_cols, inplace=True)

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
        Clean dataframe of plant generation and primary generation fuel

    """

    df = pd.read_excel(path, header=5, na_values='.')

    df.columns = clean_columns(df.columns)

    gen_cols = [col for col in df.columns if 'netgen' in col]

    # Melt generation data so it is stacked vertically rather than in columns
    # Keep generation by plant and fuel type to find the primary fuel
    melt_id_vars = ['plant_id', 'aer_fuel_type_code', 'nerc_region']
    df_tidy = pd.melt(df, id_vars=melt_id_vars, value_vars=gen_cols,
                      value_name='net_gen_mwh', var_name='month')

    # Find primary fuel, group tidy data to plant level, merge in primary fuel
    primary_fuel = find_primary_gen_fuel(df_tidy)
    df_tidy = df_tidy.groupby(['plant_id', 'month', 'nerc_region'],
                              as_index=False).sum()
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

    primary_fuel.rename(columns={'aer_fuel_type_code': 'primary_fuel'},
                        inplace=True)

    return primary_fuel


####################
# Functions below are for importing/cleaning EIA-860 generator capacity data
def find_max_tech_capacity(capacity):
    """
    Calculate the technology with greatest capacity at each plant.

    Parameters
    ----------
    capacity : DataFrame
        dataframe with capacity by generator at every plant

    Returns
    -------
    dictionary
        mapping of plant_id to the technology with largest total capacity

    """

    sum_cap = capacity.groupby(['plant_id', 'technology']).sum()
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

    df.columns = clean_columns(df.columns)

    df.rename(columns={'plant_code': 'plant_id'}, inplace=True)

    # Group data to facility level. Use state in the grouping to keep the data.
    df_grouped = df.groupby(['plant_id', 'state'], as_index=False).sum()

    # Add the technology of maximum capacity for each plant
    max_capacity_tech = find_max_tech_capacity(df)

    df_grouped['technology'] = df_grouped['plant_id'].map(max_capacity_tech)

    return df_grouped
