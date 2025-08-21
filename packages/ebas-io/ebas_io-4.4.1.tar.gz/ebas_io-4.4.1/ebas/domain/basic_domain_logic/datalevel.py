"""
Data level spcific functionality
"""

def base_datalevel(data_level):
    """
    Returns the base datalevel.
    Parameters:
        datalevel    specific datalevel
    Returns:
        base datalevel (0, 1, 2, 3)
    """
    if data_level in ('0', '0.5', '0a', '0b'):
        return '0'
    if data_level in ('1', '1a', '1b'):
        return '1'
    if data_level in ('1.5', '2', '2a', '2b'):
        return '2'
    if data_level in ('3', '3a', '3b'):
        return '3'

