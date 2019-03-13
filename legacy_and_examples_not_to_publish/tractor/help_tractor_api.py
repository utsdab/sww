#!/usr/bin/env python2
"""
The maya renderers other than arnold
"""
# TODO either deprecate this properly of make it work.....

# ##############################################################
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)5.5s \t%(name)s \t%(message)s')
sh.setFormatter(formatter)
logger.addHandler(sh)
# ##############################################################

import os
import sys
import tractor.api.author as author

# help(author.Job)
print "author----------------"
print dir(author)

print "Job----------------"
print dir(author.Job)

print "Task----------------"
print dir(author.Task)
help (author.Task)

print "Command----------------"
print dir(author.Command)
help (author.Command)


print "Iterate----------------"
print dir(author.Iterate)

print "Instance----------------"
print dir(author.Instance)
