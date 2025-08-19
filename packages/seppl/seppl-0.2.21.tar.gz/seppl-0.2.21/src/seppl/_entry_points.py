import importlib
import json

from typing import List, Dict
from ._plugin import Plugin


def _to_entry_point(plugin: Plugin) -> str:
    """
    Turns the plugin into an entry point.

    :param plugin: the object to convert
    :type plugin: CommandlineHandler
    :return: the generated entry point
    :rtype: str
    """
    m = plugin.__module__

    # can we hide a private module?
    parts = m.split(".")
    if parts[-1].startswith("_"):
        parts.pop()
        m = ".".join(parts)
        try:
            importlib.import_module(m)
        except:
            # can't remove the last and private module, so we'll stick with the full path
            m = plugin.__module__

    result = plugin.name() + "=" + m + ":" + plugin.__class__.__name__
    return result


def _to_entry_points(plugins: List[Plugin]) -> List[str]:
    """
    Turns the plugins into a list of entry points.

    :param plugins: the plugins to convert
    :type plugins: list
    :return: the list of entry points
    :rtype: list
    """
    result = list()
    for plugin in plugins:
        result.append(_to_entry_point(plugin))
    return result


def generate_entry_points(entry_points: Dict[str, List[Plugin]]) -> str:
    """
    Generates the entry points string.
    Automatically suppresses empty entry point groups with an empty list of plugins.

    :param entry_points: the plugin lists, one list per entry_points group
    :type entry_points: dict
    """
    result = dict()
    keys = list(entry_points.keys())
    for k in keys:
        if len(entry_points[k]) == 0:
            entry_points.pop(k)
        result[k] = _to_entry_points(entry_points[k])

    return "entry_points=" + json.dumps(result, indent=4)
