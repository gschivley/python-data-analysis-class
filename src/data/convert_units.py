

def unit_conversion(value, start_unit, final_unit):
    """
    Convert a value from one unit to another (e.g. short tons to kg)

    Parameters
    ----------
        value: numeric or array-like
            value to convert
        start_unit: str
            kg, tons, or lbs
        final_unit: str
            kg, tons, or lbs

    Returns
    -------
        converted_value: numeric or array-like
    """

    # All values are for conversion to kg
    convert_dict = {
        'kg': 1.,
        'tons': 907.1847,
        'lbs': 0.453592
    }

    # Convert inputs to kg, then to final unit type
    kg = value * convert_dict[start_unit]
    converted_value = kg / convert_dict[final_unit]

    return converted_value
