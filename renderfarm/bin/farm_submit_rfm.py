#!/usr/bin/env python2
'''
Main submission of a renderman for maya job to tractor.
'''

#TODO  ldap authentication is dissapearing
#TODO fix the scene navigation bug on the path expansion if you navigate away and back again in the UI
#TODO  add in a suffix for the naming of the job on the farm if desired
#TODO  add in integrator

import os
import sys
import logging
from renderfarm.dabtractor.factories import interface_rfm_factory as ui

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)5.5s \t%(name)s \t%(message)s')
sh.setFormatter(formatter)
logger.addHandler(sh)


def main():
    try:
        w=ui.Window()
    except Exception, err:
        logger.warn(err)
        sys.exit("Sorry you dont appear to be a registered farm user {}, contact "
                 "matt - "
                 "matthew.gidney@uts.edu.au".format(os.environ["USER"]))



if __name__ == '__main__':
    # print os.environ['PYTHONPATH']
    print "PLEASE LAUNCH RFM JOBS FROM MAYA USING THE DAB SHELF"
    #main()

