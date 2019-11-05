#!/usr/bin/python
'''
returns your to your user prefs area
'''

import os
import sys
from renderfarm.dabtractor.factories.shotgun_factory import Person
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)5.5s \t%(name)s \t%(message)s')
sh.setFormatter(formatter)
logger.addHandler(sh)


def getuserwork():
    try:
        p=Person()

    except Exception,err:
        logger.critical("Cant talk to shotgun properly {}".format(err))
    else:
        if os.path.exists(p.user_work):
            return p.user_work
        else:
            sys.exit(1)


# #####################################################################################################
if __name__ == '__main__':
    print getuserwork()
