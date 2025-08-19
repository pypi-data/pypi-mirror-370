import os
import tempfile

from typing import List


PH_HOME = "{HOME}"
PH_CWD = "{CWD}"
PH_TMP = "{TMP}"
PH_INPUT_PATH = "{INPUT_PATH}"
PH_INPUT_NAMEEXT = "{INPUT_NAMEEXT}"
PH_INPUT_NAMENOEXT = "{INPUT_NAMENOEXT}"
PH_INPUT_EXT = "{INPUT_EXT}"
PH_INPUT_PARENT_PATH = "{INPUT_PARENT_PATH}"
PH_INPUT_PARENT_NAME = "{INPUT_PARENT_NAME}"
PLACEHOLDERS = [
    PH_HOME,
    PH_CWD,
    PH_TMP,
    PH_INPUT_PATH,
    PH_INPUT_NAMEEXT,
    PH_INPUT_NAMENOEXT,
    PH_INPUT_EXT,
    PH_INPUT_PARENT_PATH,
    PH_INPUT_PARENT_NAME,
]
PLACEHOLDERS_INPUT_BASED = {
    PH_HOME: False,
    PH_CWD: False,
    PH_TMP: False,
    PH_INPUT_PATH: True,
    PH_INPUT_NAMEEXT: True,
    PH_INPUT_NAMENOEXT: True,
    PH_INPUT_EXT: True,
    PH_INPUT_PARENT_PATH: True,
    PH_INPUT_PARENT_NAME: True,
}
PLACEHOLDERS_LAMBDA = {
    PH_HOME: lambda i: os.path.expanduser("~"),
    PH_CWD: lambda i: os.getcwd(),
    PH_TMP: lambda i: tempfile.gettempdir(),
    PH_INPUT_PATH: lambda i: os.path.dirname(i),
    PH_INPUT_NAMEEXT: lambda i: os.path.basename(i),
    PH_INPUT_NAMENOEXT: lambda i: os.path.splitext(os.path.basename(i))[0],
    PH_INPUT_EXT: lambda i: os.path.splitext(i)[1],
    PH_INPUT_PARENT_PATH: lambda i: os.path.dirname(os.path.dirname(i)) if (len(os.path.dirname(i)) > 0) else "",
    PH_INPUT_PARENT_NAME: lambda i: os.path.basename(os.path.dirname(i)) if (len(os.path.dirname(i)) > 0) else "",
}
PLACEHOLDERS_DESCRIPTION = {
    PH_HOME: "The home directory of the current user.",
    PH_CWD: "The current working directory.",
    PH_TMP: "The temp directory.",
    PH_INPUT_PATH: "The directory part of the current input, i.e., '/some/where' of input '/some/where/file.txt'.",
    PH_INPUT_NAMEEXT: "The name (incl extension) of the current input, i.e., 'file.txt' of input '/some/where/file.txt'.",
    PH_INPUT_NAMENOEXT: "The name (excl extension) of the current input, i.e., 'file' of input '/some/where/file.txt'.",
    PH_INPUT_EXT: "The extension of the current input (incl dot), i.e., '.txt' of input '/some/where/file.txt'.",
    PH_INPUT_PARENT_PATH: "The directory part of the parent directory of the current input, i.e., '/some' of input '/some/where/file.txt'.",
    PH_INPUT_PARENT_NAME: "The name of the parent directory of the current input, i.e., 'where' of input '/some/where/file.txt'.",
}
USER_DEFINED_PLACEHOLDERS = set()


class PlaceholderSupporter:
    """
    Indicator mixin whether a class supports placeholders in some form.
    Used for outputting help information.
    """
    pass


class InputBasedPlaceholderSupporter(PlaceholderSupporter):
    """
    Indicator mixin whether a class supports input-based placeholders.
    Used for outputting help information.
    """
    pass


def add_placeholder(placeholder: str, description: str, input_based: bool, lambda_func):
    """
    Allows adding a custom placeholder.

    :param placeholder: the placeholder itself
    :type placeholder: str
    :param description: the description for the placeholder, used in the placeholder_help() method
    :type description: str
    :param input_based: whether the placeholder relies on the current input
    :type input_based: str
    :param lambda_func: the lambda to use for expanding the placeholder, takes one argument: current input
    """
    if "{" not in placeholder:
        placeholder = "{" + placeholder + "}"
    if placeholder not in PLACEHOLDERS:
        PLACEHOLDERS.append(placeholder)
    PLACEHOLDERS_DESCRIPTION[placeholder] = description
    PLACEHOLDERS_INPUT_BASED[placeholder] = input_based
    PLACEHOLDERS_LAMBDA[placeholder] = lambda_func


def expand_placeholders(template: str, current_input: str = None) -> str:
    """
    Expands the placeholder in the template using the current input.

    :param current_input: the current input dir/file to use for the expansion
    :type current_input: str
    :param template: the template to expand
    :type template: str
    :return: the expanded string
    :rtype: str
    """
    result = template

    if "{" in result:
        for ph in PLACEHOLDERS:
            input_based = PLACEHOLDERS_INPUT_BASED[ph]
            lambda_func = PLACEHOLDERS_LAMBDA[ph]
            value = None
            if not input_based:
                value = lambda_func(None)
            elif input_based and (current_input is not None):
                value = lambda_func(current_input)
            if value is not None:
                result = result.replace(ph, value)

    return result


def placeholders(input_based: bool = False) -> List[str]:
    """
    Returns the placeholder names as list. Excludes user-defined placeholders.

    :param input_based: whether to include input based ones
    :type input_based: bool
    :return: the list of placeholders
    :rtype: list
    """
    result = []
    for ph in PLACEHOLDERS_INPUT_BASED:
        if ph in USER_DEFINED_PLACEHOLDERS:
            continue
        if (not input_based) and (not PLACEHOLDERS_INPUT_BASED[ph]):
            result.append(ph)
        elif input_based and PLACEHOLDERS_INPUT_BASED[ph]:
            result.append(ph)
    return result


def placeholder_list(input_based: bool = False, obj=None) -> str:
    """
    Returns a short string of supported placeholders as list, e.g., to be used in the help string
    of argparse options, e.g.: placeholder_list(obj=self).

    :param input_based: whether to include input based ones
    :type input_based: bool
    :param obj: the object to determine the placeholder mixin from, overrides input_based parameter
    :return: the generated string
    :rtype: str
    """
    if obj is not None:
        input_based = isinstance(obj, InputBasedPlaceholderSupporter)
    return "Supported placeholders: %s" % ", ".join(placeholders(input_based=input_based))


def placeholder_help(input_based: bool = False, obj=None, markdown: bool = False) -> str:
    """
    Returns help on placeholders.

    :param input_based: whether to include input based ones
    :type input_based: bool
    :param obj: the object to determine the placeholder mixin from, overrides input_based parameter
    :param markdown: whether to generate markdown or plain text
    :type markdown: bool
    :return: the generated help string
    :rtype: str
    """
    if obj is not None:
        input_based = isinstance(obj, InputBasedPlaceholderSupporter)
    result = "Available placeholders:"
    if markdown:
        result += "\n"
    for ph in placeholders(input_based=input_based):
        if markdown:
            result += "\n* `" + ph + "`: " + PLACEHOLDERS_DESCRIPTION[ph].replace("'", "`")
        else:
            result += "\n- " + ph + ": " + PLACEHOLDERS_DESCRIPTION[ph]
    return result


def load_user_defined_placeholders(path: str):
    """
    Loads placeholders from the specified text file (format: key=value) that are not input-based.
    With "key" being the name of the placeholder without the curly brackets and value the path
    that it represents. Ignores empty lines or lines that start with '#' or ';'.

    :param path: the file with the placeholders to load
    :type path: str
    """
    with open(path, "r") as fp:
        lines = fp.readlines()
    for line in lines:
        line = line.strip()
        if len(line) == 0:
            continue
        if line.startswith("#"):
            continue
        parts = line.split("=")
        if len(parts) == 2:
            ph = "{" + parts[0] + "}"
            USER_DEFINED_PLACEHOLDERS.add(ph)
            add_placeholder(ph, "", False, lambda i: parts[1])
        else:
            print("Invalid placeholder format (key=value): %s" % line)
