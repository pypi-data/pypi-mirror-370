import inspect
from copy import deepcopy
from textwrap import dedent

import executing

from colorful_terminal import *


class Source(executing.Source):
    def get_text_with_indentation(self, node):
        result = self.asttokens().get_text(node)
        if "\n" in result:
            result = " " * node.first_token.start[1] + result
            result = dedent(result)
        result = result.strip()
        return result


class NoSourceAvailableError(OSError):
    """
    Raised when finding or accessing source code that's required to
    parse and analyze fails. This can happen, for example, when

    - varp() is invoked inside a REPL or interactive shell, e.g. from the
        command line (CLI) or with python -i.

    - The source code is mangled and/or packaged, e.g. with a project
        freezer like PyInstaller.

    - The underlying source code changed during execution. See
        https://stackoverflow.com/a/33175832.
    """

    infoMessage = (
        "Failed to access the underlying source code for analysis. Was varp() "
        "invoked in a REPL (e.g. from the command line), a frozen application "
        "(e.g. packaged with PyInstaller), or did the underlying source code "
        "change during execution?"
    )


def get_var_names(frame=2):
    """
    Returns variable names by execution frame. Frame = 2 gets you the input variable name of the arguments of your parent function.


    Args:

        • frame (int, optional) Defaults to 2.
            currentframe of excecution frame. Must be 1 =< frame =< 3.


    Raises:

        • ValueError:
            If not 1 <= frame <= 3.

        • NoSourceAvailableError:
            if callNode is None.


    Returns:

        list:
            arg names.

    """
    if frame == 1:
        callFrame = inspect.currentframe().f_back
    elif frame == 2:
        callFrame = inspect.currentframe().f_back.f_back
    elif frame == 3:
        callFrame = inspect.currentframe().f_back.f_back.f_back
    else:
        raise ValueError("max frame: 3")
    callNode = Source.executing(callFrame).node
    if callNode is None:
        raise NoSourceAvailableError()
    source = Source.for_frame(callFrame)
    sanitizedArgStrs = [source.get_text_with_indentation(arg) for arg in callNode.args]
    return sanitizedArgStrs


def get_string_as_fitted_table(
    data: list, padding: int = 2, min_width: int = None, alignment: str = "left"
):
    """Generates a string representation of the given table.

    Args:
        data (list): List of rows with rows as lists of column entries. e.g. `[["row1 col1", "row1 col2"], ["row2 col1", "row2 col2"]]`. If there are not enough columns, whitespace will fill the remaining cells.
        padding (int, optional): Space between columns = `padding * " "`. Defaults to 2.
        min_width (int, optional): Minimum width for columns. Defaults to None.
        alignment (str, optional): Text alignment. Can be "left", "center", or "right". Defaults to "left".

    Returns:
        str: String representation of the table.
    """
    dataset = deepcopy(data)
    row_lengths = [len(row) for row in dataset]
    cols = max(row_lengths)

    for row in dataset:
        while len(row) < cols:
            row.append("")

    col_widths = []
    for i in range(cols):
        col = [row[i] for row in dataset]
        col_width = max(len(str(word)) for word in col) + padding  # padding
        col_widths.append(col_width)

    s = ""
    for row in dataset:
        for index, word in enumerate(row):
            if min_width is not None and col_widths[index] < min_width:
                col_widths[index] = min_width

            if alignment == "left":
                s += str(word).ljust(col_widths[index])
            elif alignment == "center":
                s += str(word).center(col_widths[index])
            elif alignment == "right":
                s += str(word).rjust(col_widths[index])

        if row != dataset[-1]:
            s += "\n"

    return s


def pretty_print_list(
    List: list,
    print_list_name: bool = True,
    colored: bool = True,
    name_rgb=(255, 175, 0),
    value_rgb=(0, 255, 255),
    syntax_rgb=(200, 200, 200),
):
    """This function generates a visually appealing string representation of a given list.

    Args:
        List (list): The list to be printed.
        print_list_name (bool, optional): If True, prints the name of the list. Defaults to True.
        colored (bool, optional): If True, applies colors to enhance readability. Defaults to True.
        name_rgb (tuple, optional): RGB values for the color of the list name. Defaults to (255, 175, 0).
        value_rgb (tuple, optional): RGB values for the color of list values. Defaults to (0, 255, 255).
        syntax_rgb (tuple, optional): RGB values for the color of syntax elements. Defaults to (200, 200, 200).
    """
    if colored:
        n_color = Fore.rgb(*name_rgb)
        v_color = Fore.rgb(*value_rgb)
        s_color = Fore.rgb(*syntax_rgb)
        reset = Fore.RESET
    else:
        n_color = ""
        v_color = ""
        reset = ""
        s_color = ""
    if print_list_name:
        try:
            list_name = get_var_names(frame=2)[0]
        except:
            list_name = "<name of list not found>"
        name = n_color + list_name + reset + s_color + " = [\n" + reset
        spacer = "\t"
    else:
        name = ""
        spacer = ""
    len_list = len(List)
    for i, v in enumerate(List):
        v = repr(v)
        ink = f"{spacer}{v_color}{v}{reset}"
        if i != len_list - 1 and print_list_name:
            ink += s_color + "," + reset
        name += ink + "\n"
    if print_list_name:
        name += s_color + "]" + reset
    colored_print(name)


def pretty_print_nested_list(
    List: list[list],
    print_list_name: bool = True,
    colored: bool = True,
    name_rgb=(255, 175, 0),
    value1_rgb=(0, 255, 255),
    value2_rgb=(255, 255, 0),
    syntax_rgb=(200, 200, 200),
):
    """This function generates a visually appealing string representation of a nested list.

    Args:
        List (list of lists): The nested list to be printed.
        print_list_name (bool, optional): If True, prints the name of the list. Defaults to True.
        colored (bool, optional): If True, applies colors to enhance readability. Defaults to True.
        name_rgb (tuple, optional): RGB values for the color of the list name. Defaults to (255, 175, 0).
        value1_rgb (tuple, optional): RGB values for the color of odd-indexed list values. Defaults to (0, 255, 255).
        value2_rgb (tuple, optional): RGB values for the color of even-indexed list values. Defaults to (255, 255, 0).
        syntax_rgb (tuple, optional): RGB values for the color of syntax elements. Defaults to (200, 200, 200).

    Raises:
        ValueError: If List is empty
    """
    try:
        name = get_var_names(frame=2)[0]
    except:
        name = "<name of list not found>"
    if colored:
        n_color = Fore.rgb(*name_rgb)
        v1_color = Fore.rgb(*value1_rgb)
        v2_color = Fore.rgb(*value2_rgb)
        s_color = Fore.rgb(*syntax_rgb)
        reset = Fore.RESET
    else:
        n_color = ""
        v1_color = ""
        v2_color = ""
        reset = ""
        s_color = ""
    vcols = (v1_color, v2_color)
    spacer = "\t"

    data = List
    padding = 1

    if len(data) == 0:
        raise ValueError("List is empty!")
    dataset = deepcopy(data)
    row_lenghts = []
    for row in dataset:
        row_lenghts.append(len(row))
    cols = max(row_lenghts)
    for row in dataset:
        while len(row) < cols:
            row.append("")
    col_widths = []
    for i in range(cols):
        col = [row[i] for row in dataset]
        col_width = max(len(str(word)) for word in col) + padding  # padding
        col_widths.append(col_width)
    s = ""
    if print_list_name:
        s += n_color + name + reset + " = [\n"
    len_data = len(dataset)
    for row_index, row in enumerate(dataset):
        len_row = len(row)
        if print_list_name:
            s += spacer
        s += s_color + "[" + reset

        for index, word in enumerate(row):
            str_word = str(word)
            if type(word) == str:
                str_word = "'" + str_word + "'"
            if str_word != "''":
                if index != len_row - 1 and not all(
                    [w == "" for w in row[index + 1 :]]
                ):
                    str_word += s_color + "," + reset
                s += (
                    vcols[index % 2]
                    + str_word
                    + "".ljust(-len(str(word)) + col_widths[index])
                    + reset
                )

        s += s_color + TermAct.cursor_back + "]" + reset
        if row_index != len_data - 1:
            if print_list_name:
                s += s_color + "," + reset
            s += "\n"
    if print_list_name:
        s += s_color + "\n]" + reset
    colored_print(s)
