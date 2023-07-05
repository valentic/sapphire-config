#!/usr/bin/env python3

##########################################################################
#
#   Example ConfigComponent usage
#
#   2023-06-23  Todd Valentic
#               Initial implementation
#
##########################################################################

import argparse
import functools
import logging

import sapphire_config as sapphire

logging.basicConfig(level=logging.INFO)

class MyComponent(sapphire.Component):
    
    def __init__(self, prefix, name, config, parent, **kw):
        super().__init__(prefix, name, config, parent, **kw) 

        setattr(self, 
            'get_components', 
            functools.partial(self.get_components, parent=self)
        )

class State(MyComponent):

    def __init__(self, name, config, parent, **kw):
        super().__init__('state', name, config, parent, **kw)

        self.label = self.get('label', name)

    def __repr__(self):
        return self.label

class Component(MyComponent):

    def __init__(self, name, config, parent, **kw):
        super().__init__('component', name, config, parent, **kw)

        self.parent = parent
        self.status = parent.status

        self.timeout = self.config.get_timedelta('timeout')
        self.output = self.config.get_path('output.path')
        self.input = self.config.get_path('input.path')
        self.names = self.config.get_list('names')
        self.rate = self.config.get_rate('rate')
        self.key1 = self.config.get('key1')

        self.states = self.config.get_components('states', factory=State)

        print(f"{self} timeout: {self.timeout}")
        print(f"{self} path.base: {self.config.get('path.base')}")
        print(f"{self} output.path: {self.output}")
        print(f"{self} path.input: {self.input}")
        print(f"{self} names: {self.names}")
        print(f"{self} rate: {self.rate}")
        print(f"{self} key1: {self.key1}")
        print(f"{self} states: {self.states}")

class Demo():

    def __init__(self, filename):
        self.config = sapphire.Parser()
        self.config.read(filename)

        #self.components = self.config['section'].get_components(
        #    'components', factory=Component, parent=self 
        #)

        self.components = self.get_components('components', Component)
        print(self.components)

    def get_components(self, prefix, factory):
        return self.config['section'].get_components(prefix, factory=factory, parent=self)

    def status(self, msg):
        print(msg)

    def run(self):

        for name, component in self.components.items():
            component.status(name)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Example component usage')

    parser.add_argument('filename')

    args = parser.parse_args()

    Demo(args.filename).run()

        

