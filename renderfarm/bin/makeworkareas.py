#!/usr/bin/python

# ##############################################################
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)5.5s \t%(name)s \t%(message)s')
sh.setFormatter(formatter)
logger.addHandler(sh)
# ##############################################################
import os
import sys
import sww.renderfarm.dabtractor.factories.shotgun_factory as sgt

def main():
    """
    This funtion calls from shotgun all the valid tractor users and creates the
    user_work area required if it does not exit.
    It will also move those it finds to a deprecated space.
    It is meant to run as a farm job owned by pixar

    :return:
    """
    people=sgt.People()
    peoplelist=[]
    try:
        dabwork = people.env.environ["DABWORK"]
    except Exception, err:
        logger.critical("Cant find DABWORK: {}".format(err))
        sys.exit(1)

    for person in people.people:
        peoplelist.append(sgt.People.cleanname(person.get('email')))

    makedirectorytree(dabwork,peoplelist)
    deprecatedirectory(dabwork,peoplelist)

def makedirectorytree(rootpath,rootnames=[]):
    """Make the template directory tree"""
    try:
        for i, root in enumerate(rootnames):
            roottomake=os.path.join(rootpath,"user_work",root)
            if not os.path.exists(roottomake):
                logger.info("Someone missing: Making directory {}".format(roottomake))
                os.mkdir(roottomake)

            if os.environ["DABDEV"] == "development" and i>1:
                sys.exit("development cap")

    except Exception, err:
        logger.warn("Error making directories {}".format(err))
    else:
        #TODO  copy the CONFIG structure into place and make the necessary links
        pass
    finally:
        #TODO  set and check the permissions on the tree.
        pass

def deprecatedirectory(rootpath,rootnames=[]):
    """
    Move unknown directories to a .zapped folder
    :param rootpath:
    :param rootnames:
    :return: None
    """
    directoriestozap=diff(existingusers(rootpath),rootnames)
    logger.info("Found these spurious directories: {}".format(directoriestozap))
    zapdir=os.path.join(rootpath,"user_work",".zapped")
    userworkdir=os.path.join(rootpath,"user_work")
    try:
        if not os.path.exists(zapdir):
            os.mkdir(zapdir)
        for i, each in enumerate(directoriestozap):
            logger.info("{} Moving {} to .zapped".format(i, each))
            os.rename(os.path.join(userworkdir,each),
                      os.path.join(zapdir,each))
    except Exception, err:
        logger.warn("Cant move bad alien directories")
        sys.exit(1)

def existingusers(rootpath):
    """
    :param rootpath:
    :return: cleaned list of existing users with directories.
    """
    cleaned=listdir_nodotfiles(os.path.join(rootpath,"user_work"))
    return cleaned

def listdir_nodotfiles(dir):
    # same as os.listdir but no dot files
    directoriespresent=os.listdir(dir)
    cleaned=[]
    for i,each in enumerate(directoriespresent):
        firstletter = each[:1]
        if  firstletter != ".":
            cleaned.append(each)
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
    """ drwxrws--- 2 root terminator  6 28 mai   11:15 test
        chgrp terminator test

        chmod 770 test
        chmod g+s
    """
    os.chmod('pixar', 0o2770)
    os.chmod('pixar', 5327)  #2755 decimal  www.rapidtables.com/convert/number/decimal-to-octal.htm

    # import os
    # os.chmod('test', 02770)


# #################################################################################################
if __name__ == '__main__':
    main()
else:
    main()






