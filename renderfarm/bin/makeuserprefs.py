#!/usr/bin/python
'''
command to be run as a farm job by pixar user
'''

# ##############################################################
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)5.5s \t%(name)s \t%(message)s')
sh.setFormatter(formatter)
logger.addHandler(sh)
# ##############################################################
import os
import sys
import shutil
import renderfarm.dabtractor.shotgun_factory as sgt
import renderfarm.dabtractor.environment_factory as envfac

"""
    makeuserprefs.py is designed to be run as a farm job so as user pixar with
    credentials 8888:8888
    the $DABPREFS/user_prefs directory should be have these permissions
    drwxrwsr_t pixar pixar
    so that only pixar can removve entries and all subsequent folders 
    inherit the group permission mask
"""

try:
    people=sgt.People()
    tj=envfac.TractorJob()
except Exception, err:
    logging.critical("Cannot get anything from Shotgun, exiting")
    sys.exit(err)

class Base(object):
    def __init__(self):
        self.peoplelist=[]
        self.dabuserprefs = None
        try:
            self.dabuserprefs = tj.config.getenvordefault("DABUSERPREFS","env")
        except Exception, err:
            logger.critical("Cant find DABUSERPREFS or DABASSETS, exiting")
            sys.exit(err)

class Prefs(Base):
    def __init__(self):
        super(Prefs, self).__init__()
        logger.info("Prefs Class not imlemented yet")

def main():
    """
    This funtion calls from shotgun all the valid tractor users and creates the
    user_prefs area required if it does not exit.
    It will also move those it finds to a deprecated space.
    It is meant to run as a farm job owned by pixar
    """

    try:
        dabuserprefs = tj.config.getenvordefault("environment","DABUSERPREFS")
    except Exception, err:
        logger.critical("Cant find DABUSERPREFS in the environment default, exiting")
        sys.exit(err)

    peoplelist=[]
    for person in people.people:
        peoplelist.append(person.get('login'))
        # print person.get('login')

    try:
        makedirectorytree(dabuserprefs, peoplelist)
    except Exception, err:
        logger.critical("Cant run makedirectorytree, exiting")
        #sys.exit(err)

    try:
        deprecatedirectory(dabuserprefs,peoplelist)
    except Exception, err:
        logger.critical("Cant run deprecatedirectory, exiting")
        #sys.exit(err)

def makedirectorytree(rootpath,rootnames=[]):
    """  Make the template directory tree  """

    for i, root in enumerate(rootnames):
        roottomake = os.path.join(rootpath, root)

        ## new user
        if not os.path.exists(roottomake):
            try:
                logger.info("New User: {}".format(roottomake))
                os.mkdir(roottomake)
            except Exception, err:
                logger.warn("  Error making directories {}".format(err))
            else:
                logger.info("  Making directory {}".format(roottomake))
                setupconfig(roottomake)

        ## existing user
        else:
            try:
                logger.info("User found: Updating {}".format(roottomake))
                setupconfig(roottomake)
            except Exception, err:
                logger.warn("  Error updating {}".format(err))
            else:
                logger.info("  Done updating {}".format(roottomake))

        #TODO  set and check the permissions on the tree.


def setupconfig(path):
    """ dabassets = people.site.environ["DABASSETS"] """
    template = os.path.join(os.environ.get("DABSWW"),"renderfarm",people.config.getdefault("config", "template"))
    dest = os.path.join(path,os.path.basename(template))

    if os.path.exists(path) and os.path.exists(template):

        try:
            shutil.copytree(template, dest, symlinks=True, ignore=None)
        except Exception, err:
            logger.warn("     Cant copy config template {}".format(err))
        else:
            logger.info("  Copying {} to {}".format(template,dest))

        try:
            # TODO fix this so it is a relative path ../config
            linkdest =  os.path.join(path,"config")
            os.symlink(dest, linkdest )
        except Exception, err:
            logger.warn("     Cant make config link: {}".format(err))
        else:
            logger.info("  Linking {} -> {}".format(linkdest, dest))

    else:
        raise Exception("The template {} or path {} do not exist".format(template,path))



def deprecatedirectory(rootpath,rootnames=[]):
    """ Move unknown directories to a .zapped folder """

    directoriestozap = diff(existingusers(rootpath), rootnames)

    if not len(directoriestozap) == 0:
        logger.info("Found these spurious directories: {}".format(directoriestozap))
    zapdir = os.path.join(rootpath,".zapped")
    userworkdir = os.path.join(rootpath)

    try:
        if not os.path.exists(zapdir):
            os.mkdir(zapdir)
        for i, each in enumerate(directoriestozap):
            logger.info("{} Moving {} to .zapped".format(i, each))
            removed(os.path.join(zapdir, each))
            os.rename(os.path.join(userworkdir,each),
                      os.path.join(zapdir,each))
    except Exception, err:
        logger.warn("Cant move alien directories to .zapped directory, exiting")
        #sys.exit(err)

def removed(dir):
    try:
        shutil.rmtree(dir)   # ignore_errors=False)

    except Exception, err:
        logger.warn("Cant remove the directory in the .zapped directory, exiting, {}".format(err))
        #sys.exit(err)
    else:
        logger.info("Removed existing directory that was zapped before")

def listdir_nodotfiles(dir):
    # same as os.listdir but no dot files

    directoriespresent=os.listdir(dir)
    cleaned=[]

    for i,each in enumerate(directoriespresent):
        firstletter = each[:1]
        if  firstletter != ".":
            cleaned.append(each)

    return cleaned

def existingusers(rootpath):
    cleaned = listdir_nodotfiles(rootpath)
    return cleaned


def diff(first, second):
    second = set(second)
    differences= [item for item in first if item not in second]
    return differences

def setpermissionsontree(rootpath):
    pass


# ################################################################################################
if __name__ == '__main__':
    main()







