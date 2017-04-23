#!/usr/bin/python

"""
    This code handles the creation of a user area.
    At UTS the $USER is a number and there is no nice name exposed at all.
    However we can query this from the ldap database using ldapsearch.
    Thus we can define the concept of renderusername and renderusernumber
    this just need to be in the path some place  dabanim/usr/utils
"""
import os
import json
from pprint import pprint
from renderfarm.dabtractor.factories import shotgun_factory as sgt
from renderfarm.dabtractor.factories import configuration_factory as config

import renderfarm as rf
import tractor.api.author as author
import tractor.api.query as tq

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


class TractorJob(object):
    """ A class with the basic farm job info """
    def __init__(self):
        # super(TractorJob, self).__init__()
        self.author=author
        self.tq=tq
        self.config=config.JsonConfig()
        try:
            __utsuser=sgt.Person()
        except Exception, err:
            logger.warn("Cant get person from Shotgun %s" % err)
        else:
            self.username=__utsuser.dabname
            self.usernumber=__utsuser.dabnumber
            self.useremail=__utsuser.email
            self.department= __utsuser.department

        self.hostname = str(self.config.getdefault("tractor","engine"))
        self.port= int(self.config.getdefault("tractor","port"))
        self.jobowner=str(self.config.getdefault("tractor","jobowner"))
        self.engine=str(self.config.getdefault("tractor","engine"))
        self.dabwork=self.config.getenvordefault("DABWORK","config")
        self.author.setEngineClientParam( hostname=self.hostname, port=self.port, user=self.jobowner, debug=True)
        self.tq.setEngineClientParam( hostname=self.hostname, port=self.port, user=self.jobowner, debug=True)


class Environment(object):
    """This class adds to the environment is os.environ it replaces Environment Class
    1. read the environment that needs to be there in the config json file ie (has a "fj" attribute
    2. if not found then add it to the environment os.environ """

    def __init__(self):
        # super(Environment, self).__init__()
        self.config=config.JsonConfig()
        self.requiredenvars = self.config.getallenvgroups()
        for envar in self.requiredenvars:
            try:
                e=os.environ[envar]
            except:
                logger.warn("Environment variable {} NOT FOUND".format(envar))
                _value=self.getdefault(envar,"config")
                os.environ[envar]=_value
                logger.info("Setting {} to {} from config.json file".format(envar,_value))
            else:
                logger.info("{} = {}".format(envar,e))

        self.environ=os.environ
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

    sh.setLevel(logging.INFO)

    logger.debug("\n-------- ENVIRONMENT ------------")
    _E2=Environment()
    # logger.debug( _E2.requiredenvars)
    pprint(_E2.environ)


    logger.debug("\n-------- TRACTOR JOB ------------")
    _TJ=TractorJob()
    pprint(_TJ.__dict__)



