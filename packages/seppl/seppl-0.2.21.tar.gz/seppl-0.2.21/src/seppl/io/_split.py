import argparse
import math
import re
from typing import Dict, List

from ._writer import Writer


def gcd(values: List[int]):
    """
    Computes the greatest common denominator for a list of integers.

    :param values: the integers to find the gcd for (at least 2)
    :type values: list
    :return: the gcd
    :rtype: int
    """
    if len(values) < 2:
        raise Exception("At least two numbers required for gcd!")
    values = values[:]
    result = values.pop(0)
    while len(values) > 0:
        b = values.pop(0)
        result = math.gcd(result, b)
    return result


class Splitter:
    """
    Class for dividing a token stream into sub-streams.
    """

    def __init__(self, split_ratios: List[int], split_names: List[str], split_group: str = None):
        """
        Initializes the splitter.

        :param split_ratios: the list of (int) ratios to use (must sum up to 100)
        :type split_ratios: list
        :param split_names: the list of names to use for the splits
        :type split_names: list
        :param split_group: the (optional) regexp with one group use for keeping items in the same split, e.g., base name of a file or sample ID
        :type split_group: str
        """
        self.split_ratios = split_ratios
        self.split_names = split_names
        self.split_group = split_group
        self._schedule = None
        self._counter = 0
        self._stats = None
        self._groups = None

    def initialize(self):
        """
        Initializes the splitter, throws exceptions if undefined state or incorrect values.
        """
        if self.split_ratios is None:
            raise Exception("No split ratios defined!")
        if self.split_names is None:
            raise Exception("No split name defined!")
        if len(self.split_ratios) != len(self.split_names):
            raise Exception("Differing number of split ratios and names: %d != %d" % (len(self.split_ratios), len(self.split_names)))
        if sum(self.split_ratios) != 100:
            raise Exception("Split ratios must sum up to 100, but got: %d" % sum(self.split_ratios))

        # compute greatest common denominator and generate schedule
        _gcd = gcd(self.split_ratios)
        self._schedule = [0] * (len(self.split_ratios) + 1)
        for i, ratio in enumerate(self.split_ratios):
            self._schedule[i + 1] = self._schedule[i] + ratio / _gcd
        self._counter = 0
        self._stats = dict()
        self._groups = dict()

    def reset(self):
        """
        Resets the counter and stats.
        """
        self._counter = 0
        self._stats = dict()
        self._groups = dict()

    def next(self, item: str = None) -> str:
        """
        Returns the next split name.

        :param item: the item to extract the group from
        :type item: str
        :return: the name of the split
        :rtype: str
        """
        # did the group already have a split assigned?
        group = None
        if (item is not None) and (self.split_group is not None):
            m = re.match(self.split_group, item)
            if m is not None:
                group = m.group(1)
                if group in self._groups:
                    return self._groups[group]

        split = None
        for i in range(len(self.split_names)):
            if (self._counter >= self._schedule[i]) and (self._counter < self._schedule[i + 1]):
                split = self.split_names[i]

        # update counter
        self._counter += 1
        if self._counter == self._schedule[-1]:
            self._counter = 0

        # update stats
        if split not in self._stats:
            self._stats[split] = 0
        self._stats[split] += 1

        # record split for the group
        if group is not None:
            self._groups[group] = split

        return split

    def stats(self) -> Dict:
        """
        Returns the statistics.
        """
        return self._stats

    def counter(self) -> int:
        """
        Returns the counter.
        """
        return self._counter


def init_splitting_params(writer: Writer, split_names: List[str] = None, split_ratios: List[int] = None, split_group: str = None):
    """
    Initializes the splitting parameters of the writer.

    :param writer: the writer to initialize
    :type writer: Writer
    :param split_names: the names of the splits, no splitting if None
    :type split_names: list
    :param split_ratios: the integer ratios of the splits (must sum up to 100)
    :type split_ratios: list
    :param split_group: the regular expression with a single group used for keeping items in the same split, e.g., for identifying the base name of a file or the sample ID
    :type split_group: str
    """
    writer.split_names = split_names[:] if (split_names is not None) else None
    writer.split_ratios = split_ratios[:] if (split_ratios is not None) else None
    writer.split_group = split_group
    writer.splitter = None


def add_splitting_params(parser: argparse.ArgumentParser):
    """
    Adds the split ratios/names parameters to the parser.

    :param parser: the parser
    :type parser: argparse.ArgumentParser
    """
    parser.add_argument("--split_ratios", type=int, default=None, help="The split ratios to use for generating the splits (must sum up to 100)", nargs="+")
    parser.add_argument("--split_names", type=str, default=None, help="The split names to use for the generated splits.", nargs="+")
    parser.add_argument("--split_group", type=str, default=None, help="The regular expression with a single group used for keeping items in the same split, e.g., for identifying the base name of a file or the sample ID.")


def transfer_splitting_params(ns: argparse.Namespace, writer: Writer):
    """
    Transfers the splitting parameters from the parsed namespace into the writer.

    :param ns: the namespace to transfer from
    :type ns: argparse.Namespace
    :param writer: the writer to update
    :type writer: Writer
    """
    writer.split_names = ns.split_names[:] if ((ns.split_names is not None) and (len(ns.split_names) > 0)) else None
    writer.split_ratios = ns.split_ratios[:] if ((ns.split_ratios is not None) and (len(ns.split_ratios) > 0)) else None
    writer.split_group = ns.split_group


def initialize_splitting(writer: Writer):
    """
    Initializes the splitting in the writer.

    :param writer: the writer to initialize, if necessary
    :type writer: Writer
    """
    if not hasattr(writer, "split_names"):
        return
    if (getattr(writer, "split_names") is None) or (getattr(writer, "split_ratios") is None):
        return
    writer.splitter = Splitter(split_ratios=writer.split_ratios, split_names=writer.split_names, split_group=writer.split_group)
    writer.splitter.initialize()
