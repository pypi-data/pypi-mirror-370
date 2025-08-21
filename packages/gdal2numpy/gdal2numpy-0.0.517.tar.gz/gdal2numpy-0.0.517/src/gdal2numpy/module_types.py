def parseBool(text):
    """
    parseBool
    """
    text = f"{text}"
    return text not in ("False", "false", "0", "None", "undefined")


def parseInt(text):
    """
    parseInt
    """
    try:
        return int(f"{text}")
    except ValueError:
        return None


def parseFloat(text):
    """
    parseFloat
    """
    try:
        return float(f"{text}")
    except ValueError:
        return None
    

def isstring(text):
    """
    isstring
    """
    return isinstance(text, (str,))


def isarray(text):
    """
    isarray
    """
    return isinstance(text, (list, tuple))