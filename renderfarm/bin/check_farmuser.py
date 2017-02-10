#!/usr/bin/env python
import os
from sww.renderfarm.dabtractor.factories import user_factory as uf

# ##############################################################
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)5.5s \t%(filename)s as %(name)s \t%(message)s')
sh.setFormatter(formatter)
logger.addHandler(sh)
# ##############################################################

try:
    a = uf.UTSuser()
    logger.info("Found user name >>>> %s" % (a.name))
    logger.info("Found user number >>>> %s" % (a.number))
except Exception,err:
    logger.critical("Error You are NOT Known >>>> %s" % (err))

## TODO  check there are userprefs

## TODO  check user prefs has a config setup

## TODO  check there is a user_work area

## TODO  check permissions are ok

## TODO  check in tractor crewlist


