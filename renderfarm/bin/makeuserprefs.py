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
import renderfarm.dabtractor.factories.shotgun_factory as sgt
import renderfarm.dabtractor.factories.environment_factory as envfac

people=sgt.People()
tj=envfac.TractorJob()

class Base(object):
    def __init__(self):
        self.peoplelist=[]
        self.dabuserprefs = None
        try:
            self.dabuserprefs = tj.config.getenvordefault("DABUSERPREFS","env")
        except Exception, err:
            logger.critical("Cant find DABUSERPREFS or DABASSETS: {}".format(err))
            sys.exit(1)

class Prefs(Base):
    def __init__(self):
        super(Prefs, self).__init__()
        print "xxxx"
        pass



def main():
    """
    This funtion calls from shotgun all the valid tractor users and creates the
    user_prefs area required if it does not exit.
    It will also move those it finds to a deprecated space.
    It is meant to run as a farm job owned by pixar
    """
    peoplelist=[]
    try:
        dabuserprefs = tj.config.getenvordefault("environment","DABUSERPREFS")
        logger.info("Dab user prefs: {}".format(dabuserprefs))
    except Exception, err:
        logger.critical("Cant find DABUSERPREFS: {}".format(err))
        sys.exit(err)
    for person in people.people:
        peoplelist.append(person.get('login'))
        # logger.info("Person: {}".format(person))

    makedirectorytree(dabuserprefs,peoplelist)
    deprecatedirectory(dabuserprefs,peoplelist)


def makedirectorytree(rootpath,rootnames=[]):
    """Make the template directory tree"""

    for i, root in enumerate(rootnames):
        roottomake = os.path.join(rootpath, root)
        if not os.path.exists(roottomake):
            try:
                os.mkdir(roottomake)
            except Exception, err:
                logger.warn("Error making directories {}".format(err))
            else:
                logger.info("Someone is missing: Making directory {}".format(roottomake))
                setupconfig(roottomake)
        else:
            # may be a new config that is being rolled out.
            logger.info("Setting up config {}".format(roottomake))
            setupconfig(roottomake)

        #TODO  copy the CONFIG structure into place and make the necessary links
        #TODO  set and check the permissions on the tree.


def setupconfig(path):
    # dabassets = people.site.environ["DABASSETS"]
    template = people.config.getdefault("config", "template")
    dest = os.path.join(path,os.path.basename(template))
    # logger.info("{} {}".format(template,dest))

    if os.path.exists(path) and os.path.exists(template):
        try:
            shutil.copytree(template, dest, symlinks=True, ignore=None)
        except Exception, err:
            logger.warn("Cant copy config {}".format(err))
        else:
            logger.info("Copying {} to {}".format(template,dest))

        try:
            # TODO fix this so it is a relative path ../config
            linksrc = dest
            linkdest =  os.path.join(path,"config")
            os.symlink(linksrc, linkdest )
        except Exception, err:
            logger.warn("Cant make config link: {}".format(err))
        else:
            logger.info("Linking {} -> {}".format(linkdest, linksrc))


def deprecatedirectory(rootpath,rootnames=[]):
    """
    Move unknown directories to a .zapped folder
    :param rootpath:
    :param rootnames:
    :return: None
    """
    directoriestozap=diff(existingusers(rootpath),rootnames)
    if not len(directoriestozap) == 0:
        logger.info("Found these spurious directories: {}".format(directoriestozap))
    zapdir=os.path.join(rootpath,".zapped")
    userworkdir=os.path.join(rootpath)
    try:
        if not os.path.exists(zapdir):
            os.mkdir(zapdir)
        for i, each in enumerate(directoriestozap):
            logger.info("{} Moving {} to .zapped".format(i, each))
            os.rename(os.path.join(userworkdir,each),
                      os.path.join(zapdir,each))
    except Exception, err:
        logger.warn("Cant move bad alien directories")
        sys.exit(err)

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
    """
    :param rootpath:
    :return: cleaned list of existing users with directories.
    """
    cleaned=listdir_nodotfiles(rootpath)
    return cleaned


def diff(first, second):
    """
    :param first:  list
    :param second: list
    :return: list
    """
    second = set(second)
    differences= [item for item in first if item not in second]
    return differences

def setpermissionsontree(rootpath):
    pass


# ################################################################################################
if __name__ == '__main__':
    main()







