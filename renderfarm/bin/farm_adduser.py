#!/usr/bin/env rmanpy

import os
from sww.renderfarm.dabtractor.factories import user_factory as uf
# ##############################################################
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)5.5s \t%(filename)s as %(name)s \t%(message)s')
sh.setFormatter(formatter)
logger.addHandler(sh)
# ##############################################################


usermap=uf.Map()
me = os.getenv("USER")

#looking up the map file
try:
    usermap.getuser(me)

except Exception, err:
    logger.warn("User {} is not in the map file.".format(me))
    logger.warn("Adding {} - check for a Tractor Farm Job.".format(me))
    u = uf.UtsUser()
    u.addtomap()
    u.validate()
    u.spool()
else:
    logger.info("You are a farm user: {} {} from year: {}".format(usermap.getuser(me),\
                                                                  usermap.getusername(me)))




