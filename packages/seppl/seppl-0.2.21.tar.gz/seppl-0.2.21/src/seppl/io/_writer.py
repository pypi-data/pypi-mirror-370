import abc
import argparse
from typing import Iterable

from wai.logging import LOGGING_WARNING

from seppl import InputConsumer, PluginWithLogging, SessionHandler, Session, SkippablePlugin, add_skip_option


class Writer(PluginWithLogging, InputConsumer, SessionHandler, SkippablePlugin, abc.ABC):
    """
    Ancestor of classes that write data.
    """

    def __init__(self, logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the handler.

        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)
        self._session = None
        self._last_input = None
        self.skip = False

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        add_skip_option(parser)
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.skip = ns.skip

    @property
    def is_skipped(self) -> bool:
        """
        Returns whether the plugin is to be skipped.

        :return: True if to be skipped
        :rtype: bool
        """
        return self.skip

    @property
    def session(self) -> Session:
        """
        Returns the current session object

        :return: the session object
        :rtype: Session
        """
        return self._session

    @session.setter
    def session(self, s: Session):
        """
        Sets the session object to use.

        :param s: the session object
        :type s: Session
        """
        self._session = s

    def _has_input_changed(self, current_input: str = None, update: bool = False) -> bool:
        """
        Checks whether the current input is different from the last one we processed.

        :param current_input: the current input, uses the current_input from the session if None
        :type current_input: str
        :param update: whether to update the last input immediately
        :type update: bool
        :return: True if input has changed
        :rtype: bool
        """
        if current_input is None:
            current_input = self.session.current_input
        result = self._last_input != current_input
        if update:
            self._update_last_input(current_input)
        return result

    def _update_last_input(self, current_input: str):
        """
        Updates the last input that was processed.

        :param current_input: the "new" last input
        :type current_input: str
        """
        self._last_input = current_input

    def _output_needs_changing(self, current_output: str, target: str, ext: str) -> bool:
        """
        Checks whether the output needs changing.

        :param current_output: the current output
        :type current_output: str
        :param target: the output target
        :type target: str
        :param ext: the extension for the output file, incl dot
        :type ext: str
        :return: True if the output needs to change
        :rtype: bool
        """
        raise NotImplementedError()


class DirectWriter:
    """
    Mixin for classes that support direct writing to file-like objects.
    """
    pass


class StreamWriter(Writer, abc.ABC):
    """
    Ancestor for classes that write data one record at a time.
    """

    def write_stream(self, data):
        """
        Saves the data one by one.

        :param data: the data to write (single record or iterable of records)
        """
        raise NotImplementedError()


class BatchWriter(Writer, abc.ABC):
    """
    Ancestor of classes that write data all at once.
    """

    def write_batch(self, data: Iterable):
        """
        Saves the data in one go.

        :param data: the data to write
        :type data: Iterable
        """
        raise NotImplementedError()


class DirectStreamWriter(DirectWriter):
    """
    Mixin for stream writers that support writing directly to file-like object.
    """

    def write_stream_fp(self, data, fp, as_bytes: bool):
        """
        Saves the data one by one.

        :param data: the data to write (single record or iterable of records)
        :param fp: the file-like object to write to
        :param as_bytes: whether to write as str or bytes
        :type as_bytes: bool
        """
        raise NotImplementedError()


class DirectBatchWriter(DirectWriter):
    """
    Mixin for batch writers that can write to file-like objects directly.
    """

    def write_batch_fp(self, data: Iterable, fp, as_bytes: bool):
        """
        Saves the data in one go.

        :param data: the data to write
        :type data: Iterable
        :param fp: the file-like object to write to
        :param as_bytes: whether to write as str or bytes
        :type as_bytes: bool
        """
        raise NotImplementedError()
