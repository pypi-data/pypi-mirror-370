"""Moule atmos_phys.convert

Unit conversions for atmospheric measuremensts.
Sub modules for different domains (aerosol, gases, ...; see there)

Example:
    A typical sequence for converting data::


        from atmos_phys.convert.gas import ConvertEthanal
        cvt = ConvertEthanal('pmol/mol', 'g/m3')
        data = [1.023, 0.998, 1.11]
        cvt.convert_data(data)
        print(data)
        [2.011e-09, 1.962e-09, 2.182e-09]
        print(cvt.conversion_string())
        from 'pmol/mol' to 'g/m3' at 273.15 K, 1013.25 hPa, conversion factor 0.00000000196544
"""
