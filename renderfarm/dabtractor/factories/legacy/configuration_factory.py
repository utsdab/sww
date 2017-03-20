#!/usr/bin/python

"""
    This code holds the configurations for various things
"""
import os
import sys


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

import sww.renderfarm.dabtractor as dabtractor
import sww.renderfarm.dabtractor.factories.environment_factory as envfac
import os

class ConfigurationBase(object):
    """Base configurations - these are the possible options installed"""
    def __init__(self):
        self.mayaversions = ("2017",)
        self.rendermanversions = ("21.3","21.2",)
        self.rendermanrenderers = ("rms-ris", "rms-reyes")
        self.rendermanintegrators = ("pxr", "vcm")
        self.nukeversions = ("10.0v5","10.5v2")
        self.configuration = "base"
        self.projectgroups = ("yr1", "yr2", "yr3", "yr4", "admin")
        self.mayarenderers = ["mr", "sw"]
        self.mayarenderers = ("mr",)
        self.renderfarmbin = os.path.join(os.path.dirname(os.path.dirname(dabtractor.__file__)), "bin")
        self.renderfarmmodulepath = os.path.dirname(os.path.dirname(dabtractor.__file__))
        self.renderfarmproxypath = os.path.join(os.path.dirname(dabtractor.__file__), "proxys")
        self.nukedefaultproxytemplate = ("nuke_proxy_720p_prores_v003.py",)
        self.dabrenderpath = ("/Volumes/dabrender")

class CurrentConfiguration(ConfigurationBase):
    def __init__(self):
        super(CurrentConfiguration, self).__init__()
        self.configuration = "current"
        self.mayaversion = self.mayaversions[0]
        self.rendermanversion = self.rendermanversions[0]
        self.rendermanrenderer = self.rendermanrenderers[0]
        self.rendermanintegrator = self.rendermanintegrators[0]
        self.nukeversion = self.nukeversions[0]
        self.mayarenderer = self.mayarenderers[0]
        self.projectgroup = self.projectgroups[0]


if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)
    AA=CurrentConfiguration()
    print "**** TESTING ****"
    print "latest maya is %s" % AA.mayaversion
    print "latest nuke is %s" % AA.nukeversion
    print "latest renderman is %s" % AA.rendermanversion
    print "latest projects is %s" % AA.projectgroup
    print "renderfarmbin is %s" % AA.renderfarmbin
    print "proxypath is %s" % AA.renderfarmproxypath
