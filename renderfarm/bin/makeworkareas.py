#!/usr/bin/python
'''
command to be run as a farm job by pixar user
'''

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
import pwd
import grp
import shutil
import renderfarm.dabtractor.factories.shotgun_factory as sgt
import renderfarm.dabtractor.factories.environment_factory as envfac

tj=envfac.TractorJob()
people=sgt.People()

def main():
    """
    This funtion calls from shotgun all the valid tractor users and creates the
    user_work area required if it does not exit.
    It will also move those it finds to a deprecated space.
    It is meant to run as a farm job owned by pixar
    """
    # people=sgt.People()
    peoplelist=[]
    try:
        dabwork = people.config.getenvordefault("environment","DABWORK")
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
                logger.warn("Someone missing: Making directory {}".format(roottomake))
                os.mkdir(roottomake)
            else:
                logger.info("All Good for  {}".format(roottomake))
            setpermissionsontree(roottomake)

    except Exception, err:
        logger.warn("Error making directories {}".format(err))
    else:
        pass
    finally:
        #TODO  set and check the permissions on the tree.
        pass

def deprecatedirectory(rootpath,rootnames=[]):
    """
    Move unknown directories to a .zapped folder
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
            removed(os.path.join(zapdir, each))
            os.rename(os.path.join(userworkdir,each),
                      os.path.join(zapdir,each))
    except Exception, err:
        logger.warn("Cant move alien directories, exiting")
        #sys.exit(err)

def removed(dir):
    try:
        shutil.rmtree(dir)   # ignore_errors=False)
    except Exception, err:
        logger.warn("Cant remove the directory in the .zapped directory, exiting")
        #sys.exit(err)
    else:
        logger.info("Removed existing directory that was zapped before")

def existingusers(rootpath):
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
    second = set(second)
    differences = [item for item in first if item not in second]
    return differences

def setpermissionsontree(rootpath):
    pass
    """ drwxrws--- 2 root terminator  6 28 mai   11:15 test
        chgrp terminator test

        chmod 770 test
        chmod g+s
    """
    _uid=8888
    _gid=1438417908

    try:
        pixar = people.config.getenvordefault("farm","user")
        _uid = pwd.getpwnam(pixar).pw_uid
        #_gid = grp.getgrnam(pixar).gr_gid    cant find module grp
        os.chown(rootpath,_uid,_gid)
        # os.chown(rootpath,'pixar', 0o2770)
        # os.chmod(rootpath, 5327)  #2755 decimal  www.rapidtables.com/convert/number/decimal-to-octal.htm
    except Exception, err:
        logger.warn("Cant chown {} {} - {}".format(_uid,_gid, err))

    try:
        _mask = 0o2775
        os.chmod(rootpath, _mask)  #2755 decimal  www.rapidtables.com/convert/number/decimal-to-octal.htm
        #os.chown(path,uid,gid)
        # import os
        # os.chmod('test', 02770)
    except Exception, err:
        logger.warn("Cant chmod () - {}".format(_mask, err))



# #################################################################################################
if __name__ == '__main__':
    main()
else:
    main()






