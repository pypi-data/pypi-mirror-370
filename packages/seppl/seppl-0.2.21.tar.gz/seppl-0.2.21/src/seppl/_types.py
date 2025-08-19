import importlib
import inspect

from typing import Optional, Tuple, List


class AnyData:
    """
    Dummy class that can be used for matching anything in compatibility tests.
    """
    pass


def get_class(full_class_name: Optional[str] = None,
              module_name: Optional[str] = None, class_name: Optional[str] = None) -> type:
    """
    Returns the class object associated with the dot-notation classname.
    Either the fully qualified class name or module and class name can be supplied.

    :param full_class_name: the classname (module + name)
    :type full_class_name: str
    :param module_name: the name of the module
    :type module_name: str
    :param class_name: the
    :return: the class object
    """
    if full_class_name is not None:
        parts = full_class_name.split('.')
        module = ".".join(parts[:-1])
        m = importlib.import_module(module)
        c = getattr(m, parts[-1])
        return c
    elif (module_name is not None) and (class_name is not None):
        m = importlib.import_module(module_name)
        c = getattr(m, class_name)
        return c
    else:
        raise Exception("Either fully qualified class name or module and class name must be supplied!")


def fix_module_name(module: str, cls: str) -> Tuple[str, str]:
    """
    Turns a.b._C.C into a.b.C if possible.

    :param module: the module
    :type module: str
    :param cls: the class name
    :type cls: str
    :return: the (potentially) updated tuple of module and class name
    :rtype: tuple
    """
    if module.split(".")[-1].startswith("_"):
        try:
            module_short = ".".join(module.split(".")[:-1])
            getattr(importlib.import_module(module_short), cls)
            module = module_short
        except Exception:
            pass
    return module, cls


def get_class_name(obj: object) -> str:
    """
    Returns the fully qualified classname of the Python class or object.

    :param obj: the Python class/object to get the classname for
    :type obj: object
    :return: the generated classname
    :rtype: str
    """
    if inspect.isclass(obj):
        m, c = fix_module_name(obj.__module__, obj.__name__)
        return m + "." + c
    else:
        return get_class_name(obj.__class__)


def classes_to_str(classes: List):
    """
    Turns a list of classes into a string.

    :param classes: the list of classes to convert
    :type classes: list
    :return: the generated string
    :rtype: str
    """
    classes_str = list()
    for cls in classes:
        classes_str.append(get_class_name(cls))
    return ", ".join(classes_str)
