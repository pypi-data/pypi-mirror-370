# seppl
<img align="right" src="img/seppl_logo.png" width="15%" alt="Seppl logo showing a pixelated Seppl hand puppet, based on https://de.wikipedia.org/wiki/Seppel#/media/Datei:Seppl.JPG"/>

Simple Entry Point PipeLines (**seppl**). Python library for parsing pipeline 
components with their own options. 

**seppl** takes a very light-weight approach to avoid encroaching too much on
your code. If you want to, you can add some compatibility checks between the 
pipeline components (see further down).
However, the execution of the pipeline (and potentially moving data between 
components) is left to you and your code.


## Installation

### PyPI

```bash
pip install seppl 
```

### Github

```bash
pip install git+https://github.com/waikato-datamining/seppl.git
```


## Usage

### Registry

*seppl* can operate in three different modes:

* [class lister registry](docs/class_lister_registry.md) - a single function (aka class lister) returns a dictionary  
  of superclasses and their associated modules (slower, due to analyzing code) 
* [dynamic registry](docs/dynamic_registry.md) - only superclass and module need to be supplied for initializing 
  a plugin class hierarchy (slower, due to analyzing code)
* [explicit registry](docs/explicit_registry.md) - every single plugin needs to be listed (fast)


### Plugins

Your plugins need to be derived from the `seppl.Plugin` superclass, for the
*magic* to work. Such a plugin needs to implement the following two methods:

* `name(self)`: returns the name/identifier to use in the pipeline command string 
  (potentially followed by options for the plugin to parse)
* `description(self)`: returns a description (how long is up to you), which is used
  for the argparse parser; the same parser that can be used to generate a help
  screen for a plugin

In order to have custom options parsed by your plugin, you need to override
the following two methods:

* `_create_argparser(self)`: this method assembles the argparse parser
* `_apply_args(self, ns: argparse.Namespace)`: in this method, you need to 
  transfer the parsed options into member variables of your plugin 

The `SkippablePlugin` mixin, as implemented by `Filter` and `Writer`, allows
the disabling of the plugin via the `--skip` flag. Plugins that were disabled
this way, get automatically removed when calling the `args_to_objects` function.
This is an easy way of turning on/off parts of a pipeline without having to
remove complex filter/writer configurations.


### Aliases

If you want to have the ability to allow shorthand names for your plugins as well,
then you can do that by using the `seppl.AliasSupporter` mixin. The plugins will
simply be added under their aliases to the class registry as well (inflating the 
number of *available* plugins).

The following low-level methods are available for aliases:

* `has_aliases` - checks whether a plugin has any aliases
* `get_aliases` - retrieves any aliases and simply returns an empty list if not an `AliasSupporter`

The `Registry` and `ClassRegistry` classes have the following methods/properties 
to aid in the handling of aliases:

* `is_alias(str)` - checks whether a plugin is an alias
* `all_alias` - returns a sorted list of all known aliases

**NB:** Due to the dynamic instantiation that `ClassRegistry` uses, the aliases
are only being populated after appropriate calls to the `plugin(...)` method.


### Compatibility

If you want to enable checks between pipeline components, then your plugins
need to implement the appropriate mixins and implement the relevant methods:

* `seppl.OutputProducer`: for plugins that generate data; the `generates` method
  returns a list of classes that the plugin can output (typically only one).
* `seppl.InputConsumer`: for plugins that consume data; the `accepts` method
  returns a list of classes that the plugin can process.

E.g., *reader* plugins would implement `OutputProducer`, *filters* would 
implement both, `OutputProducer` and `InputConsumer`, and *writers* only
`InputConsumer`.

You can then run the `check_compatibility` method against your pipeline,
i.e., a list of plugins, to see whether they are compatible. This method will
raise an exception if plugins are not implementing the mixins or if there is
no overlap between the generated/accepted classes.

For general purpose plugins, you can use `AnyData` dummy class in the
`accepts`/`generates` methods, as this class is used by default as a 
*match all* by the `check_compatibility` method.

See the plugins in [plugins_comp.py](https://github.com/waikato-datamining/seppl-example/blob/main/src/my/plugins_comp.py)
and [some example pipeline checks](https://github.com/waikato-datamining/seppl-example/blob/main/src/my/usage/compatibility.py)
done with them. 


### Unicode characters

The following methods can be used for escaping/unescaping unicode characters
to make them copyable into remote ssh sessions:

* `seppl.escape_args`
* `seppl.unescape_args`


### Placeholders

seppl offers basic support for placeholders in files and directories. If a 
plugin makes use of placeholders, it should import the relevant indicator
mixin as the help screen generation outputs placeholder information at the
bottom of the screen. The following mixins are available:

* `seppl.placeholders.PlaceholderSupporter` - for placeholders that don't rely on the current input, typically *readers*
* `seppl.placeholders.InputBasedPlaceholderSupporter` - also supports placeholders that make use of the current input, typically *filters* and *writers*

When defining argparse options, you can use the `placeholder_list(...)` 
method to append a short list of available placeholders, e.g.:

```python
from seppl.placeholders import placeholder_list
...
parser.add_argument("-i", "--input", type=str, required=False, nargs="*", 
                    help="Path to the file(s) to read; glob syntax is supported; " + placeholder_list(obj=self))
```

The `seppl.io.locate_files` method automatically expands placeholders that do 
not require the current input.

For expanding placeholders at runtime, you can use the `expand_placeholders`
method of the session object of the plugin, which automatically includes
the current input as part of the expansion. 

For example, for an output file of a writer, the call would typically look 
like this:

```python
output_file = self.session.expand_placeholders(self.output_file)
```

You can call the expansion also explicitly using the `seppl.placeholders.expand_placeholders`
method:

```python
from  seppl.placeholders import expand_placeholders
...
s1 = expand_placeholders("{HOME}")
s2 = expand_placeholders("{CWD}/output/{INPUT_NAMEEXT}", current_input="/some/where/myfile.txt") 
```

It is possible to expand the built-in placeholders using two approaches:

* `seppl.placeholders.add_placeholder` method - adds a new the placeholder alongside its 
  description and lambda for generating a result from an optional input file.
  Useful for frameworks that make use of seppl.
  These placeholders will show in help screens and option lists.
* `seppl.placeholders.load_user_defined_placeholders` method - loads static placeholders
  from a text file (format: key=value). Useful for placeholders specific to 
  users/environments. These placeholders won't show up in help screens and option lists. 


### Tools

The following command-line tools are available:

* `seppl-escape`: for escaping unicode characters
* `seppl-unescape`: for unescaping unicode characters
