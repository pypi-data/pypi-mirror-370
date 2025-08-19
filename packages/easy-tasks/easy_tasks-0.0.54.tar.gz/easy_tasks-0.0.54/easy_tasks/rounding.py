

def round_relative_to_decimal(number: float, digits: int) -> str:
    """Round a number to the specified number of decimal trailing digits.
     Example 1: 0 with 2 digits: 0.00
     Example 2: 1.234 with 2 digits: 1.23

    Args:
        - number (float): Number to round.
        - digits (int): Decimal trailing digits.

    Returns:
        str: String representation of the rounded number.
    """
    number = round(number, digits)
    sn = str(number)
    if not "." in sn:
        sn += "."
    while len(sn.split(".")[-1]) < digits:
        sn = sn + "0"
    return sn


def round_significantly_std_notation(number: float, significant_digits: int) -> str:
    """Round a number to have only significant digits. Output is in standard notation.
     If the number is greater than ten to the power of the significant digits, the number is rounded to have 0 trailing digits.

    Args:
        number (float): Number to round.
        significant_digits (int): Significant digits.

    Returns:
        str: String representation of the rounded number in standard notation.
    """
    negative = False
    if number < 0:
        negative = True
        number *= -1
    snum = str(number)
    if not "e" in snum.lower():
        dpos = spos = snum.find(".")
        if dpos == -1:
            dpos = len(snum)
            snum += "."
        for i, c in enumerate(snum):
            if c != "." and c != "0":
                spos = i
                break
        e = dpos - spos
    else:
        e = int(snum.lower().split("e")[-1])
    num = number
    if e < 1:
        num = number / 10**e
        nstr = round_relative_to_decimal(num, significant_digits - 1)
        deci = e * (-1)
        nstr = "0" + "." + (deci - 1) * "0" + nstr.replace(".", "")
        if e == 0:
            nstr = nstr[:-1]
    elif e == 1:
        nstr = round_relative_to_decimal(number, significant_digits - 1)
    else:
        nstr = str(round(number, 0))
        if len(nstr) > significant_digits:
            nstr = nstr.split(".")[0]
        else:
            while len(nstr) - 1 < significant_digits:
                if "." not in nstr:
                    nstr += "."
                nstr += "0"
    if negative:
        nstr = "-" + nstr
    return nstr


def round_significantly_sci_notation(number: float, significant_digits: int, e_for_10: str = "E") -> str:
    """Round a number to have only significant digits. Output is in scientific notation with the n-th power of ten as En.

    Args:
        number (float): Number to round.
        significant_digits (int): Significant digits.

    Returns:
        str: String representation of the rounded number in scientific notation with the n-th power of ten as En.
    """
    negative = False
    if number < 0:
        negative = True
        number *= -1
    snum = str(number)
    if not "e" in snum.lower():
        dpos = spos = snum.find(".")
        if dpos == -1:
            dpos = len(snum)
        for i, c in enumerate(snum):
            if c != "." and c != "0":
                spos = i
                break
        e = dpos - spos
    else:
        e = int(snum.lower().split("e")[-1])
    estr = ""
    num = number
    if e <= 0:
        estr = f"{e_for_10}{e}"
        num = number / 10**e
        nstr = round_relative_to_decimal(num, significant_digits - 1) + estr
    else:
        e -= 1
        estr = f"{e_for_10}{e}"
        num = number / 10**e
        nstr = round_relative_to_decimal(num, significant_digits - 1) + estr
    if negative:
        nstr = "-" + nstr
    return nstr
