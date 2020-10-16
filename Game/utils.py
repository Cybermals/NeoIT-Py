"""New Impressive Title - Utilities API"""


#Functions
#=============================================================================
def parse_vec(s, size = 3):
    """Parse a vector and return it as a list of values. Upon failure, return a
    vector containing all 0s.
    """
    if s.count(" ") < size - 1:
        return [0] * size

    try:
        return [float(value) for value in s.split(" ")]

    except ValueError:
        return [0] * size