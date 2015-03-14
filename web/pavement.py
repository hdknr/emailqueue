# -*- coding: utf-8 -*-
from paver.easy import (
    task, cmdopts, sh, consume_args
)
from djado.paves import runserver, do
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
