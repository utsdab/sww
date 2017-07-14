#!/usr/bin/python
'''
    This code holds the configurations for various  custom things
    Basically these are kept in a single configuration file in JSON format
    Holding studio specific defaults and choices for various interfaces and software.
'''

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

import os
import json
from sww import renderfarm as rf

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
        if attribute == "site":
            try:
                _return = os.environ[group]
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

    def getattributes(self,group):
        """ Return a groups attributes """
        _return = None
        try:
            _return = self.groups.get(group).keys()
        except Exception, err:
            logger.warn("Group %s not in site.json file, %s" % (group,err))
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
