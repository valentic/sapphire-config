#!/usr/bin/env python

import sys
from datetime import datetime, timedelta
import pathlib
import configparser as cp

import sapphire_config as sapphire
#from sapphire_config import SapphireConfigParser, Rate

if __name__ == '__main__':

    filenames = sys.argv[1:]

    config = sapphire.Parser()

    config.read(filenames)

    for section in config.sections():
        print(section)
        for option in config.options(section):
            rawvalue = config.get(section, option, raw=True)
            value = config.get(section, option)
            print(f'  [R] {option}: {rawvalue}')
            print(f'  [I] {option}: {value}')
            print()

    print('Test list: [ProcessGroup] clients')
    print('  %s' % config.get_list('archive','list'))
    print('  %s' % config.get_list('archive','list.int', type=int))
    print('  %s' % config.get_list('archive','list.comma', sep=','))
    print('  %s' % config.get_list('archive','missing'))
    try:
        print('  %s' % config.get_list('archive','missing', fallback=cp._UNSET))
    except cp.NoOptionError:
        print('handled missing option OK') 
    print('  %s' % config.get_list('archive','missing', fallback=''))
    print('  %s' % config.get_list('archive','missing', fallback=[]))

    print('Test set:')
    print('  %s' % config.get_set('archive','set'))
    print('  %s' % config.get_set('archive','set.int', type=int))
    print('  %s' % config.get_set('archive','set.comma', sep=','))

    print('Test bytes:')
    print(' %s' % config.get_bytes('archive','bytes'))
    print(' %s' % config.get_bytes('archive','missing'))

    print('Test datetime:')
    print(' %s' % config.get_datetime('archive','datetime'))
    print(' %s' % config.get_datetime('archive','missing'))
    print(' %s' % config.get_datetime('archive','missing', fallback='2023-02-01'))
    print(' %s' % config.get_datetime('archive','missing', fallback=datetime.now()))

    print('Test timedelta:')
    print(' %s' % config.get_timedelta('archive','timedelta'))
    print(' %s' % config.get_timedelta('archive','missing'))
    print(' %s' % config.get_timedelta('archive','missing', fallback='60'))
    print(' %s' % config.get_timedelta('archive','missing', fallback='60s'))
    print(' %s' % config.get_timedelta('archive','missing', fallback=60))
    print(' %s' % config.get_timedelta('archive','missing', fallback=timedelta(seconds=10)))

    print('Test path:')
    print(' %s' % config.get_path('archive','path'))
    print(' %s' % config.get_path('archive','missing'))
    print(' %s' % config.get_path('archive','missing', fallback='/tmp'))
    print(' %s' % config.get_path('archive','missing', fallback=pathlib.Path('/tmp')))

    print('Test int:')
    print(' %s' % config.get_int('archive','int'))
    print(' %s' % config.get_int('archive','int.hex', base=16))
    print(' %s' % config.get_int('archive','missing'))
    print(' %s' % config.get_int('archive','missing', fallback='100'))
    print(' %s' % config.get_int('archive','missing', fallback=100))

    print('Test boolean:')
    print(' %s' % config.get_boolean('archive','boolean'))
    print(' %s' % config.get_boolean('archive','boolean.lower'))
    print(' %s' % config.get_boolean('archive','boolean.int'))
    print(' %s' % config.get_boolean('archive','boolean.off'))
    print(' %s' % config.get_boolean('archive','missing'))
    print(' %s' % config.get_boolean('archive','missing', fallback='false'))
    print(' %s' % config.get_boolean('archive','missing', fallback=False))

    print('Test rate:')
    rate = sapphire.Rate(20)
    print(' %s' % config.get_rate('archive','rate'))
    print(' %s' % config.get_rate('archive','missing'))
    print(' %s' % config.get_rate('archive','missing', fallback=60))
    print(' %s' % config.get_rate('archive','missing', fallback='100s'))
    print(' %s' % config.get_rate('archive','missing', fallback=rate))
    
    print('Test components:')
    class Factory:
        def __init__(self, name, config, parent, **kw):
            self.name = name
            self.parent = parent
            self.opts = kw
    print(' %s' % config.get_components('archive', 'components', Factory))
    print(' %s' % config.get_components('archive', 'missing', Factory))

    print('Test callback:')
    callback = config.get_callback('archive', 'callback')
    print(callback, callback())

    print('Proxy tests:')
    print("  ['archive']['boolean']: %s" % config['archive']['boolean'])
    print("  ['archive'].get('boolean'): %s" % config['archive'].get('boolean'))
    archive = config['archive']
    print("  archive['boolean']: %s" % archive['boolean'])
    print("  archive.get('boolean'): %s" % archive.get('boolean'))

    print('Timespan:')
    print('  td : %s' % config['archive'].get_timespan('timespan.td'))
    print('  int: %s' % config['archive'].get_timespan('timespan.int'))
    print('  rd : %s' % config['archive'].get_timespan('timespan.rd'))
