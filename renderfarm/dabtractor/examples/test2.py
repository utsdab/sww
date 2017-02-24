#!/usr/bin/env rmanpy



import os

print os.environ["PATH"]
print os.environ["PYTHONPATH"]

import tractor.api.author as aut

print dir(aut)
# print os.environ
