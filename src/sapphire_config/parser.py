#!/usr/bin/env python
"""Sapphire Config Parser"""

##########################################################################
#
#   Configuration parser from the Data Transport Network project.
#
#   Adds a number of converters and ConfigComponent support.
#
#   2020-12-24  Todd Valentic
#               Initial implementation
#
#   2023-06-17  Todd Valentic
#               PEP8 compliance
#
#   2023-07-17  Todd Valentic
#               Change Rate offset default to 0 from None
#
#   2023-07-24  Todd Valentic
#               Add Rate.nexttime()
#
##########################################################################

import configparser as cp
import datetime
import importlib
import pathlib
import re

from typing import Union

from dateutil.relativedelta import relativedelta
import dateutil.parser
import humanfriendly
import pytimeparse2 as pytimeparse

# -------------------------------------------------------------------------
#   Types
# -------------------------------------------------------------------------

# pylint: disable=protected-access

UNSET = cp._UNSET


class Rate:
    """Repeating event specification"""

    def __init__(
        self,
        period: Union[int, float, datetime.timedelta],
        sync: bool = False,
        offset: Union[int, float, datetime.timedelta] = 0,
        at_start: bool = False,
    ):
        if isinstance(period, (float, int)):
            period = datetime.timedelta(seconds=period)

        if isinstance(offset, (float, int)):
            offset = datetime.timedelta(seconds=offset)

        self.period = period
        self.sync = sync
        self.offset = offset
        self.at_start = at_start

    def __repr__(self):
        return (
            f"<Rate "
            f"period={self.period}, "
            f"sync={self.sync}, "
            f"offset={self.offset}, "
            f"at_start={self.at_start}"
            f">"
        )

    def __eq__(self, other):
        return (
            self.period == other.period
            and self.sync == other.sync
            and self.offset == other.offset
            and self.at_start == other.at_start
        )

    def nexttime(self, curtime: datetime.datetime):
        """Seconds until next deadline""" 

        period = self.period.total_seconds()

        if self.sync:
            timestamp = (curtime - self.offset).timestamp() 
            wait = period - timestamp % period
        else:
            wait = period

        return datetime.timedelta(seconds = wait)
        
# -------------------------------------------------------------------------
#   Converters
# -------------------------------------------------------------------------


def as_datetime(value):
    """Convert to datetime"""

    return dateutil.parser.parse(value)


def as_timedelta(value):
    """Convert to timedelta"""

    if isinstance(value, datetime.timedelta) or value is None:
        return value
    if isinstance(value, (int, float)):
        return datetime.timedelta(seconds=value)
    return datetime.timedelta(seconds=pytimeparse.parse(value))


def as_list(value, sep=None, conv=str):
    """Convert to list"""

    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [conv(x.strip()) for x in value.split(sep)]


def as_set(value, sep=None, conv=str):
    """Convert to set"""

    if isinstance(value, set):
        return value
    if value is None:
        return set()
    return {conv(x.strip()) for x in value.split(sep)}


def as_bytes(value):
    """Convert to bytes"""

    return humanfriendly.parse_size(str(value))


def as_path(value):
    """Convert to path"""
    return pathlib.Path(value)


def as_boolean(value):
    """Convert to boolean"""

    value = str(value).lower()
    if value not in cp.RawConfigParser.BOOLEAN_STATES:
        raise ValueError(f"Not a boolean: {value}")
    return cp.RawConfigParser.BOOLEAN_STATES[value]


def as_timespan(value):
    """Convert to relativetime"""

    args = {}

    if "=" in value:
        for arg in value.split(","):
            k, v = arg.split("=")
            args[k.strip()] = int(v)

    else:
        td = as_timedelta(value)
        args["seconds"] = td.total_seconds()

    return relativedelta(**args)


Converters = {
    "_bytes": as_bytes,
    "_datetime": as_datetime,
    "_path": as_path,
    "_timespan": as_timespan,
}


# -------------------------------------------------------------------------
#   Interpolation - allow for nested values
# -------------------------------------------------------------------------


class NestedInterpolation(cp.Interpolation):
    """Extends the standard BasicInterpolation.

    For example:

        something: %(part.%(number)s)s

    would first resolve %(number)s and then %(part...)s. If number=4,
    then %(part.4)s.
    """

    _KEYCRE = re.compile(r"%\((?:[^()]+)\)s")

    def before_get(self, parser, section, option, value, defaults):
        rawval = value
        depth = cp.MAX_INTERPOLATION_DEPTH

        while depth:
            depth -= 1
            keys = self._KEYCRE.findall(value)

            if not keys:
                break

            for key in keys:
                k = parser.optionxform(key[2:-2])
                try:
                    v = defaults[k]
                except KeyError:
                    raise cp.InterpolationMissingOptionError(
                        option, section, rawval, key
                    ) from None
                value = value.replace(key, v)

        if "%(" in value:
            raise cp.InterpolationDepthError(option, section, rawval)

        value = value.replace("%%", "%")

        return value


# -------------------------------------------------------------------------
#   Sapphire Config Parser
# -------------------------------------------------------------------------


class Parser(cp.ConfigParser):
    """Sapphire Extensions for ConfigParser"""

    def __init__(self, *pos, **kw):
        kw["interpolation"] = NestedInterpolation()
        kw["converters"] = Converters
        super().__init__(*pos, **kw)

    def get(self, *pos, fallback=None, **kw):
        """Make default fallback None instead of UNSET"""
        return super().get(*pos, fallback=fallback, **kw)

    def _get(self, section, conv, option, **kw):
        value = self.get(section, option, **kw)
        return value if value is None else conv(value)

    # pylint: disable=redefined-builtin

    def _get_conv(
        self, section, option, conv, *, raw=False, vars=None, fallback=None, **kw
    ):
        try:
            return self._get(
                section, conv, option, fallback=UNSET, raw=raw, vars=vars, **kw
            )
        except (cp.NoSectionError, cp.NoOptionError):
            if fallback is UNSET:
                raise
            if fallback is None:
                return fallback
            if isinstance(fallback, str):
                return conv(fallback)
            return fallback

    def get_int(self, *pos, base=0, **kw):
        """Get an int"""

        value = self.get(*pos, **kw)
        if value is None:
            return None
        return int(str(value), base=base)

    def get_float(self, *pos, **kw):
        """Get a float"""

        return self.getfloat(*pos, **kw)

    def get_boolean(self, *pos, **kw):
        """Get a boolean"""

        value = self.get(*pos, **kw)
        if value is None:
            return None
        return as_boolean(str(value))

    def get_list(self, *pos, sep=None, conv=str, **kw):
        """Get a list"""

        return as_list(self.get(*pos, **kw), sep=sep, conv=conv)

    def get_set(self, *pos, sep=None, conv=str, **kw):
        """Get a set"""

        return as_set(self.get(*pos, **kw), sep=sep, conv=conv)

    def get_timedelta(self, *pos, **kw):
        """Get a timedelta"""

        return as_timedelta(self.get(*pos, **kw))

    def get_rate(self, section, option, fallback=None, **kw):
        """Get a rate"""

        if isinstance(fallback, Rate):
            period = fallback.period
            sync = fallback.sync
            offset = fallback.offset
            at_start = fallback.at_start
        else:
            period = fallback
            sync = False
            offset = 0
            at_start = False

        proxy = self[section]
        period = proxy.get_timedelta(option, fallback=period, **kw)
        period = proxy.get_timedelta(f"{option}.period", fallback=period, **kw)

        if period is None:
            return None

        sync = proxy.get_boolean(f"{option}.sync", fallback=sync, **kw)
        offset = proxy.get_timedelta(f"{option}.offset", fallback=offset, **kw)
        at_start = proxy.get_boolean(f"{option}.at_start", fallback=at_start, **kw)

        return Rate(period, sync, offset, at_start)

    def get_components(
        self, section, option, factory=None, parent=None, opts=None, **kw
    ):
        """Parse components"""

        if opts is None:
            opts = {}

        components = {}

        for name in self.get_list(section, option, **kw):
            components[name] = factory(name, self[section], parent, **opts)

        return components

    def get_callback(self, section, option, fallback=None, **kw):
        """Parse callback"""

        try:
            modname = self.get(section, f"{option}.module", fallback=UNSET, **kw)
        except (cp.NoSectionError, cp.NoOptionError):
            if fallback is UNSET:
                raise
            return fallback

        try:
            funcname = self.get(section, f"{option}.function", fallback=UNSET, **kw)
        except (cp.NoSectionError, cp.NoOptionError):
            if fallback is UNSET:
                raise
            return fallback

        initname = self.get(section, f"{option}.init", fallback=None, **kw)

        module = importlib.import_module(modname)
        callback = getattr(module, funcname)

        if initname:
            getattr(module, initname)()

        return callback
