#!/usr/bin/python
'''
    This code holds the configurations for various  custom things
    Basically these are kept in a single configuration file in JSON format
    Holding studio specific defaults and choices for various interfaces and software.
'''

import os
import json
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)5.5s \t%(filename)s as %(name)s \t%(message)s')
sh.setFormatter(formatter)
logger.addHandler(sh)


'''
import yaml
tractor seems to not have yaml in its rmanpy framework
so need to use generic python? and call tractor?

tractor.api.author is a Python API for building Tractor jobs.

This module is installed with the Python interpreter that ships with Tractor, rmanpy. It may be used with other Python interpreters, but will require site-specific configuration to locate or install the required Tractor Python modules.
The following examples assume that the query module has been imported as follows:

>>> import tractor.api.author as author

'''
import renderfarm as rf
from pprint import pprint


# class YamlConfig(object):
#     '''
#     load the site yaml file
#     '''
#     def __init__(selfself):
#         self.configyaml = os.path.join(os.path.dirname(rf.__file__), "etc","dabtractor_config.yml")

class JsonConfig(object):
    """
    This class gathers up the configuration settings from an external json file.
    Function return configurations.
    The schema is simple - a two level dictionary:

    { group : {
        attribute : value
        attribute : [ default, value1, value2 ]  ### default value is index 0
        }
    }
    """
    def __init__(self):
        self.configjson = os.path.join(os.path.dirname(rf.__file__), "etc","dabtractor_config.json")
        _file=open(self.configjson)
        self.groups = {}
        self.config = None
        try:
            self.config=json.load(_file)
        except Exception, err:
            logger.warn("Problem reading json file %s"%err)
        else:
            _groups=self.config.keys()
            _groups.sort()
            for i, group in enumerate(_groups):
                _attribute=self.config.get(group)
                if type(_attribute)==type({}):  # has children who are dicts
                    self.groups[group]=_attribute
        finally:
            _file.close()

    def getoptions(self, group, attribute):
        """ Assumes the value of the attribute is a list """
        _return = None
        err=None
        try:
            _type = type(self.groups.get(group).get(attribute))
        except Exception, err:
            logger.warn("Options - Group <%s> or Attribute <%s> not in site.json file, %s" % (group, attribute, err))
            logger.debug("ALL DEFAULTS = %s" % self.getalldefaults())
        else:
            if _type==type([]):
                _return = self.groups.get(group).get(attribute)
            else:
                logger.warn("Attribute %s has no options, %s" % (attribute, err))
        finally:
            return _return

    def getdefault(self, group, attribute):
        """ Returns the first index if a list or just the vale if not a list """
        _return = None
        try:
            _type = type(self.groups.get(group).get(attribute))
        except Exception, err:
            logger.warn("Default - Group <%s> or Attribute <%s> not in site.json file, %s" % (group, attribute, err))
            logger.debug("ALL DEFAULTS = %s" % self.getalldefaults())
        else:
            if _type==type([]):
                _return = self.groups.get(group).get(attribute)[0]
            elif _type==type(u''):
                _return = self.groups.get(group).get(attribute)
            else:
                logger.warn("%s not a list or a string" % attribute)
        finally:
            return str(_return)

    def getenvordefault(self, group, attribute):
        """ Returns the envar OR first index if a list or just the value if not a list """
        _return = None
        if attribute == "environment":
            try:
                _return = os.environ[attribute]
            except Exception,err:
                logger.debug("Cant get envar {} {}".format(group,err))
            else:
                return str(_return)
        else:
            try:
                _type = type(self.groups.get(group).get(attribute))
            except Exception, err:
                logger.warn("Default - Group <%s> or Attribute <%s> not in site.json file, %s" % (group, attribute, err))
                logger.debug("ALL DEFAULTS = %s" % self.getalldefaults())
            else:
                if _type==type([]):
                    _return = self.groups.get(group).get(attribute)[0]
                elif _type==type(u''):
                    _return = self.groups.get(group).get(attribute)
                else:
                    logger.warn("%s not a list or a string" % attribute)
            finally:
                return str(_return)

    def getgroups(self):
        """ Returns all attribute groups """
        _return = None
        try:
            _return = self.groups.keys()
        except Exception, err:
            logger.warn("Groups not defined, %s" % (err))
        finally:
            return str(_return)

    def getattributes(self, group):
        """ Return a groups attributes """
        _return = None
        try:
            _return = self.groups.get(group).keys()
        except Exception, err:
            logger.warn("Group %s not in dabtractor_config.json file, %s" % (group,err))
            logger.debug("ALL DEFAULTS = %s" % self.getalldefaults())
        finally:
            return _return

    def getalldefaults(self):
        """ Returns a dict with key (group,attribute) and value is the default """
        _defaults = {}
        for group in self.groups.keys():
            for attribute in self.groups.get(group).keys():
                if type(self.groups.get(group).get(attribute))==type([]):
                    default = self.groups.get(group).get(attribute)[0]
                elif type(self.groups.get(group).get(attribute))== type(u'xx'):
                    default = self.groups.get(group).get(attribute)
                else:
                    logger.warn("%s not a list or a string" % attribute)
                    logger.warn( type(self.groups.get(group).get(attribute)))
                    default = None
                _defaults[(group,attribute)]=default
        return _defaults

    def getallenvgroups(self):
        """ Any group with a "path" attribute should be and environment variable declaration os.environ
        return a list of groups with "path" declared
        warn if the value is not valid """
        _haspath = []
        for group in self.groups.keys():
            for attribute in self.groups.get(group).keys():
                if attribute=="fj":
                    _haspath.append(group)
        return _haspath

class Output(object):
    def __init__(self):
        #  various output templates held in an output object
        self.resolution=(1280,720,1.0) # width height apxel aspect
        # "HD720p","HD540p", "HD1080p","DCPflat","DCPscope","Omni10k","Omni5k", "FROMFILE"
        self.resolutions={
                          "HD540p" :(960,540,1.0),     # 1.778
                          "HD720p" :(1280,720,1.0),    # 1.778
                          "HD1080p":(1920,1080,1.0),   # 1.778
                          "DCPscope":(2048,858,1.0),   # 2.39  DCP
                          "DCPflat" :(1998,1080,1.0),  # 1.85  DCP
                          "Omni4k" :(4096,4096,1.0),   # 1.0   Data Arena Omnidirectional stereo top bottom
                          "Omni10k":(10000,10000,1.0)  # 1.0   Data Arena Omnidirectional stereo top bottom
                          }





if __name__ == '__main__':

    sh.setLevel(logging.DEBUG)

    logger.debug("\n-------- JSON Config ------------")

    siteconfig=JsonConfig()
    # logger.debug( _E2.requiredenvars)
    pprint(siteconfig.getalldefaults())
    pprint(siteconfig.getenvordefault("environment","DABSWW"))
    pprint(siteconfig.getenvordefault("class","worktype"))
    pprint(siteconfig.getattributes("class"))
    pprint(siteconfig.getoptions("class","worktype"))
    #
    # mayaversion= siteconfig.getdefault("maya","version")
    # rendermanversion= siteconfig.getdefault("renderman","version")
    # rmanver="renderman-{}".format(rendermanversion,mayaversion)
    # rfmver="renderman-{}-maya-{}".format(rendermanversion,mayaversion)
    # print rmanver
    # print rfmver

    out=Output()
    o = out.resolutions.keys()
    for each in o:
        try:
            print each,out.resolutions.get(each)[0],out.resolutions.get(each)[1],out.resolutions.get(each)[2]
        except:
            print


