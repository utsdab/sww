#!/usr/bin/env rmanpy
'''
Main submission of a nuke job to tractor.
'''

import os
import sys
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)5.5s \t%(name)s \t%(message)s')
sh.setFormatter(formatter)
logger.addHandler(sh)



def main():
    from renderfarm.dabtractor.factories import interface_nuke_factory as ui
    try:
        w = ui.Window()
    except Exception, err:
        logger.warn(err)
        sys.exit("Sorry you dont appear to be a registered farm user {}, try running farm_adduser.py and then contact "
                 "matt - "
                 "matthew.gidney@uts.edu.au".format(os.environ["USER"]))


if __name__ == '__main__':
    main()
