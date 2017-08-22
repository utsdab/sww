#!/usr/bin/env python
'''

'''

#TODO

from renderfarm.dabtractor.factories.command_factory import Bash

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)5.5s \t%(filename)s as %(name)s \t%(message)s')
sh.setFormatter(formatter)
logger.addHandler(sh)

logger.info(">>>>>>> The farm will run a job to cleanup the user_work area <<<<<<<<")

USERPREFS=Bash(projectgroup="admin",command="makeuserprefs.py")
USERPREFS.build()
USERPREFS.validate()

USERWORK=Bash(projectgroup="admin",command="makeworkareas.py")
USERWORK.build()
USERWORK.validate()

try:
    USERPREFS.spool()
except Exception, err:
    logger.warn("Spool Error {e}".format(e=err))

try:
    USERWORK.spool()
except Exception, err:
    logger.warn("Spool Error {e}".format(e=err))


