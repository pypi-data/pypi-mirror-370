"""
$Id: struct_builder.py 2452 2020-04-23 19:20:47Z pe $

Module for building dynamic structures, e.g. configuration structure which
is customized for dynamic run time conditions.

Struct builder -- three operations:
===================================

Condition:
----------
A dictionary can be invalidated if a condition is not met. Conditions always
apply to a dictionary.
Condition object is a dictionary key that refers to either an IsIn or NotIn
object.

E.g.:
{
    'whatever': 'something',
    struct_builder.Condition('condition'): True
}
Result is {'whatever': 'something'} if 'condition' is True
Result is None in any other case.


Merge:
------
Merges a dictionary into a parent dictionary. Merge always occurs in a
dictionary (parent dictionary). The Merge Object is a dictionary key which
refers to a dictionary of cases. Each case refers to a merge dictionary (which)
should be merged into the parent dictionary.
a) If the condition is not listed in the cases, The result will be None.
b) If the merge dictionary is None (or results to None because of a nested
Condition or Merge), the parent dictionary will also result to None!
E.g.:
{
    struct_builder.Merge('condition'): {
        True: {
            'whatever': 'something',
            },
        # Default: None  # same result! (special rule a)
    }
}
Result is {'whatever': 'something'} if 'condition' is True
Result is None in any other case. (Special rules a and b)

Substitute:
-----------
Object will be substituted with a given value according to conditions.
Substitute can occur as a value (i.e. scalar, list element or dictionary value).
a) If the condition is not listed in the cases, The result will be None.
E.g.
[
    1,
    2,
    3,
    struct_builder.Substitute('bla', {
        22: 4,
        33 : 5,
        # Default: None  # same result! (special rule a)
        })
    }
]
Results to [1, 2, 3, 4] if 'bla' is 22
Results to [1, 2, 3, 5] if 'bla' is 33
Results to [1, 2, 3, None] in any other case


More complex conditions: IsIn, NotIn, BitAnd:
---------------------------------------------

For all Operations (Condition, Merge and Substitute) there is also the
possibility to have more complex conditions.
Instead of a value which is compared, IsIn, NotIn and BitAnd objects can be
used, e.g.:
{
    struct_builder.Merge('condition'): {
        1: {
            'whatever': 'something',
           },
        IsIn([2,3]): {
            'whatever': 'something else',
           },
        NotIn([7, 8, 9]): {
            'whatever': 'yet another thing',
           },
        BitAnd(2): {
            'whatever': 'the thing for 2, 3, 6, 7, ...)',
           },
        # Default: None  # same result! (special rule a)
    }
}
Note: As there is a possibility that more then one case is true, the following
priority is used:
1) equal match (case of 1: above)
2) BitAnd matches
3) IsIn matches
4) NotIn matches
5) Default

Example for Condition:
{
    'whatever': 'something',
    struct_builder.Condition('condition'): struct_builder.IsIn([True])
}
Example for Substitute:
[
    1,
    2,
    3,
    struct_builder.Substitute('bla', {
        3: 10,
        struct_builder.IsIn([1, 2, 3]): 11,
        struct_builder.NotIn([4, 5, 6]): 12,
        struct_builder.BitAnd(2): 13,
        struct_builder.Default: 14
        })
]

Special case for list:
----------------------
If a list element was a dictionary, but results to None (due to a Condition or
a nested Merge), the list element is dropped.
E.g.
[
    { 1: 2, 2: 3},
    { 1: 2, 2: 3},
    {
        1: 2, 2: 3,
        Condition('bla'): IsIn[22]
    }
]
Results in [{ 1: 2, 2: 3},{ 1: 2, 2: 3}, { 1: 2, 2: 3}] if 'bla' is 22
Results in [{ 1: 2, 2: 3},{ 1: 2, 2: 3}] in any other case
"""



class Default(object):  # pylint: disable=R0903
    # R0903: Too few public methods
    """
    Simple enumeration value for default behaviour in EbasMetadata.
    """
    pass

class IsIn(tuple):
    """
    List for validation checks.
    """
    pass

class NotIn(tuple):
    """
    Negated list for validation checks.
    """
    pass

class BitAnd(int):
    """
    Operand for bitwise "and" operation in validation checks.
    """
    pass

class Condition(object):  # pylint: disable=R0903
    # R0903: Too few public methods
    """
    Class for implementing the Condition.
    """
    def __init__(self, name):
        """
        Set up the substitution object.
        Parameters:
            name      name for the condition (str)
        Returns:
            None
        """
        self.name = name

    def evaluate(self, in_not_in, conditionals):  # pylint: disable=R0911
    # R0911: Too many return statements
        """
        Evaluates the substitution.
        Parameters:
            in_not_in       a In or NotIn Object to be used for the evaluation
            conditionals    the conditional dictionary from the StructurBuilder
        Returns:
            True/False
        """
        if self.name not in conditionals:
            raise ValueError("condition name {} not found in conditional {}"
                             .format(self.name, conditionals))
        if isinstance(in_not_in, IsIn):
            if conditionals[self.name] in in_not_in:
                return True
            else:
                return False
        if isinstance(in_not_in, NotIn):
            if conditionals[self.name] not in in_not_in:
                return True
            else:
                return False
        if isinstance(in_not_in, BitAnd):
            if conditionals[self.name] & in_not_in:
                return True
            else:
                return False
        if in_not_in == conditionals[self.name]:
            return True
        return False

class Merge(object):  # pylint: disable=R0903
    # R0903: Too few public methods
    """
    Class for implementing a Dictionary Merge.
    """
    def __init__(self, name):
        """
        Set up the substitution object.
        Parameters:
            name      name for the condition (str)
        Returns:
            None
        """
        self.name = name

    def evaluate(self, cases, conditionals):
        """
        Evaluates the substitution.
        Parameters:
            cases           the different cases and their result values (dict)
            conditionals    the conditional dictionary from the StructurBuilder
        Returns:
            dictionary which should be merged
        """
        if self.name not in conditionals:
            raise ValueError("condition name {} not found in conditional {}"
                             .format(self.name, conditionals))
        # first prio: equal value
        if conditionals[self.name] in cases:
            return cases[conditionals[self.name]]
        # second prio: Matching BitAnd exists:
        for cas in cases:
            try:
                if isinstance(cas, BitAnd) and conditionals[self.name] & cas:
                    return cases[cas]
            except TypeError:
                # ignore TypeError, there was something that cant be used for &
                # conditionals[self.name]
                pass
        # third prio: Matching IsIn exists
        for cas in cases:
            if isinstance(cas, IsIn) and  conditionals[self.name] in cas:
                return cases[cas]
        # fourth prio: Matching NotIn exists
        for cas in cases:
            if isinstance(cas, NotIn) and  conditionals[self.name] not in cas:
                return cases[cas]
        # fifth prio: Default
        if Default in cases:
            return cases[Default]
        # else None
        return None


class Substitute(object):  # pylint: disable=R0903
    # R0903: Too few public methods
    """
    Class for implementing the Substitution.
    """
    def __init__(self, name, cases):
        """
        Set up the substitution object.
        Parameters:
            name      name for the condition (str)
            cases          the different cases and their result values (dict)
        Returns:
            None
        """
        self.name = name
        self.cases = cases

    def evaluate(self, conditionals):
        """
        Evaluates the substitution.
        Parameters:
            conditionals    the conditional dictionary from the StructurBuilder
        Returns:
            Value (or struct) to be used
        """
        if self.name not in conditionals:
            raise ValueError("condition name {} not found in conditional {}"
                             .format(self.name, conditionals))
        # first prio: equal value
        if conditionals[self.name] in self.cases:
            return self.cases[conditionals[self.name]]
        # second prio: Matching BitAnd exists:
        for cas in self.cases:
            if isinstance(cas, BitAnd) and conditionals[self.name] & cas:
                return self.cases[cas]
        # third prio: Matching IsIn exists
        for cas in self.cases:
            if isinstance(cas, IsIn) and  conditionals[self.name] in cas:
                return self.cases[cas]
        # fourth prio: Matching NotIn exists
        for cas in self.cases:
            if isinstance(cas, NotIn) and  conditionals[self.name] not in cas:
                return self.cases[cas]
        # fifth prio: Default
        if Default in self.cases:
            return self.cases[Default]
        # else None
        return None


class StructureBuilder(object):  # pylint: disable=R0903
    # R0903: Too few public methods
    """
    Class for building dynamic structures, e.g. configuration structure which
    is customized for dynamic run time conditions.
    """

    def __init__(self, conditionals=None):
        """
        Initialise builder object. Set conditions and values.
        Parameters:
            conditionals   the conditional names and values to be used for
                           building
        Returns:
            None
        """
        self.conditionals = conditionals

    def build(self, structure):
        """
        Builds the result structure.
        Parameters:
            structure
        Returns:
            result structure
        """
        if isinstance(structure, dict):
            structure = structure.copy()
            for key in list(structure.keys()):
                if isinstance(key, Condition):
                    if key.evaluate(structure[key], self.conditionals):
                        # condition is met, delete the condition from dict
                        del structure[key]
                    else:
                        # condition is not met, drop the whole dict
                        return None

            for key in list(structure.keys()):
                if isinstance(key, Merge):
                    new = key.evaluate(structure[key], self.conditionals)
                    del structure[key]
                    new = self.build(new)
                    if new is None:
                        return None
                    else:
                        # for None, no merge needed, else merge:
                        structure.update(new)
                else:
                    # all other dictionary keys except Merge: bulid the
                    # sub-structure
                    new = self.build(structure[key])
                    if isinstance(structure[key], dict) and new is None:
                        # special case: if a dictionary becomes None, then a
                        # Condition failed inside --> delete the key from parent
                        del structure[key]
                    else:
                        structure[key] = new
        elif isinstance(structure, list):
            structure = list(structure)
            i = 0
            while i < len(structure):
                new = self.build(structure[i])
                if isinstance(structure[i], dict) and new is None:
                    # special case: if a dictionary becomes None, then a
                    # Condition failed inside --> delete the element from parent
                    del structure[i]
                else:
                    structure[i] = new
                    i += 1
        elif isinstance(structure, Substitute):
            new = structure.evaluate(self.conditionals)
            return self.build(new)
        return structure
