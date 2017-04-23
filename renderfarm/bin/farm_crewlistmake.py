#!/usr/bin/env python
import os
import stat
from renderfarm.dabtractor.factories import user_factory as uf
from renderfarm.dabtractor.factories import environment_factory as ef
from renderfarm.dabtractor.factories import utils_factory as utf
from renderfarm.dabtractor.factories import shotgun_factory as sgt

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


logger.info(">>>>>>> Checking if you are a Farm User <<<<<<<<")

# p=Person()
# logger.info("Shotgun Tractor User >>>> Login={number}   Name={name}  Email={email}".format(\
#     name=p.dabname,number=p.dabnumber,email=p.email))
# logger.info("-------------------------------FINISHED TESTING")


people=sgt.People()

file="/Volumes/dabrender/__tmp/new_crew.list.txt"

## TODO  check maya prefs has a config setup
try:
    if os.path.exists(os.path.dirname(file)):
        people.writetractorcrewfile(file)
    else:
        raise
except Exception, err:
    logger.critical("Error Writing File {}".format (file, err))
else:
    logger.info("Created temp crelist file to integrate : {}".format (file))








