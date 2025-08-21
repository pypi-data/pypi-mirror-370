"""
chemical elements properties
"""

# Fundamental constants for chemical elements
# Constants are:
# AtomicWeight: the ratio of the mass of one atom to 1/12 of the mass of one
#               carbon-12 atom (unit: dimensionless)
# MolarMass: the mass of one mole of the element
#
# Annotation: the numbers for AtomicWeight and MolarMass are by definition
# equal. We use different constants anyway because they have different
# dimension.
ELEMENTS = \
{
    "C":
    {
        "MolarMass": 12.011,  # molar mass (g/mol)
        "AtomicWeight": 12.011,  # (dimensionless)
        # Source: Conventional Atomic Weights 2013. Commission on Isotopic
        # Abundances and Atomic Weights: [12.0096, 12.0116]
    },
    "Ca":
    {
        "MolarMass": 40.078,  # molar mass (g/mol)
        "AtomicWeight": 40.078, # (dimensionless)
        # Source: Atomic weights of the elements 2013 (IUPAC Technical Report)
        # https://doi.org/10.1515%2Fpac-2015-0305)
    },
    "Cl":
    {
        "MolarMass": 35.45,  # molar mass (g/mol)
        "AtomicWeight": 35.45, # (dimensionless)
        # Source: Conventional Atomic Weights 2013.
        # (isotope mix is highly variable due to regional source of the material
        # the conventional atomic weight specifies a global average
        # https://doi.org/10.1515%2Fpac-2015-0305)
        # Atomic weights of the elements 2013 (IUPAC Technical Report)
        # [35.446, 35.457], conventional: 35.45
    },
    "F":
    {
        "MolarMass": 18.998403163,  # molar mass (g/mol)
        "AtomicWeight": 18.998403163,  # (dimensionless)
        # Source: Atomic weights of the elements 2013 (IUPAC Technical Report)
        # https://doi.org/10.1515/pac-2015-0305
    },
    "H":
    {
        "MolarMass": 1.008,  # molar mass (g/mol)
        "AtomicWeight": 1.008,  # (dimensionless)
        # Source: Conventional Atomic Weights 2013. Commission on Isotopic
        # Abundances and Atomic Weights: [1.00784-1.00811]
    },
    "K":
    {
        "MolarMass": 39.0983,  # molar mass (g/mol)
        "AtomicWeight": 39.0983, # (dimensionless)
        # Source: Atomic weights of the elements 2013 (IUPAC Technical Report)
        # https://doi.org/10.1515%2Fpac-2015-0305)
    },
    "Mg":
    {
        "MolarMass": 24.305,  # molar mass (g/mol)
        "AtomicWeight": 24.305, # (dimensionless)
        # Source: Atomic weights of the elements 2013 (IUPAC Technical Report)
        # https://doi.org/10.1515%2Fpac-2015-0305)
        # Conventional atomic weight
    },
    "N":
    {
        "MolarMass": 14.007,  # molar mass (g/mol)
        "AtomicWeight": 14.007,  # (dimensionless)
        # Source: Conventional Atomic Weights 2015. Commission on Isotopic
        # Abundances and Atomic Weights: [14.00643, 14.00728]
    },
    "Na":
    {
        "MolarMass": 22.98976928,  # molar mass (g/mol)
        "AtomicWeight": 22.98976928, # (dimensionless)
        # Source: Atomic weights of the elements 2013 (IUPAC Technical Report)
        # https://doi.org/10.1515%2Fpac-2015-0305)
    },
    "O":
    {
        "MolarMass": 15.9994,  # molar mass (g/mol)
        "AtomicWeight": 15.9994,  # (dimensionless)
        # Source: Conventional Atomic Weights 2015. Commission on Isotopic
        # Abundances and Atomic Weights: [15.99903, 15.99977]
    },
    "P":
    {
        "MolarMass": 30.973761998,  # molar mass (g/mol)
        "AtomicWeight": 30.973761998,  # (dimensionless)
        # Source: Atomic weights of the elements 2013 (IUPAC Technical Report)
        # https://doi.org/10.1515/pac-2015-0305
    },
    "S":
    {
        "MolarMass": 32.06,  # molar mass (g/mol)
        "AtomicWeight": 32.06, # (dimensionless)
        # Source: Conventional Atomic Weights 2013.
        # (isotope mix is highly variable due to regional source of the material
        # the conventional atomic weight specifies a global average
        # https://doi.org/10.1515/pac-2015-0305)
        # Standard Atomic Weights 2015. Commission on Isotopic
        # Abundances and Atomic Weights: [32.059-32.076]
    },
}

