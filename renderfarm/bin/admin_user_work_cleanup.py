#!/usr/bin/env python
from renderfarm.dabtractor.factories import command_factory as comfac

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

logger.info(">>>>>>> The farm will run a job to cleanup the user_work area <<<<<<<<")

USERPREFS=comfac.Bash(projectgroup="admin",command="makeuserprefs.py")
USERPREFS.build()
USERPREFS.validate()

USERWORK=comfac.Bash(projectgroup="admin",command="makeworkareas.py")
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


