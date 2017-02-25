#!/usr/bin/env python
from sww.renderfarm.dabtractor.factories import adhoc_jobs_factory as ah

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

JOB=ah.SimpleCommand()
JOB.build()
JOB.validate()
JOB.spool()


