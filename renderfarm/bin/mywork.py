#!/usr/bin/python

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

import argparse
import os
import sys

from sww.renderfarm.dabtractor.factories import shotgun_factory as sgt

def getuserwork():
    try:
        p=sgt.Person()

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
