import importlib
import inspect
import os
import sys
import traceback
from typing import Callable, Union, List, Optional, Type, Dict

if sys.version_info < (3, 10):
    from importlib_metadata import entry_points
else:
    from importlib.metadata import entry_points

from ._types import get_class_name, get_class
from ._plugin import Plugin, get_all_names, get_aliases

DEFAULT = "DEFAULT"
""" the placeholder for the default class listers in the environment variable. """

LIST_CLASSES = "list_classes"
""" the default method for listing classes. """


def get_class_lister(class_lister: str) -> Callable:
    """
    Parses the class_lister definition and returns the function.
    The default format is "module_name:function_name".
    If ":function_name" is omitted it is assumed to be ":list_classes".

    :param class_lister: the class lister definition to parse
    :type class_lister: str
    :return: the parsed function
    """
    if ":" not in class_lister:
        module_name = class_lister
        func_name = LIST_CLASSES
    else:
        module_name, func_name = class_lister.split(":")

    try:
        module = importlib.import_module(module_name)
    except:
        raise Exception("Failed to import class lister module: %s" % module_name)

    if hasattr(module, func_name):
        func = getattr(module, func_name)
        if inspect.isfunction(func):
            return func
        else:
            raise Exception("Class lister function is not an actual function: %s" % class_lister)
    else:
        raise Exception("Class lister function '%s' not found in module '%s'!" % (func_name, module_name))


class ClassListerRegistry:
    """
    Registry for managing class hierarchies via class listers.
    """

    def __init__(self, default_class_listers: Union[str, List[str]] = None, env_class_listers: str = None,
                 excluded_class_listers: Union[str, List[str]] = None, env_excluded_class_listers: str = None,
                 ignored_class_listers: Union[str, List[str]] = None, env_ignored_class_listers: str = None):
        """

        :param default_class_listers: the default class lister(s) to use
        :type default_class_listers: str or list
        :param env_class_listers: the environment variable to retrieve the class lister(s) from
        :type env_class_listers: str
        :param excluded_class_listers: the class lister(s) to exclude from being used
        :type excluded_class_listers: str or list
        :param env_excluded_class_listers: the environment variable to retrieve the excluded class lister(s) from
        :type env_excluded_class_listers: str
        :param ignored_class_listers: the class lister(s) providing classes that should be ignored
        :type ignored_class_listers: str or list
        :param env_ignored_class_listers: the environment variable to retrieve the class lister(s) providing ignored clases
        :type env_ignored_class_listers: str
        """

        self._classes = dict()
        self._all_aliases = set()
        self._default_class_listers = None
        self._env_class_listers = None
        self._excluded_class_listers = None
        self._env_excluded_class_listers = None
        self._ignored_class_listers = None
        self._env_ignored_class_listers = None
        self._custom_class_listers = None

        self.default_class_listers = default_class_listers
        self.env_class_listers = env_class_listers
        self.excluded_class_listers = excluded_class_listers
        self.env_excluded_class_listers = env_excluded_class_listers
        self.ignored_class_listers = ignored_class_listers
        self.env_ignored_class_listers = env_ignored_class_listers

    @property
    def default_class_listers(self) -> Optional[List[str]]:
        """
        Returns the class lister functions.

        :return: the functions
        :rtype: list
        """
        return self._default_class_listers

    @default_class_listers.setter
    def default_class_listers(self, class_listers: Optional[Union[str, List[str]]]):
        """
        Sets/unsets the class lister functions to use. Clears the class cache.

        :param class_listers: the list of class listers to use, None to unset
        :type class_listers: list
        """
        if class_listers is None:
            class_listers = ""
        if isinstance(class_listers, str):
            class_listers = [x.strip() for x in class_listers.split(",")]
        elif isinstance(class_listers, list):
            class_listers = class_listers[:]
        else:
            raise Exception("default_class_listers must be either str or list, but got: %s" % str(type(class_listers)))
        self._default_class_listers = class_listers
        self._classes = dict()

    @property
    def env_class_listers(self) -> Optional[str]:
        """
        Returns the environment variable with the class lister functions (if any).

        :return: the class lister functions, None if none set
        :rtype: str
        """
        return self._env_class_listers

    @env_class_listers.setter
    def env_class_listers(self, class_listers: Optional[str]):
        """
        Sets/unsets the environment variable with the class lister functions to use. Clears the class cache.

        :param class_listers: the environment variable with the class lister functions to use, None to unset
        :type class_listers: str
        """
        self._env_class_listers = class_listers
        self._classes = dict()

    @property
    def excluded_class_listers(self) -> Optional[List[str]]:
        """
        Returns the excluded class lister functions.

        :return: the functions
        :rtype: list
        """
        return self._excluded_class_listers

    @excluded_class_listers.setter
    def excluded_class_listers(self, excluded_class_listers: Optional[Union[str, List[str]]]):
        """
        Sets/unsets the excluded class lister functions to use. Clears the class cache.

        :param excluded_class_listers: the list of excluded class listers to use, None to unset
        :type excluded_class_listers: list
        """
        if excluded_class_listers is None:
            excluded_class_listers = ""
        if isinstance(excluded_class_listers, str):
            excluded_class_listers = [x.strip() for x in excluded_class_listers.split(",")]
        elif isinstance(excluded_class_listers, list):
            excluded_class_listers = excluded_class_listers[:]
        else:
            raise Exception("excluded_class_listers must be either str or list, but got: %s" % str(type(excluded_class_listers)))
        self._excluded_class_listers = excluded_class_listers
        self._classes = dict()

    @property
    def env_excluded_class_listers(self) -> Optional[str]:
        """
        Returns the environment variable with the excluded class lister functions (if any).

        :return: the excluded class lister functions, None if none set
        :rtype: str
        """
        return self._env_excluded_class_listers

    @env_excluded_class_listers.setter
    def env_excluded_class_listers(self, excluded_class_listers: Optional[str]):
        """
        Sets/unsets the environment variable with the excluded class lister functions to use. Clears the class cache.

        :param excluded_class_listers: the environment variable with the excluded class lister functions to use, None to unset
        :type excluded_class_listers: str
        """
        self._env_excluded_class_listers = excluded_class_listers
        self._classes = dict()

    @property
    def ignored_class_listers(self) -> Optional[List[str]]:
        """
        Returns the class lister functions providing ignored classes.

        :return: the functions
        :rtype: list
        """
        return self._ignored_class_listers

    @ignored_class_listers.setter
    def ignored_class_listers(self, ignored_class_listers: Optional[Union[str, List[str]]]):
        """
        Sets/unsets the class lister functions providing ignored classes. Clears the class cache.

        :param ignored_class_listers: the list of class listers providing ignored classes, None to unset
        :type ignored_class_listers: list
        """
        if ignored_class_listers is None:
            ignored_class_listers = ""
        if isinstance(ignored_class_listers, str):
            ignored_class_listers = [x.strip() for x in ignored_class_listers.split(",")]
        elif isinstance(ignored_class_listers, list):
            ignored_class_listers = ignored_class_listers[:]
        else:
            raise Exception("ignored_class_listers must be either str or list, but got: %s" % str(type(ignored_class_listers)))
        self._ignored_class_listers = ignored_class_listers
        self._classes = dict()

    @property
    def env_ignored_class_listers(self) -> Optional[str]:
        """
        Returns the environment variable with the class lister functions providing ignored classes (if any).

        :return: the class lister functions providing ignored classes, None if none set
        :rtype: str
        """
        return self._env_ignored_class_listers

    @env_ignored_class_listers.setter
    def env_ignored_class_listers(self, ignored_class_listers: Optional[str]):
        """
        Sets/unsets the environment variable with the class lister functions providing ignored classes. Clears the class cache.

        :param ignored_class_listers: the environment variable with the class lister functions providing ignored classes, None to unset
        :type ignored_class_listers: str
        """
        self._env_ignored_class_listers = ignored_class_listers
        self._classes = dict()

    @property
    def custom_class_listers(self) -> Optional[List[str]]:
        """
        Returns the custom class listers (if any).

        :return: the class listers, None if none set
        :rtype: list
        """
        return self._custom_class_listers

    @custom_class_listers.setter
    def custom_class_listers(self, class_listers: Optional[Union[str, List[str]]]):
        """
        Sets/unsets the custom class listers to use. Clears the plugin cache.

        :param class_listers: the list of class listers to use, None to unset
        :type class_listers: list
        """
        self._custom_class_listers = class_listers
        self._classes = dict()

    def has_env_class_listers(self) -> bool:
        """
        Checks whether an environment variable for class listers is set.

        :return: True if set
        :rtype: bool
        """
        return (self._env_class_listers is not None) \
               and (len(self._env_class_listers) > 0) \
               and (os.getenv(self._env_class_listers) is not None) \
               and (len(os.getenv(self._env_class_listers)) > 0)

    def has_env_excluded_class_listers(self) -> bool:
        """
        Checks whether an environment variable for excluded class listers is set.

        :return: True if set
        :rtype: bool
        """
        return (self._env_excluded_class_listers is not None) \
               and (len(self._env_excluded_class_listers) > 0) \
               and (os.getenv(self._env_excluded_class_listers) is not None) \
               and (len(os.getenv(self._env_excluded_class_listers)) > 0)

    def has_env_ignored_class_listers(self) -> bool:
        """
        Checks whether an environment variable for class listers providing ignored classes is set.

        :return: True if set
        :rtype: bool
        """
        return (self._env_ignored_class_listers is not None) \
               and (len(self._env_ignored_class_listers) > 0) \
               and (os.getenv(self._env_ignored_class_listers) is not None) \
               and (len(os.getenv(self._env_ignored_class_listers)) > 0)
    
    def _expand_default_class_listers_placeholder(self, c: str) -> str:
        """
        Expands the DEFAULT class listers placeholder in the comma-separated class listers string.

        :param c: the class listers string to expand
        :type c: str
        :return: the expanded class listers string
        :rtype: str
        """
        if DEFAULT in c:
            if len(self.default_class_listers) > 0:
                c = c.replace(DEFAULT, ",".join(self.default_class_listers))
            else:
                c = c.replace(DEFAULT, "")
        return c

    def actual_fallback_class_listers(self) -> List[str]:
        """
        Returns list the of class listers to fall back on.
        Precedence: custom_class_listers > env_class_listers > default_class_listers

        :return: the list of class listers
        :rtype: list
        """
        if (self._custom_class_listers is not None) and (len(self._custom_class_listers) > 0):
            return self._custom_class_listers

        if self.has_env_class_listers():
            m = self._expand_default_class_listers_placeholder(os.getenv(self.env_class_listers))
            return [x.strip() for x in m.split(",")]

        return self.default_class_listers[:]

    def actual_excluded_class_listers(self) -> List[str]:
        """
        Returns list the of excluded class listers.
        Precedence: excluded_env_class_listers > excluded_class_listers

        :return: the list of class listers
        :rtype: list
        """
        if self.has_env_excluded_class_listers():
            m = self._expand_default_class_listers_placeholder(os.getenv(self._env_excluded_class_listers))
            return [x.strip() for x in m.split(",")]

        return self.excluded_class_listers[:]

    def actual_ignored_class_listers(self) -> List[str]:
        """
        Returns list the of class listers providing ignored classes.
        Precedence: ignored_env_class_listers > ignored_class_listers

        :return: the list of class listers
        :rtype: list
        """
        if self.has_env_ignored_class_listers():
            m = self._expand_default_class_listers_placeholder(os.getenv(self._env_ignored_class_listers))
            return [x.strip() for x in m.split(",")]

        return self.ignored_class_listers[:]

    def _determine_sub_classes(self, cls: Type, module_name: str) -> List[str]:
        """
        Determines all the sub-classes of type cls in the specified module.

        :param cls: the superclass
        :param module_name: the module to look for sub-classes
        :type module_name: str
        :return: the list of sub-classes
        :rtype: list
        """
        result = []

        try:
            module = importlib.import_module(module_name)
        except:
            print("Failed to import module: %s" % module_name, file=sys.stderr)
            traceback.print_exc()
            return result

        for att_name in dir(module):
            if att_name.startswith("_"):
                continue
            if att_name.startswith("Abstract"):
                continue
            att = getattr(module, att_name)
            if inspect.isclass(att) and not inspect.isabstract(att) and issubclass(att, cls):
                try:
                    obj = att()
                except NotImplementedError:
                    pass
                except:
                    print("Problem encountered instantiating: %s" % (module_name + "." + att_name), file=sys.stderr)
                    traceback.print_exc()
                    continue
                result.append(get_class_name(att))

        return result

    def _determine_ignored_classes_from_class_listers(self, c: str, class_listers: List[str]) -> List[str]:
        """
        Determines the ignored classes via the specified class listers.

        :param c: the superclass to get the classes for
        :type c: str
        :param class_listers: the class lister functions to use
        :type class_listers: list
        :return: the determined list of ignored classes
        :rtype: list
        """
        result = []

        if len(class_listers) > 0:
            cls = None

            for class_lister in class_listers:
                if class_lister == "":
                    continue

                if cls is None:
                    try:
                        cls = get_class(c)
                    except:
                        print("Failed to instantiate class: %s" % c, file=sys.stderr)
                        traceback.print_exc()
                        return result

                try:
                    func = get_class_lister(class_lister)
                except:
                    print("Problem encountered with class lister: %s" % class_lister, file=sys.stderr)
                    traceback.print_exc()
                    continue

                if self.excluded_class_listers is not None:
                    if class_lister in self.excluded_class_listers:
                        continue

                if inspect.isfunction(func):
                    class_dict = func()
                    if c in class_dict:
                        result.extend(class_dict[c])

        return result

    def _determine_from_class_listers(self, c: str, class_listers: List[str]) -> List[str]:
        """
        Determines the derived classes via the specified class listers.

        :param c: the superclass to get the classes for
        :type c: str
        :param class_listers: the class lister functions to use
        :type class_listers: list
        :return: the determined list of subclasses
        :rtype: list
        """
        result = []

        if len(class_listers) > 0:
            cls = None

            for class_lister in class_listers:
                if class_lister == "":
                    continue

                if cls is None:
                    try:
                        cls = get_class(c)
                    except:
                        print("Failed to instantiate class: %s" % c, file=sys.stderr)
                        traceback.print_exc()
                        return result

                try:
                    func = get_class_lister(class_lister)
                except:
                    print("Problem encountered with class lister: %s" % class_lister, file=sys.stderr)
                    traceback.print_exc()
                    continue

                if self.excluded_class_listers is not None:
                    if class_lister in self.excluded_class_listers:
                        continue

                if inspect.isfunction(func):
                    class_dict = func()
                    if c in class_dict:
                        for sub_module in class_dict[c]:
                            sub_classes = self._determine_sub_classes(cls, sub_module)
                            result.extend(sub_classes)

        return result

    def _determine_from_entry_points(self, c: str) -> List[str]:
        """
        Determines the derived classes via class listers defined as entry points.

        :param c: the superclass to get the classes for
        :type c: str
        :return: the determined list of subclasses
        :rtype: list
        """
        result = []
        class_listers = []
        for item in entry_points(group="class_lister"):
            class_listers.append(item.value)
        if len(class_listers) > 0:
            result = self._determine_from_class_listers(c, class_listers)
        return result

    def _determine_from_env(self, c: str) -> List[str]:
        """
        Determines the derived classes via class listers defined through the environment variable.

        :param c: the superclass to get the classes for
        :type c: str
        :return: the determined list of subclasses
        :rtype: list
        """
        result = []

        if os.getenv(self.env_class_listers) is not None:
            # format: "classlister1,classlister2,..."
            # classlister format: "module_name:function_name" or "module_name" if "list_classes" as method
            class_listers = os.getenv(self.env_class_listers).split(",")
            result = self._determine_from_class_listers(c, class_listers)

        return result

    def _initialize(self, c: str):
        """
        Initializes the class cache for the specified superclass.

        :param c: the superclass to initialize the cache for
        :type c: str
        :return: the list of classes for the superclass
        :rtype: list
        """
        all_classes = set()

        # from entry points
        entry_point_classes = self._determine_from_entry_points(c)
        if entry_point_classes is not None:
            all_classes.update(entry_point_classes)

        # register from class listers as well?
        if (len(all_classes) == 0) or ((self._custom_class_listers is not None) and (len(self._custom_class_listers) > 0)) or self.has_env_class_listers():
            actual = self.actual_fallback_class_listers()
            all_classes.update(self._determine_from_class_listers(c, actual))

        # excluded classes?
        excluded_listers = self.actual_excluded_class_listers()
        excluded_classes = self._determine_from_class_listers(c, excluded_listers)
        for cls in excluded_classes:
            if cls in all_classes:
                all_classes.remove(cls)
                
        # ignored classes?
        ignored_listers = self.actual_ignored_class_listers()
        ignored_classes = self._determine_ignored_classes_from_class_listers(c, ignored_listers)
        for cls in ignored_classes:
            if cls in all_classes:
                all_classes.remove(cls)
                
        self._classes[c] = sorted(list(all_classes))

    def plugins(self, c: Union[str, Type], fail_if_empty: bool = True) -> Dict[str, Plugin]:
        """
        Returns the classes for the specified superclass.

        :param c: the super class to get the derived classes for (classname or type)
        :param fail_if_empty: whether to raise an exception if no classes present
        :type fail_if_empty: bool
        :return: the list of classes
        :rtype: list
        """
        if not isinstance(c, str):
            c = get_class_name(c)
        if c not in self._classes:
            self._initialize(c)
        result = dict()
        if c in self._classes:
            for cname in self._classes[c]:
                try:
                    cls = get_class(cname)
                    plugin = cls()
                    names = get_all_names(plugin)
                    for name in names:
                        result[name] = plugin
                        # record any aliases
                        self._all_aliases.update(get_aliases(plugin))
                except NotImplementedError:
                    pass
                except:
                    print("Failed to instantiate: %s" % cname)
                    traceback.print_exc()
        if fail_if_empty and (len(result) == 0):
            raise Exception("No classes found for: %s" % c)
        return result

    @property
    def all_aliases(self) -> List[str]:
        """
        Returns a sorted list of all known aliases.
        Due to dynamic instantiation the call to all_aliases must come after the relevant plugins(...) call.

        :return: the list of all known aliases
        :rtype: list
        """
        return sorted(list(self._all_aliases))

    def is_alias(self, name: str) -> bool:
        """
        Checks whether the plugin name is an alias.
        Due to dynamic instantiation the call to is_alias(...) must come after the relevant plugins(...) call.

        :param name: the plugin name to check
        :type name: str
        :return: True if an alias
        :rtype: bool
        """
        return name in self._all_aliases
