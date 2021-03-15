def decimal_Parse(s):
    return float(s)

def IsWhiteSpace(*args):
    '''
    Mimic char.IsWhiteSpace.

    Sequential arguments:
    1st (args[0]) -- String to check as a whole or as a character
    2nd (args[1]) -- If present, the second param is the index in
                     args[0] to check and no other parts of args[0] will
                     be checked.
    '''
    if len(args) == 1:
        raise ValueError("IsWhiteSpace only takes (c)"
                         " or (c, index)")
    if len(args[0]) != 1:
        raise ValueError("The 1st param must be a character but is"
                         " \"{}\".".format(param))
    if len(args) == 1:
        return str.isspace(args[0])
    elif len(args) == 2:
        return str.isspace(args[0][args[1]])
    raise ValueError("IsWhiteSpace only takes (charStr)"
                     " or (str, index)")


def IsNullOrEmpty(s):
    if s is None:
        return True
    if len(s) == 0:
        return True
    return False


def IsNullOrWhiteSpace(s):
    if s is None:
        return True
    if len(s) == 0:
        return True
    return str.isspace(s)


def NumberToStr(n):
    '''
    Mimic c# decimal1.ToString() behavior common to G-code (lose the
    decimal places if not present) since in Python, str(float(1.0))
    is "1.0" but the desired output of the .NET code was "1".
    '''
    if isinstance(n, float) and (float(int(n)) == n):
        return str(int(n))
    return str(n)


def IsDigit(c):
    if len(c) != 1:
        raise ValueError("The param must be a character but is"
                         " \"{}\".".format(param))
    return c in "0123456789"
