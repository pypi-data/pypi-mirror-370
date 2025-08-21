"""
$Id: dataset_types.py 2800 2022-06-09 11:20:46Z pe $

Basic functionality for classifying dataset types
(auxiliary, precipitation amount)

Those methods are used both in ebas.io and ebas.domain.entities.ds.
In order to make them available for both modules they are separated in this
general domain module.
"""

def is_precip_concentration(matrix, comp_name):
    """
    Check if the dataset is a precipitation concentration component (one
    that needs precipitation amount)
    Parameters:
        comp_name   component name
        matrix      matrix name
    Returns:
        True/False
    """
    if matrix in ('precip', 'precip_tot') and \
            not comp_name.startswith('precipitation_amount'):
        return True
    return False

def is_precip_amount(matrix, comp_name):
    """
    Check if the dataset is a precipitation amount component
    Parameters:
        comp_name   component name
        matrix      matrix name
    Returns:
        True/False
    """
    if matrix in ('precip', 'precip_tot') and \
            comp_name.startswith('precipitation_amount'):
        return True
    return False

def is_auxiliary(matrix, comp_name):
    """
    Check if the dataset is to be considered "auxiliary data".
    Parameters:
        comp_name   component name
        matrix      matrix name
    Returns:
        True/False
    """
    if matrix in ('instrument', 'position'):
        return True
    if matrix != 'met' and \
       comp_name in  ('pressure', 'temperature', 'relative_humidity'):
        return True
    if comp_name == 'sample_count':
        # Component sample count is auxiliary.
        # But parameters with statistics=sample count are not!
        return True
    if comp_name in ('start_time', 'end_time', 'number of size bins'):
        # These are variables skipped on import, but when creating files, they
        # are of course auxiliary.
        return True
    return is_precip_amount(matrix, comp_name)
