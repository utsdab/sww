#!/usr/bin/python

"""
    This code handles the creation of a user area.
    At UTS the $USER is a number and there is no nice name exposed at all.
    However we can query this from the ldap database using ldapsearch.
    Thus we can define the concept of renderusername and renderusernumber
    this just need to be in the path some place  dabanim/usr/bin
"""
import os
import json
import inspect
import utils_factory as utils
import user_factory as ufac
import sww.renderfarm.dabtractor as dt
import sww.renderfarm as rf
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

class ConfigBase(object):
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
        """
        """

        self.configjson = os.path.join(os.path.dirname(rf.__file__), "etc","dabtractor_config.json")
        _file=open(self.configjson)
        self.groups = {}
        # self.config = None
        try:
            self.config=json.load(_file)
        except Exception, err:
            logger.warn("Problem reading json file {}".format(err))
        else:
            _groups=self.config.keys()
            _groups.sort()
            for i, group in enumerate(_groups):
                # print i,group
                _attribute=self.config.get(group)
                if type(_attribute)==type({}):  # has children who are dicts
                    # print _attribute
                    self.groups[group]=_attribute
        finally:
            print self.groups
            _file.close()

    def getoptions(self, group, key):
        """
        Assumes the value of the attribute is a list
        :param group:
        :param key:
        :return:
        """
        _return = None
        try:
            _type = type(self.groups.get(group).get(key))
        except Exception, err:
            logger.warn("Options - Group <%s> or Attribute <%s> not in config.json file, %s" % (group,key,err))
            logger.debug("ALL DEFAULTS = %s" % self.getalldefaults())
        else:
            if _type==type([]):
                _return = self.groups.get(group).get(key)
            else:
                logger.warn("Attribute %s has no options, %s" % (key, err))
        finally:
            return _return

    def getdefault(self, group, key):
        """
        Returns the first index if a list or just the vale if not a list
        :param group:
        :param key:
        :return:
        """

        _return = None
        try:
            _type = type(self.groups.get(group).get(key))
        except Exception, err:
            logger.warn("Default - Group <%s> or Attribute <%s> not in config.json file, %s" % (group, key, err))
            logger.debug("ALL DEFAULTS = %s" % self.getalldefaults())
        else:
            if _type==type([]):
                _return = self.groups.get(group).get(key)[0]
            elif _type==type(u''):
                _return = self.groups.get(group).get(key)
            else:
                logger.warn("%s not a list or a string" % key)
        finally:
            return str(_return)

    def getgroups(self):
        """
        Returns all attribute groups
        :return:
        """

        _return = None
        try:
            _return = self.groups.keys()
        except Exception, err:
            logger.warn("Groups not defined, %s" % (err))
        finally:
            return str(_return)

    def getattributes(self,group):
        """
        Return a groups attributes
        :param group:
        :return:
        """

        _return = None
        try:
            _return =  self.groups.get(group).keys()
        except Exception, err:
            logger.warn("Group %s not in config.json file, %s" % (group,err))
            logger.debug("ALL DEFAULTS = %s" % self.getalldefaults())
        finally:
            return _return


    def getalldefaults(self):
        """
        Returns a dict with key (group,attribute) and value is the default
        :return:
        """

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
        """
        Any group with a "path" attribute should be and environment variable declaration os.environ
        return a list of groups with "path" declared
        warn if the value is not valid
        :return:
        """

        _haspath = []
        for group in self.groups.keys():
            for attribute in self.groups.get(group).keys():
                if attribute=="farmjob":
                    _haspath.append(group)
        return _haspath


class FarmJob(ConfigBase):
    """
    A class with the basic farm job info
    """
    def __init__(self):
        """

        """
        super(FarmJob, self).__init__()
        self.author=author
        self.tq=tq
        __utsuser=ufac.FarmUser()
        self.username=__utsuser.name
        self.usernumber=__utsuser.number
        self.hostname = str(self.getdefault("tractor","engine"))
        self.port= int(self.getdefault("tractor","port"))
        self.jobowner=str(self.getdefault("tractor","jobowner"))
        self.engine=str(self.getdefault("tractor","engine"))

        self.author.setEngineClientParam( hostname=self.hostname, port=self.port, user=self.jobowner, debug=True)
        self.tq.setEngineClientParam( hostname=self.hostname, port=self.port, user=self.jobowner, debug=True)



class Environment(ConfigBase):
    """
    This class is the project structure base
    $DABRENDER/$TYPE/$SHOW/$PROJECT/$SCENE
    $SCENE is possible scenes/mayascene.ma - always relative to the project
    presently $TASK and $SHOT not used
    move this all to a json file template

    This probaly needs to be changed as the idea of a project might be buried
    within the show more deeply as per the way shotgun_repos would have it.
    So $PROJECT is possibly  .../dir1/dir2/dir3/....../project
    project is a maya project and should therefor have a workspace.mel file.


    this class is to be obsoleted!!!!!!
    only used in the UI widget, and the methods should move there.

    """

    def __init__(self):
        super(Environment, self).__init__()
        self.type = None
        self.show =  None
        self.project =  None
        self.scene =  None

    def setfromscenefile(self, scenefilefullpath):
        """
        Try and set the structure from the scene file path.
        :param scenefilefullpath:
        :return:
        """
        try:
            os.path.isfile(scenefilefullpath)
        except Exception, err:
            logger.warn("Cant set from file.{} {}".format(scenefilefullpath, err))
        else:
            _dirname=os.path.dirname(scenefilefullpath)
            _basename=os.path.basename(scenefilefullpath)
            _dirbits=os.path.normpath(_dirname).split("/")
            _fullpath=os.path.normpath(scenefilefullpath).split("/")
            for i, bit in enumerate(_dirbits):
                if bit == "project_work" or bit == "user_work":
                    logger.debug("")
                    self.dabwork="/".join(_dirbits[0:i])
                    logger.info("DABWORK: {}".format(self.dabwork))
                    self.type=bit
                    logger.info("TYPE: {}".format(self.type))
                    self.show=_dirbits[i+1]
                    logger.info("SHOW: {}".format( self.show))
                    self.project=_dirbits[i+2]
                    logger.info("PROJECT: {}".format( self.project))
                    self.scene="/".join(_fullpath[i+3:])
                    logger.info("SCENE: {}".format( self.scene))


    def setfromprojroot(self, dirfullpath):
        """
        Try and set from the directory full path
        :param dirfullpath:
        :return:
        """

        try:
            os.path.isdir(dirfullpath)
        except Exception, err:
            logger.warn("Cant set from dir: {} {}".format( dirfullpath,err))
        else:
            _dirname=os.path.dirname(dirfullpath)
            _basename=os.path.basename(dirfullpath)
            _dirbits=os.path.normpath(_dirname).split("/")
            _fullpath=os.path.normpath(dirfullpath).split("/")
            for i, bit in enumerate(_dirbits):
                if bit == "project_work" or bit == "user_work":
                    logger.info("")
                    self.dabwork="/".join(_dirbits[0:i])
                    logger.info("DABWORK: {}".format(self.dabwork))
                    self.type=bit
                    logger.info("TYPE: {}".format(self.type))
                    self.show=_dirbits[i+1]
                    logger.info("SHOW: {}".format( self.show))
                    self.project="/".join(_dirbits[i+1:])
                    logger.info("PROJECT: {}".format( self.project))


    def putback(self):
        """
        Put values back to the environment
        :return:
        """

        try:
            os.environ["DABWORK"] = self.dabwork
            os.environ["TYPE"] = self.type
            os.environ["SHOW"] = self.show
            os.environ["PROJECT"] = self.project
            os.environ["SCENE"] = self.scene
        except Exception,err:
            logger.warn("Putback failed %s"%err)
        else:
            logger.info("Putback main environment variables")


class Environment2(ConfigBase):
    """
    This class adds to the environment is oe.environ it replaces Environment Class

    1. read the environment that needs to be there in the config json file ie (has a "farmjob" attribute
    2. if not founf then add it to the environment os.environ

    """
    def __init__(self):
        """

        """
        super(Environment2, self).__init__()
        self.requiredenvars = self.getallenvgroups()

        for envar in self.requiredenvars:
            try:
                e=os.environ[envar]
            except:
                logger.warn("Environment variable {} NOT FOUND".format(envar))
                _value=self.getdefault(envar,"env")
                os.environ[envar]=_value
                logger.info("Setting {} to {} from config.json file".format(envar,_value))
            else:
                logger.info("{} = {}".format(envar,e))

        self.environ=os.environ
        logger.debug(self.environ.items())

    def setnewenv(self,key,value):
        """
        Declare a new variable and put back to os.environ.
        :param key:
        :param value:
        :return:
        """

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
    logger.debug("-------- PROJECT FACTORY TEST ------------")

    E2=Environment2()
    print E2.requiredenvars
    print E2.environ.keys()

    CB=ConfigBase()
    print CB.getallenvgroups()
    print CB.getalldefaults()

    FJ=FarmJob()
    print FJ.getalldefaults()



    # JJ = Environment()
    #
    #
    # logger.debug("GROUPS = %s"% JJ.getgroups())
    # group = "maya"
    # attribute = "versions"
    #
    # logger.debug( "ATTRIBUTES = %s"% JJ.getattributes(group))
    # logger.debug( "ATTRIBUTE VALUES =  %s"%  JJ.getoptions(group,attribute))
    # logger.debug( "DEFAULT VALUE =  %s"% JJ.getdefault(group,attribute))
    #
    # group = "nuke"
    # attribute = "versions"
    # logger.debug( "ATTRIBUTES =  %s"%  JJ.getattributes(group))
    # logger.debug( "ATTRIBUTE VALUES =  %s"%  JJ.getoptions(group,attribute))
    # logger.debug( "DEFAULT VALUE =  %s"% JJ.getdefault(group,attribute))
    #
    # group = "renderman"
    # attribute = "versions"
    # logger.debug( "ATTRIBUTES =  %s"%  JJ.getattributes(group))
    # logger.debug( "ATTRIBUTE VALUES =  %s"%  JJ.getoptions(group,attribute))
    # logger.debug( "DEFAULT VALUE =  %s"% JJ.getdefault(group,attribute))
    #
