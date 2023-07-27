"""Sapphire Unit Tests"""

# pylint: disable=missing-function-docstring

import configparser
import datetime
import os
import pathlib
import pytest

from dateutil.relativedelta import relativedelta

import sapphire_config as sapphire

class Factory(sapphire.Component):
    """Example Component class"""

    def __init__(self, *p, **kw):
        super().__init__('component', *p, **kw)

class FactorySet(sapphire.Component):
    """Test component set"""

    def __init__(self, *p, **kw):
        super().__init__("component", *p, **kw)

        self.config.set("setname", f"setname.{self.name}") 


def test_get_parser():
    config = sapphire.Parser()
    config['section'] = {}
    config['section']['option'] = 'value'

    result = config.get('section', 'option')
    assert result == 'value'

def test_get_proxy_dict():
    config = sapphire.Parser()
    config['section'] = {}
    config['section']['option'] = 'value'

    result = config['section']['option']
    assert result == 'value'

def test_get_missing_section():
    config = sapphire.Parser()

    with pytest.raises(configparser.NoSectionError):
        config.get('section','missing', fallback=sapphire.UNSET)

def test_get_missing_option():
    config = sapphire.Parser()
    config['section'] = {}

    with pytest.raises(configparser.NoOptionError):
        config.get('section','missing', fallback=sapphire.UNSET)

def test_get_proxy_func():
    config = sapphire.Parser()
    config['section'] = {}
    config['section']['option'] = 'value'

    result = config['section'].get('option')
    assert result == 'value'

def test_int():
    config = sapphire.Parser()
    config['section'] = {}
    config['section']['int'] = '1'

    result = config['section'].get_int('int')
    assert result == 1

def test_int_hex():
    config = sapphire.Parser()
    config['section'] = {}
    config['section']['int'] = '0x10'

    result = config['section'].get_int('int')
    assert result == 16

def test_int_base():
    config = sapphire.Parser()
    config['section'] = {}
    config['section']['int'] = '044'

    result = config['section'].get_int('int', base=8)
    assert result == 36

def test_int_fallback_none():
    config = sapphire.Parser()
    config['section'] = {}

    result = config['section'].get_int('missing')
    assert result is None

def test_int_fallback_str():
    config = sapphire.Parser()
    config['section'] = {}

    result = config['section'].get_int('missing', fallback='1')
    assert result == 1

def test_int_fallback_int():
    config = sapphire.Parser()
    config['section'] = {}

    result = config['section'].get_int('missing', fallback=1)
    assert result == 1

def test_boolean():
    config = sapphire.Parser()
    config['section'] = {}
    config['section']['boolean'] = 'true'

    result = config['section'].get_boolean('boolean')
    assert result is True

def test_boolean_fallback_none():
    config = sapphire.Parser()
    config['section'] = {}

    result = config['section'].get_boolean('missing')
    assert result is None

def test_boolean_fallback_str():
    config = sapphire.Parser()
    config['section'] = {}

    result = config['section'].get_boolean('missing', fallback='true')
    assert result is True

def test_boolean_fallback_bool_t():
    config = sapphire.Parser()
    config['section'] = {}

    result = config['section'].get_boolean('missing', fallback=True)
    assert result is True

def test_boolean_fallback_bool_f():
    config = sapphire.Parser()
    config['section'] = {}

    result = config['section'].get_boolean('missing', fallback=False)
    assert result is False

def test_boolean_fallback_int_t():
    config = sapphire.Parser()
    config['section'] = {}

    result = config['section'].get_boolean('missing', fallback=1)
    assert result is True

def test_boolean_fallback_int_f():
    config = sapphire.Parser()
    config['section'] = {}

    result = config['section'].get_boolean('missing', fallback=0)
    assert result is False

def test_get_list_parser():
    config = sapphire.Parser()
    config['section'] = {}
    config['section']['list'] = 'a b c'

    result = config.get_list('section', 'list')
    assert result == ['a', 'b', 'c']

def test_get_list_proxy_func():
    config = sapphire.Parser()
    config['section'] = {}
    config['section']['list'] = 'a b c'

    result = config['section'].get_list('list')
    assert result == ['a', 'b', 'c']

def test_get_list_conv_parser():
    config = sapphire.Parser()
    config['section'] = {}
    config['section']['list'] = '1 2 3'

    result = config.get_list('section', 'list', conv=int)
    assert result == [1, 2, 3]

def test_get_list_conv_proxy():
    config = sapphire.Parser()
    config['section'] = {}
    config['section']['list'] = '1 2 3'

    result = config['section'].get_list('list', conv=int)
    assert result == [1, 2, 3]

def test_get_list_sep():
    config = sapphire.Parser()
    config['section'] = {}
    config['section']['list'] = '1, 2, 3'

    result = config['section'].get_list('list', sep=',')
    assert result == ['1', '2', '3']

def test_get_list_sep_conv():
    config = sapphire.Parser()
    config['section'] = {}
    config['section']['list'] = '1, 2, 3'

    result = config['section'].get_list('list', sep=',', conv=int)
    assert result == [1, 2, 3]

def test_get_list_fallback_none():
    config = sapphire.Parser()
    config['section'] = {}
    config['section']['list'] = '1, 2, 3'

    result = config['section'].get_list('missing')
    assert result == []

def test_get_list_fallback_str():
    config = sapphire.Parser()
    config['section'] = {}

    result = config['section'].get_list('missing', fallback='a b c')
    assert result == ['a', 'b', 'c']

def test_get_list_no_section():
    config = sapphire.Parser()

    with pytest.raises(KeyError):
        config['section'].get_list('missing')

def test_get_list_fallback_type_error():
    config = sapphire.Parser()
    config['section'] = {}

    with pytest.raises(AttributeError):
        config['section'].get_list('missing', fallback=1)

def test_get_list_fallback_empty_str():
    config = sapphire.Parser()
    config['section'] = {}

    result = config['section'].get_list('missing', fallback='')
    assert result == []

def test_get_list_fallback_list():
    config = sapphire.Parser()
    config['section'] = {}

    result = config['section'].get_list('missing', fallback=[1, 2, 3])
    assert result == [1, 2, 3]

def test_get_set_parser():
    config = sapphire.Parser()
    config['section'] = {}
    config['section']['set'] = 'a b c c'

    result = config.get_set('section', 'set')
    assert result == {'a', 'b', 'c'}

def test_get_set_proxy():
    config = sapphire.Parser()
    config['section'] = {}
    config['section']['set'] = 'a b c c'

    result = config['section'].get_set('set')
    assert result == {'a', 'b', 'c'}

def test_get_set_conv_parser():
    config = sapphire.Parser()
    config['section'] = {}
    config['section']['set'] = '1 2 3'

    result = config.get_set('section', 'set', conv=int)
    assert result == {1, 2, 3}

def test_get_set_sep():
    config = sapphire.Parser()
    config['section'] = {}
    config['section']['set'] = '1, 2, 3'

    result = config['section'].get_set('set', sep=',')
    assert result == {'1', '2', '3'}

def test_get_bytes():
    config = sapphire.Parser()
    config['section'] = {}
    config['section']['bytes'] = '100 MiB'

    result = config['section'].get_bytes('bytes')
    assert result == 104857600

def test_get_datetime():
    config = sapphire.Parser()
    config['section'] = {}
    config['section']['datetime'] = '2023-06-01'

    result = config['section'].get_datetime('datetime')
    assert result == datetime.datetime(2023,6,1)

def test_get_datetime_fallback_none():
    config = sapphire.Parser()
    config['section'] = {}

    result = config['section'].get_datetime('missing')
    assert result is None

def test_get_datetime_fallback_str():
    config = sapphire.Parser()
    config['section'] = {}

    result = config['section'].get_datetime('missing', fallback='2023-06-01')
    assert result == datetime.datetime(2023,6,1)

def test_get_datetime_fallback_datetime():
    config = sapphire.Parser()
    config['section'] = {}

    dt = datetime.datetime(2023,6,1)
    result = config['section'].get_datetime('missing', fallback=dt)
    assert result == datetime.datetime(2023,6,1)

def test_get_timedelta():
    config = sapphire.Parser()
    config['section'] = {}
    config['section']['timedelta'] = '10s'

    result = config['section'].get_timedelta('timedelta')
    assert result == datetime.timedelta(seconds=10)

def test_get_timedelta_fallback_none():
    config = sapphire.Parser()
    config['section'] = {}

    result = config['section'].get_timedelta('missing')
    assert result is None

def test_get_timedelta_fallback_str():
    config = sapphire.Parser()
    config['section'] = {}

    result = config['section'].get_timedelta('missing', fallback='10s')
    assert result == datetime.timedelta(seconds=10)

def test_get_timedelta_fallback_int():
    config = sapphire.Parser()
    config['section'] = {}

    result = config['section'].get_timedelta('missing', fallback=10)
    assert result == datetime.timedelta(seconds=10)

def test_get_timeselta_fallback_td():
    config = sapphire.Parser()
    config['section'] = {}

    td = datetime.timedelta(seconds=10)
    result = config['section'].get_path('missing', fallback=td)
    assert result == td

def test_get_path():
    config = sapphire.Parser()
    config['section'] = {}
    config['section']['path'] = '/home/test'

    result = config['section'].get_path('path')
    assert result == pathlib.Path('/home/test')

def test_get_path_fallback_none():
    config = sapphire.Parser()
    config['section'] = {}

    result = config['section'].get_path('missing')
    assert result is None

def test_get_path_fallback_str():
    config = sapphire.Parser()
    config['section'] = {}

    result = config['section'].get_path('missing', fallback='/home/test')
    assert result == pathlib.Path('/home/test')

def test_get_path_fallback_path():
    config = sapphire.Parser()
    config['section'] = {}

    pt = pathlib.Path('/home/test')
    result = config['section'].get_path('missing', fallback=pt)
    assert result == pt

def test_get_rate():
    config = sapphire.Parser()
    config['section'] = {}
    config['section']['rate'] = '60'

    period = datetime.timedelta(seconds=60)
    rate = sapphire.Rate(period)

    result = config['section'].get_rate('rate')
    assert result == rate

def test_get_rate_all():
    config = sapphire.Parser()
    config['section'] = {}
    config['section']['rate.period'] = '60'
    config['section']['rate.sync'] = 'true'
    config['section']['rate.offset'] = '10s'
    config['section']['rate.at_start'] = 'true'

    period = datetime.timedelta(seconds=60)
    offset = datetime.timedelta(seconds=10)
    rate = sapphire.Rate(period, sync=True, offset=offset, at_start=True)

    result = config['section'].get_rate('rate')
    assert result == rate

def test_get_rate_fallback_none():
    config = sapphire.Parser()
    config['section'] = {}

    #result = config['section'].get_rate('missing')
    result = config.get_rate('section', 'missing')
    assert result is None

def test_get_rate_fallback_str():
    config = sapphire.Parser()
    config['section'] = {}

    period = datetime.timedelta(seconds=60)
    rate = sapphire.Rate(period)

    result = config['section'].get_rate('missing', fallback='60s')
    assert result == rate

def test_get_rate_fallback_int():
    config = sapphire.Parser()
    config['section'] = {}

    period = datetime.timedelta(seconds=60)
    rate = sapphire.Rate(period)

    result = config['section'].get_rate('missing', fallback=60)
    assert result == rate

def test_get_rate_fallback_rate():
    config = sapphire.Parser()
    config['section'] = {}

    period = datetime.timedelta(seconds=60)
    rate = sapphire.Rate(period)

    result = config['section'].get_rate('missing', fallback=rate)
    assert result == rate

def test_rate_init_default():
    rate = sapphire.Rate(0)

    assert isinstance(rate.period, datetime.timedelta) 
    assert isinstance(rate.offset, datetime.timedelta)
    assert rate.period.total_seconds() == 0
    assert rate.offset.total_seconds() == 0
    assert rate.sync == False
    assert rate.at_start == False

def test_rate_init_timedelta():
    period = datetime.timedelta(0)
    offset = datetime.timedelta(0)
    rate = sapphire.Rate(period, offset)

    assert isinstance(rate.period, datetime.timedelta) 
    assert isinstance(rate.offset, datetime.timedelta)
    assert rate.period.total_seconds() == 0
    assert rate.offset.total_seconds() == 0

def test_rate_nexttime():
    rate = sapphire.Rate(60, sync=False)

    curtime = datetime.datetime(2001, 1, 1, 0, 0, 5)

    wait = rate.nexttime(curtime)
    assert wait.total_seconds() == 60 

def test_rate_nexttime_sync():
    rate = sapphire.Rate(60, sync=True)

    curtime = datetime.datetime(2001, 1, 1, 0, 0, 5)

    wait = rate.nexttime(curtime)
    assert wait.total_seconds() == 55 

def test_rate_nexttime_offset():
    rate = sapphire.Rate(60, offset=10)

    curtime = datetime.datetime(2001, 1, 1, 0, 0, 5)

    wait = rate.nexttime(curtime)
    assert wait.total_seconds() == 60 

def test_rate_nexttime_offset_sync():
    rate = sapphire.Rate(60, offset=10, sync=True)

    curtime = datetime.datetime(2001, 1, 1, 0, 0, 5)

    wait = rate.nexttime(curtime)
    assert wait.total_seconds() == 5 

def test_rate_nexttime_offset_sync2():
    rate = sapphire.Rate(60, offset=10, sync=True)

    curtime = datetime.datetime(2001, 1, 1, 0, 0, 15)

    wait = rate.nexttime(curtime)
    assert wait.total_seconds() == 55

def test_get_components():
    config = sapphire.Parser()
    config['section'] = {}
    config['section']['components'] = 'a b'

    result = config.get_components('section', 'components', factory=Factory)
    assert isinstance(result, dict)

def test_get_components_proxy():
    config = sapphire.Parser()
    config['section'] = {}
    config['section']['components'] = 'a b'

    result = config['section'].get_components('components', factory=Factory)
    assert isinstance(result, dict)

def test_component_set():
    config = sapphire.Parser()
    config['section'] = {}
    config['section']['components'] = 'a b'

    result = config.get_components('section', 'components', factory=FactorySet)
    assert result['a'].config.get('setname') == "setname.a" 

def test_component_options():
    config = sapphire.Parser()
    config['section'] = {}
    config['section']['components'] = 'a'

    c = config.get_components('section', 'components', factory=FactorySet)
    options = c['a'].config.options()

    assert options == ['name', 'component', 'setname', 'components'] 

def test_get_callback():
    config = sapphire.Parser()
    config['section'] = {}
    config['section']['callback.module'] = 'os'
    config['section']['callback.function'] = 'cpu_count'
    config['section']['callback.init'] = 'cpu_count'

    result = config['section'].get_callback('callback')
    assert result is os.cpu_count

def test_get_interpolation():
    config = sapphire.Parser()
    config['section'] = {}
    config['section']['base.name'] = 'a'
    config['section']['opt'] = 'name'
    config['section']['path'] = r'%(base.%(opt)s)s'

    result = config.get('section', 'path')
    assert result == 'a'

def test_get_interpolation_proxy():
    config = sapphire.Parser()
    config['section'] = {}
    config['section']['base.name'] = 'a'
    config['section']['opt'] = 'name'
    config['section']['path'] = r'%(base.%(opt)s)s'

    result = config['section']['path']
    assert result == 'a'

def test_get_interpolation_loop():
    config = sapphire.Parser()
    config['section'] = {}
    config['section']['base.name'] = r'%(path)'
    config['section']['opt'] = 'name'
    config['section']['path'] = r'%(base.%(opt)s)s'

    with pytest.raises(configparser.InterpolationDepthError):
        _result = config['section']['path']

def test_component_mixin():
    config = sapphire.Parser()
    config['section'] = {}
    config['section']['base.mixin.key1'] = 'base key1'
    config['section']['components'] = 'a b'
    config['section']['component.a.mixin'] = 'base.mixin'
    config['section']['component.a.key1'] = 'a key1'

    components = config['section'].get_components('components', factory=Factory)
    result = components['a'].config.get('key1')
    assert result == 'a key1'

def test_component_mixin_default():
    config = sapphire.Parser()
    config['section'] = {}
    config['section']['base.mixin.key1'] = 'base key1'
    config['section']['components'] = 'a b'
    config['section']['component.a.mixin'] = 'base.mixin'

    components = config['section'].get_components('components', factory=Factory)
    result = components['a'].config.get('key1')
    assert result == 'base key1'

def test_timespan_int():
    config = sapphire.Parser()
    config['section'] = {}
    config['section']['timespan'] = '10'

    rd = relativedelta(seconds=10)
    result = config['section'].get_timespan('timespan')
    assert result == rd

def test_timespan_td():
    config = sapphire.Parser()
    config['section'] = {}
    config['section']['timespan'] = '10s'

    rd = relativedelta(seconds=10)
    result = config['section'].get_timespan('timespan')
    assert result == rd

def test_timespan_rd():
    config = sapphire.Parser()
    config['section'] = {}
    config['section']['timespan'] = 'days=1, seconds=10'

    rd = relativedelta(days=1, seconds=10)
    result = config['section'].get_timespan('timespan')
    assert result == rd

def test_escape():
    config = sapphire.Parser()
    config['section'] = {}
    config['section']['value'] = '%%Y'

    result = config['section'].get('value')
    assert result == '%Y' 

