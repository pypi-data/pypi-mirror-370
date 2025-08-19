Changelog
=========

0.2.21 (2025-08-19)
-------------------

- the `ClassRegistry` now supports class listers that list class names (not modules!) to be *ignored*,
  i.e., ones that should be returned for their class hierarchies; useful when excluding
  inherited plugins that are not applicable in the concrete application


0.2.20 (2025-07-15)
-------------------

- the `is_help_requested` method can now pinpoint whether global help or help for a specific
  plugin was requested (requires supplying a list of valid handler names and whether to use
  partial matching)
- the `args_to_objects` method now resolves the plugin name and throws an error if it is
  flagged as unknown


0.2.19 (2025-07-10)
-------------------

- the write methods of `DirectStreamWriter` and `DirectBatchWriter` now have the additional
  `as_bytes` parameter, to indicate whether whether to write as bytes or str


0.2.18 (2025-07-03)
-------------------

- formalized support for direct read from/write to file-like objects with the
  `DirectReader`, `DirectStreamWriter`, `DirectBatchWriter` mixins


0.2.17 (2025-06-26)
-------------------

- replaced deprecated `pkg_resources` with `importlib.metadata`-based approach
  (based on: https://packaging.python.org/en/latest/guides/creating-and-discovering-plugins/#using-package-metadata)


0.2.16 (2025-04-08)
-------------------

- filters and writers can be skipped now via the `--skip` flag, making it easy for external
  scripts to enable/disable pipeline components


0.2.15 (2025-03-28)
-------------------

- added support to the `seppl.io.Splitter` class for keeping item/sample groups together via a `split_group`
  regular expression
- backported helper methods for `seppl.io.Writer` classes for managing splitting


0.2.14 (2025-03-24)
-------------------

- added `resume_from` parameter to `seppl.io.locate_files` method which allows to skip all
  files preceding this glob


0.2.13 (2025-03-14)
-------------------

- the `resolve_handler` and `split_args` methods now have the `partial` boolean
  parameter which determines whether partial matches are accepted or not; off
  by default as it can interfere with parameters from plugins


0.2.12 (2025-03-13)
-------------------

- moved placeholder functionality from `seppl` to `seppl.placeholders`
- `load_user_defined_placeholders` now ignores lines that start with #


0.2.11 (2025-03-13)
-------------------

- added support for placeholders, which can be expanded via the `Session` object
- plugins supporting placeholders should import the `PlaceholderSupporter` indicator
  mixin for automatically adding help on placeholders to the help screen; plugins
  that support placeholders based on the current input should import the
  `InputBasedPlaceholderSupporter` indicator mixin
- placeholder-supporting plugins can use the `placeholder_list` method in their argparse options
- the `load_user_defined_placeholders` method allows incorporating custom placeholders for directories


0.2.10 (2025-02-11)
-------------------

- added alias support to the `ClassRegistry` class
- added method `is_alias(...)` and property `all_aliases` to the `Registry` and `ClassRegistry` classes
- extended the `enumerate_plugins` method to allow flagging of aliases (default: `*`)


0.2.9 (2025-01-24)
------------------

- added support for using partial handler/plugin names (as long as they are unique)
- added experimental support for aliases with `AliasSupporter` mixin


0.2.8 (2024-12-20)
------------------

- added `setuptools` as dependency


0.2.7 (2024-08-29)
------------------

- the `seppl.io.locate_files` method can support recursive globs now (default is no)


0.2.6 (2024-07-01)
------------------

- reworked the `execute` method, properly distinguishing between stream/batch mode now


0.2.5 (2024-06-18)
------------------

- the `seppl.io.locate_files` method can take a default glob now, which gets appended
  to inputs that point to directories


0.2.4 (2024-05-06)
------------------

- reworked excluding of classes


0.2.3 (2024-05-03)
------------------

- `_determine_from_entry_points` method of `ClassListerRegistry` class now checks whether
  there the attributes tuple has any elements (i.e., whether the optional `:function_name`
  was provided)
- message `X records processed in total` now only output at the end


0.2.2 (2024-05-02)
------------------

- `ClassListerRegistry` now safely removes any excluded class listers before locating the classes


0.2.1 (2024-05-02)
------------------

- `ClassListerRegistry` now removes any excluded class listers before locating the classes


0.2.0 (2024-05-01)
------------------

- the `execute` method no longer counts `None` items returned by the reader
- added the `seppl.ClassListerRegistry` class that offers a more convenient way of
  discovering classes via a function that returns a dictionary of superclasses and
  the associated modules to inspect; with this approach only a single entry_point
  has to be defined in `setup.py`, pointing to the class lister module/function


0.1.3 (2024-02-29)
------------------

- added the dummy type `AnyData` which is used by default in the `check_compatibility`
  method for a *match all* (ie can be used for general purpose plugins)


0.1.2 (2024-02-22)
------------------

- added methods `escape_args` and `unescape_args` (and corresponding command-line
  tools `seppl-escape` and `seppl-unescape`) for escaping/unescaping unicode
  characters in command-lines to make them copyable across ssh sessions


0.1.1 (2024-02-07)
------------------

- `check_compatibility` method now also checks whether generated class is
  subclass of accepted classes, to allow for broader `accepts()` methods
- `gcd` method now creates a copy of the integer ratio list before processing it


0.1.0 (2024-02-05)
------------------

- added basic support for meta-data: MetaDataHandler, get_metadata, add_metadata
- added support for splitting sequences using supplied (int) split ratios
- added session support: Session, SessionHandler
- added I/O super classes: Reader, Writer, StreamWriter, BatchWriter, Filter, MultiFilter
- added support for executing I/O pipelines: Reader, [Filter...], [Writer]


0.0.11 (2023-11-27)
-------------------

- the `DEFAULT` placeholder in the environment variable listing the modules now
  gets expanded to the default modules, making it easier to specify modules
  in derived projects
- added `excluded_modules` and `excluded_env_modules` to `Registry` class
  initializer to allow user to specify modules (explicit list or list from env
  variable) to be excluded from being registered; useful when outputting
  help for derived modules that shouldn't output all the base plugins as well.


0.0.10 (2023-11-15)
-------------------

- the registry now inspects modules when environment modules are present even when
  it already found plugins (eg default ones)


0.0.9 (2023-11-15)
------------------

- the registry now inspects modules when custom modules were supplied even when
  it already found plugins (eg default ones)


0.0.8 (2023-11-10)
------------------

- suppressing help output for unknown args now


0.0.7 (2023-11-09)
------------------

- `Plugin.parse_args` now returns any unparsed arguments that were found
- the `args_to_objects` method now raises an Exception by default when
  unknown arguments are encountered for a plugin (can be controlled with
  the `allow_unknown_args` parameter)


0.0.6 (2023-10-11)
------------------

- enforcement of uniqueness is now checking whether the class names differ
  before raising an exception.


0.0.5 (2023-10-10)
------------------

- added `OutputProducer` and `InputConsumer` mixins that can be use for checking
  the compatibility between pipeline components using the `check_compatibility`
  function.


0.0.4 (2023-10-09)
------------------

- added support for `dynamic` mode which only requires listing the superclass of a plugin
  and the module in which to look for these plugins (slower, but more convenient)


0.0.3 (2023-10-05)
------------------

- added `generate_entry_points` helper method to easily generate the `entry_points` section
  for plugins, rather than manually maintaining it
- added `generate_help` and `generate_plugin_usage` methods for generating documentation
  for plugins


0.0.2 (2023-10-04)
------------------

- removed old, logging-related code from Plugin class
- added `args_to_objects` to quickly instantiate plugins from parsed arguments
- added example to README.md and example library (https://github.com/waikato-datamining/seppl-example)


0.0.1 (2023-09-28)
------------------

- initial release

