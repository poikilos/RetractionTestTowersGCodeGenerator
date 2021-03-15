def ToNumber(s):
    result = None
    try:
        result = int(s)
    except ValueError:
        result = float(s)
    # ^ mimic decimal.Parse behavior :( (Python str(float("1")) is 1.0)
    return result

def IsSpace(*args):
    '''
    Sequential arguments:
    1st (args[0]) -- String to check as a whole or as a character
    2nd (args[1]) -- If present, the second param is the index in
                     args[0] to check and no other parts of args[0] will
                     be checked.
    '''
    if len(args) == 1:
        return str.isspace(args[0])
    elif len(args) == 2:
        return str.isspace(args[0][args[1]])
    raise ValueError("IsSpace only takes (charStr)"
                     " or (str, index)")

def NumberToStr(n):
    '''
    Mimic c# decimal1.ToString() behavior common to G-code (lose the
    decimal places if not present) since in Python, str(float(1.0))
    is "1.0".
    '''
    if isinstance(n, float) and (float(int(n)) == n):
        return str(int(n))
    return str(n)
