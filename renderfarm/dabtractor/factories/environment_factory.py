#!/usr/bin/env python2
'''
    This code handles the creation of a user area.
    At UTS the $USER is a number and there is no nice name exposed at all.
    However we can query this from the ldap database using ldapsearch.
    Thus we can define the concept of renderusername and renderusernumber
    this just need to be in the path some place  dabanim/usr/utils
'''
#TODO work out how much overlap there is between all these similar configuration factories
#TODO configuration, environment,shotgun,user and utils.


import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)5.5s \t%(filename)s as %(name)s \t%(message)s')
sh.setFormatter(formatter)
logger.addHandler(sh)

import os
from pprint import pprint
try:
    from shotgun_factory import Person
except ImportError, err:
    logger.critical("Cant import Person object from shotgun api")
try:
    from shotgun_factory import Project
except ImportError, err:
    logger.critical("Cant import Project object from shotgun api")

from site_factory import JsonConfig
import tractor.api.author as author
import tractor.api.query as tq

class TractorJob(object):
    """ A class with the basic farm job info """
    def __init__(self):
        self.author = author
        self.tq = tq
        self.config = JsonConfig()
        self.shotgunOwner = None
        self.shotgunOwnerId = None

        try:
            self.sgtperson = Person()
        except Exception, err:
            logger.warn("Cant get actual person from Shotgun {}, assuming dev".format(err))
            self.sgtperson = None
            self.devmode()
        else:
            self.username = self.sgtperson.dabname
            self.usernumber = self.sgtperson.dabnumber
            self.useremail = self.sgtperson.email
            self.department = self.sgtperson.department
            self.shotgunOwner = self.sgtperson.shotgunlogin
            self.shotgunOwnerId = self.sgtperson.shotgun_id

        try:
            self.sgtproject=Project()
        except Exception, err:
            logger.warn("Cant get project from Shotgun %s" % err)
        else:
            pass

        self.hostname = str(self.config.getdefault("tractor","engine"))
        self.port = int(self.config.getdefault("tractor","port"))
        self.jobowner = str(self.config.getdefault("tractor","jobowner"))
        self.engine = str(self.config.getdefault("tractor","engine"))
        self.dabwork = self.config.getenvordefault("environment","DABWORK")
        self.author.setEngineClientParam( hostname=self.hostname, port=self.port, user=self.jobowner, debug=True)
        self.tq.setEngineClientParam( hostname=self.hostname, port=self.port, user=self.jobowner, debug=True)
        self.jobtitle = None
        self.jobenvkey = None
        self.jobfile = None
        self.jobstartframe = None
        self.jobendframe = None
        self.jobchunks = None
        self.jobbyframe = None
        self.jobthreads = None
        self.jobthreadmemory = None
        self.envtype = None
        self.envshow = None
        self.envproject = None
        self.envscene = None
        self.mayaversion = None
        self.rendermanversion = None
        self.houdiniversion = None
        self.shotgunProject = None
        self.shotgunProjectId = None
        self.shotgunClass = None
        self.shotgunShotAsset = None
        self.shotgunShotAssetId = None
        self.shotgunSeqAssetType = None
        self.shotgunSeqAssetTypeId = None
        self.shotgunTask = None
        self.shotgunTaskId = None
        self.sendToShotgun = False
        self.farmpriority = None
        self.farmcrew = None
        self.farmtier=None
        self.optionskipframe = None
        self.optionmakeproxy = None
        self.optionsendemail = None
        self.optionresolution = None
        self.optionmaxsamples = None

    def devmode(self):
        self.username="matthewgidney"
        self.usernumber="120988"
        self.useremail="matthew.gidney@uts.edu.au"
        self.department= "staff"

class Environment(object):
    """This class adds to the environment is os.environ it replaces Environment Class
    1. read the environment that needs to be there in the site json file ie (has a "fj" attribute
    2. if not found then add it to the environment os.environ """

    def __init__(self):
        self.config=JsonConfig()
        self.requiredenvars = self.config.getallenvgroups()
        for envar in self.requiredenvars:
            try:
                e=os.environ[envar]
            except:
                logger.warn("Environment variable {} NOT FOUND".format(envar))
                _value=self.getdefault(envar,"site")
                os.environ[envar]=_value
                logger.info("Setting {} to {} from site.json file".format(envar,_value))
            else:
                logger.info("{} = {}".format(envar,e))

        self.environ = os.environ
        logger.debug(self.environ.items())

    def setnewenv(self,key,value):
        """ Declare a new variable and put back to os.environ. """
        if not os.environ.has_key(key):
            try:
                os.environ[key]=value
            except Exception, err:
                logger.warn("Cant set environment variable {} to {}".format(key,value))
            else:
                logger.info("Environment variable {} = {}".format(key,value))
            finally:
                self.environ=os.environ
        else:
            logger.warn("Environment variable {} already set".format(key))


if __name__ == '__main__':

    sh.setLevel(logging.DEBUG)

    logger.debug("\n-------- ENVIRONMENT ------------")
    _E2=Environment()
    # logger.debug( _E2.requiredenvars)
    for k in _E2.requiredenvars:
        logger.debug("KEY {key} : {value}".format(key=k[0],value=k[:0]))


    logger.debug("\n-------- TRACTOR JOB ------------")
    # _TJ=TractorJob()
    # pprint(_TJ.__dict__)



