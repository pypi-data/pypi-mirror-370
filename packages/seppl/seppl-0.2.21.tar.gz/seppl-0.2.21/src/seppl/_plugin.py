import argparse
import logging
import sys
import traceback

from typing import List
from ._types import classes_to_str, get_class_name, AnyData

from wai.logging import LOGGING_WARNING, set_logging_level, add_logging_level, add_logger_name


UNKNOWN_ARGS = "unknown_args"


class Plugin:
    """
    Base class for plugins.
    """

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        raise NotImplementedError()

    def description(self) -> str:
        """
        Returns a description of the handler.

        :return: the description
        :rtype: str
        """
        raise NotImplementedError()

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = argparse.ArgumentParser(
            description=self.description(),
            prog=self.name(),
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument(UNKNOWN_ARGS, nargs=argparse.REMAINDER, help=argparse.SUPPRESS)
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        pass

    def parse_args(self, args: List[str]) -> list:
        """
        Parses the command-line arguments.

        :param args: the arguments to parse
        :type args: list
        :return: any unknown args
        :rtype: list
        """
        parser = self._create_argparser()
        ns = parser.parse_args(args)
        self._apply_args(ns)
        return ns.unknown_args

    def print_help(self):
        """
        Outputs the help in the console.
        """
        self._create_argparser().print_help()

    def format_help(self) -> str:
        """
        Returns the formatted help string.

        :return: the help string
        :rtype: str
        """
        return self._create_argparser().format_help()


class AliasSupporter(object):
    """
    Mixin for classes that support alias names.
    """

    def aliases(self) -> List[str]:
        """
        Returns the aliases under which the plugin is known under/available as well.

        :return: the aliases
        :rtype: list
        """
        return []


def has_aliases(o) -> bool:
    """
    Checks whether the object has any aliases.

    :param o: the object to check
    :return: True if at least one alias defined
    """
    return len(get_aliases(o)) > 0


def get_aliases(o) -> List[str]:
    """
    Returns the aliases of the object, if it implements AliasSupporter.

    :param o: the object to get the aliases for
    :return: the list of aliases
    :rtype: list
    """
    result = []
    if isinstance(o, AliasSupporter):
        aliases = o.aliases()
        if aliases is not None:
            result.extend(aliases)
    return result


def get_all_names(o: Plugin) -> List[str]:
    """
    Returns all the names for the plugin, including any aliases.

    :param o: the plugin to get the names for
    :type o: Plugin
    :return: the list of aliases
    :rtype: list
    """
    result = [o.name()]
    result.extend(get_aliases(o))
    return result


class LoggingHandler(object):
    """
    Mixin for classes that support logging
    """

    def logger(self) -> logging.Logger:
        """
        Returns the logger instance to use.

        :return: the logger
        :rtype: logging.Logger
        """
        raise NotImplementedError()


class PluginWithLogging(Plugin, LoggingHandler):
    """
    Plugin that handles logging.
    """

    def __init__(self, logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the handler.

        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__()
        self.logging_level = logging_level
        self.logger_name = logger_name
        self._logger = None

    def logger(self) -> logging.Logger:
        """
        Returns the logger instance to use.

        :return: the logger
        :rtype: logging.Logger
        """
        if self._logger is None:
            if (self.logger_name is not None) and (len(self.logger_name) > 0):
                logger_name = self.logger_name
            else:
                logger_name = self.name()
            self._logger = logging.getLogger(logger_name)
            set_logging_level(self._logger, self.logging_level)
        return self._logger

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        add_logging_level(parser)
        add_logger_name(parser, help_str="The custom name to use for the logger, uses the plugin name by default")
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.logging_level = ns.logging_level
        self.logger_name = ns.logger_name
        self._logger = None


class OutputProducer(object):
    """
    Mixin for classes that generate output.
    """

    def generates(self) -> List:
        """
        Returns the list of classes that get produced.

        :return: the list of classes
        :rtype: list
        """
        raise NotImplementedError()


class InputConsumer(object):
    """
    Mixin for classes that consume input.
    """

    def accepts(self) -> List:
        """
        Returns the list of classes that are accepted.

        :return: the list of classes
        :rtype: list
        """
        raise NotImplementedError()


class Initializable(LoggingHandler):
    """
    Mixin for classes that require initialization and finalization
    """

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        self.logger().info("Initializing...")

    def finalize(self):
        """
        Finishes the processing, e.g., for closing files or databases.
        """
        self.logger().info("Finalizing...")


def init_initializable(handler: Initializable, handler_type: str, raise_again: bool = False) -> bool:
    """
    Initializes the commandline handler and outputs the stacktrace and help screen
    if it fails to do so. Optionally, the exception can be raised again (to propagate).

    :param handler: the handler to initialize
    :type handler: CommandlineHandler
    :param handler_type: the name of the type to use in the error message (eg "reader")
    :type handler_type: str
    :param raise_again: whether to raise the Exception again
    :type raise_again: bool
    :return: whether the initialization was successful
    :rtype: str
    """
    try:
        handler.initialize()
        return True
    except Exception as e:
        if isinstance(handler, Plugin):
            print("\nFailed to initialize %s '%s':\n" % (handler_type, handler.name()), file=sys.stderr)
        else:
            print("\nFailed to initialize %s '%s':\n" % (handler_type, get_class_name(handler)), file=sys.stderr)
        traceback.print_exc()
        if isinstance(handler, Plugin):
            print()
            handler.print_help()
            print()
        if raise_again:
            raise e
        return False


def check_compatibility(plugins: List[Plugin], match_all=AnyData):
    """
    Checks whether the plugins are compatible based on their inputs/outputs.
    Raises an exception if not compatible.

    :param plugins: the list of plugins to check
    :type plugins: list
    :param match_all: the class that always matches
    """
    if len(plugins) == 0:
        return

    for i in range(len(plugins) - 1):
        plugin1 = plugins[i]
        plugin2 = plugins[i + 1]
        index1 = "#" + str(i)
        index2 = "#" + str(i+1)
        if not isinstance(plugin1, OutputProducer):
            raise Exception(index1 + "/" + plugin1.name() + " is not an OutputProducer!")
        if not isinstance(plugin2, InputConsumer):
            raise Exception(index2 + "/" + plugin2.name() + " is not an InputConsumer!")
        classes1 = plugin1.generates()
        classes2 = plugin2.accepts()
        #
        if (match_all in classes1) or (match_all in classes2):
            return
        compatible = False
        for class1 in classes1:
            if class1 in classes2:
                compatible = True
                break
            for class2 in classes2:
                if issubclass(class1, class2):
                    compatible = True
                    break
            if compatible:
                break
        if not compatible:
            raise Exception(
                "Output(s) of " + index1 + "/" + plugin1.name()
                + " not compatible with input(s) of " + index2 + "/" + plugin2.name() + ": "
                + classes_to_str(classes1) + " != " + classes_to_str(classes2))


class SkippablePlugin:
    """
    Mixin for plugins that can be disabled, i.e., get skipped in the pipeline.
    """

    @property
    def is_skipped(self) -> bool:
        """
        Returns whether the plugin is to be skipped.

        :return: True if to be skipped
        :rtype: bool
        """
        return False


def add_skip_option(parser: argparse.ArgumentParser, help_str: str = "Disables the plugin, removing it from the pipeline."):
    """
    Adds the --skip option to the argument parser.

    :param parser: the parser to update
    :type parser: argparse.ArgumentParser
    :param help_str: the help string to use
    :type help_str: str
    """
    parser.add_argument("--skip", action="store_true", default=False, help=help_str, required=False)
