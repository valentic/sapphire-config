#!/usr/bin/env python3
"""Sapphire Config Component"""

##########################################################################
#
#   ConfigComponent
#
#   A base class for configuration components. A component is a group of
#   configuration items within a section of a config file that represent
#   the values for an object. For example, we might be watching a set of
#   mount points for disk usage. In this case, we need to specify the
#   information for each watch object. The config file would look like:
#
#     watches:  datapath spoolpath
#
#     watch.datapath.path:      /mnt/data
#     watch.datapath.label:     Data files
#
#     watch.spoolpath.path:     /mnt/spool
#     watch.spoolpath.label:    Spool files
#
#   The ConfigComponents are datapath and spoolpath. Each component has
#   the following format:
#
#       prefix.name.key: value
#
#   There is also a 'default' section, indicated by '*':
#
#       prefix.*.key: value
#
#   Mixins
#
#       Common configuration values can be extracted out and "mixed in"
#       to the component. This technique can be used to simplify
#       configuration files by greatly reducing the amount of repeated
#       values. Mixins can call other mixins, allowing for a heirarchy
#       of values to be established. When a value is requested, a lookup
#       stack of prefixes is followed until the value is found. This lookup
#       stack is composed of the mixins and default values.
#
#       For example, if we have:
#
#           base1.mixin.key1:   base1-value1
#           base1.mixin.key2:   base1-value2
#
#           base2.mixin.mixin:  base1.mixin
#           base2.mixin.key1:   base2-value1
#
#           base3.mixin.key1:   base3-value1
#           base3.mixin.key2:   base3-value2
#           base3.mixin.key3:   base3-value3
#
#           components: component1 component2
#
#           component.*.mixin:  base2.mixin base3.mixin
#           component.component1.key1:  component1-value1
#
#       The lookup stack for component1 is:
#
#           ['', 'component.*.', 'component.default.', 'base3.mixin.',
#            'base1.mixin.', 'base2.mixin.', 'component.component1.']
#
#       Keys are looked up by starting at the end of the list, adding
#           the item as a prefix to the key name. Looking up the keys
#           wound find:
#
#           key1 -> component.component1.key1
#           key2 -> base1.mixin.key2
#           key3 -> base3.mixin.key3
#
#       By convention, I like to use '.mixin' as the suffix for the
#           mixin groupings, but that isn't a requirement. They can
#           have any name that you want.
#
#   2023-06-26  Todd Valentic
#               Initial implementation.
#                   Complete rewrite with a new approach. Create a new
#                   configparser filled in with entries specific for the
#                   component. Allows for the reuse of features without
#                   any new machinery.
#
#   2023-7-25   Todd Valentic
#               Add set() and options() to config
#               Remove get() mapping, use config
#
##########################################################################

from functools import partial

from .parser import Parser

# pylint: disable=too-few-public-methods, unused-argument

class Component:
    """A component proxy from parent config"""

    def __init__(self, prefix, name, conf, parent, **kw):
        self.config = self._create_proxy(prefix, name, conf)
        self.parent = parent
        self.prefix = prefix
        self.name = name

    def _create_proxy(self, prefix, name, parent):
        section = f"{prefix}.{name}"

        config = Parser()

        config.add_section(section)
        proxy = config[section]

        # Add non-component values to default section

        for key in parent:
            if not key.startswith(f"{prefix}."):
                value = parent.get(key, raw=True)
                config.set("DEFAULT", key, value)

        # Add component default options to section

        proxy.update(self._get_values(parent, f"{prefix}.*."))
        proxy.update(self._get_values(parent, f"{prefix}.default."))

        # Add component mixins

        mixins = parent.get_list(f"{prefix}.*.mixin")
        mixins = parent.get_list(f"{prefix}.default.mixin", mixins)
        mixins = parent.get_list(f"{prefix}.{name}.mixin", mixins)

        for mixin in mixins:
            proxy.update(self._get_values(parent, f"{mixin}."))

        # Add component default options to section

        proxy.update(self._get_values(parent, f"{prefix}.{name}."))

        # Add component meta options to section

        proxy["name"] = name
        proxy[prefix] = name

        proxy.set = partial(proxy.parser.set, proxy.name)
        proxy.options = partial(proxy.parser.options, proxy.name) 

        return proxy

    def _get_values(self, parent, prefix):
        result = {}

        for key in parent:
            if key.startswith(prefix):
                newkey = key.replace(prefix, "")
                value = parent.get(key, raw=True)
                result[newkey] = value

        return result

    def __repr__(self):
        return f"{self.prefix}.{self.name}"
