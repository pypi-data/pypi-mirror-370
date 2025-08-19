import os
from typing import List

from ._plugin import Plugin, get_aliases
from .placeholders import PlaceholderSupporter, placeholder_help

HELP_FORMAT_TEXT = "text"
HELP_FORMAT_MARKDOWN = "markdown"
HELP_FORMATS = [
    HELP_FORMAT_TEXT,
    HELP_FORMAT_MARKDOWN,
]


def generate_plugin_usage(plugin: Plugin, help_format: str = HELP_FORMAT_TEXT, heading_level: int = 1):
    """
    Generates the usage help screen for the specified plugin.

    :param plugin: the plugin to generate the usage for (name used on command-line)
    :type plugin: Plugin
    :param help_format: the format to use for the output
    :type help_format: str
    :param heading_level: the level to use for the heading (markdown)
    :type heading_level: int
    """
    if help_format not in HELP_FORMATS:
        raise Exception("Unhandled help format: %s" % help_format)

    aliases = get_aliases(plugin)
    result = ""
    if help_format == HELP_FORMAT_TEXT:
        result += "\n" + plugin.name() + "\n" + "=" * len(plugin.name()) + "\n"
        result = result.strip()
        result += "\n\n"
        if len(aliases) > 0:
            result += "Alias(es): %s\n\n" % ", ".join(aliases)
        result += plugin.format_help() + "\n"
        if isinstance(plugin, PlaceholderSupporter):
            result += "\n" + placeholder_help(markdown=False, obj=plugin) + "\n"
    elif help_format == HELP_FORMAT_MARKDOWN:
        result += "#"*heading_level + " " + plugin.name() + "\n"
        result += "\n"
        result = result.strip()
        result += "\n\n"
        if len(aliases) > 0:
            result += "Alias(es): %s\n\n" % ", ".join(aliases)
        result += plugin.description() + "\n"
        result += "\n"
        result += "```\n"
        result += plugin.format_help()
        result += "```\n"
        if isinstance(plugin, PlaceholderSupporter):
            result += "\n" + placeholder_help(markdown=True, obj=plugin) + "\n"
    else:
        raise Exception("Unhandled help format: %s" % help_format)

    return result


def generate_help(plugins: List[Plugin], help_format: str = HELP_FORMAT_TEXT, heading_level: int = 1,
                  output_path: str = None):
    """
    Generates and outputs the help screen for the plugin.

    :param plugins: the plugins to generate the help screens for
    :type plugins: list
    :param help_format: the format to output
    :type help_format: str
    :param heading_level: the heading level to use (markdown)
    :type heading_level: int
    :param output_path: the dir to save the output to, uses stdout if None
    :type output_path: str
    """
    if help_format not in HELP_FORMATS:
        raise Exception("Unknown help format: %s" % help_format)

    for p in plugins:
        help_screen = generate_plugin_usage(p, help_format=help_format, heading_level=heading_level)
    
        if output_path is None:
            print(help_screen)
        else:
            if help_format == HELP_FORMAT_TEXT:
                suffix = ".txt"
            elif help_format == HELP_FORMAT_MARKDOWN:
                suffix = ".md"
            else:
                raise Exception("Unhandled help format: %s" % help_format)
    
            if os.path.isdir(output_path):
                output_file = os.path.join(output_path, p.name() + suffix)
            else:
                output_file = output_path
            with open(output_file, "w") as fp:
                fp.write(help_screen)
