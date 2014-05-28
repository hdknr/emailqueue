# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from optparse import make_option
import sys
import inspect
import argparse

class SubCommand(object):
    name = ''
    description = ''
    args = []   # (tuple, dict)

    def __init__(self, *args, **kwargs):
        self.parser = argparse.ArgumentParser(
            prog=self.name, add_help=False,
            description=self.description.__unicode__())

        for a, k in self.args:
            self.parser.add_argument(*a, **k)

    def help(self):
        self.parser.print_help()

    def execute(self, *args, **options):
        params = self.parser.parse_args(args)
        self.run(params, **options)
        
    def run(self, params , **options):
        raise NotImplemented()


class GenericCommand(BaseCommand):
    args = ''
    help = ''
    model = None
    
    @classmethod
    def subcommands(cls):
        return dict(
            (v.name, v) for k, v in cls.__dict__.items()
            if inspect.isclass(v) and issubclass(v, SubCommand))
    
    @classmethod
    def subcommand(cls, name):
        return cls.subcommands().get(name, None)

    
    def run_from_argv(self, argv):
        ''' Django call this '''

        args = argv and argv[0] == 'manage.py' and argv[2:] or argv[1:0]

        if len(args) < 1:
            for k, v in self.subcommands().items():
                print "\n\n*** Subcommand:", k
                v().help()

        elif len(args) > 1 and args[0] == 'help':
            command = self.subcommand(args[1])
            command and command().help()
        else: 
            command = self.subcommand(args[0])
            command and command().execute(*args[1:])

    def open_file(self, options):
        fp = sys.stdin if options['file'] == 'stdin' else open(options['file'])
        return fp
