#!/usr/bin/python
"""
    All these Classes are to do with the defining of the USER

    This code handles the creation of a user area.
    At UTS the $USER is a number and there is no nice name exposed at all.
    However we can query this from the ldap database using ldapsearch.
    Thus we can definr the concept of renderusername and renderusernumber
    this just need to be in the path some place  dabanim/usr/bin
"""
import os
import sys
import string
import time
import subprocess
import environment_factory as envfac
import tractor.api.author as author
import shotgun_factory as sgt

# ##############################################################
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)5.5s \t%(filename)s as %(name)s \t%(message)s')
sh.setFormatter(formatter)
logger.addHandler(sh)
# ##############################################################

class UtsUser(object):
    """
    This class represents the UTS user account.  Data is queried from the
    LDAP server at UTS to build a model of the student.  This requires the
    user to authenticate against the UTS LDAP server.
    Once this is built then the class has methods to write the data to a
    Map object which caches the info into a json file.
    The json file is owned by pixar user and is edited by creating a farm
    job which runs as pixar user.  This afford a mechanism to manage the
    reading and writing to this map file.  Its not great but its ok.
    It could be that this file is a serialised file.
    """
    def __init__(self):
        """

        """
        self.name=None
        self.number = os.getenv("USER")
        self.job=None
        self.farmjob=envfac.FarmJob()
        self.env=envfac.Environment2()
        self.year=time.strftime("%Y")
        logger.info("Current Year is %s" % self.year)


        try:
            p = subprocess.Popen(["ldapsearch", "-h", "moe-ldap1.itd.uts.edu.au", "-LLL", "-D",
                                  "uid=%s,ou=people,dc=uts,dc=edu,dc=au" % self.number,
                                  "-Z", "-b", "dc=uts,dc=edu,dc=au", "-s", "sub", "-W",
                                  "uid=%s" % self.number, "uid", "mail"], stdout=subprocess.PIPE)
            result = p.communicate()[0].splitlines()

            logger.debug(">>>%s<<<<" % result)
            niceemailname = result[2].split(":")[1]
            nicename = niceemailname.split("@")[0]
            compactnicename = nicename.lower().translate(None, string.whitespace)
            cleancompactnicename = compactnicename.translate(None, string.punctuation)
            logger.info("UTS thinks you are: %s" % cleancompactnicename)
            self.name = cleancompactnicename

        except Exception, error7:
            logger.warn("    Cant get ldapsearch to work: %s" % error7)
            sys.exit("UTS doesnt seem to know you")




class FarmUser(object):
    def __init__(self):
        """ The user details as defined in the map, each user has data held in a
        dictionary """
        self.env=envfac.Environment2()
        self.user = self.env.environ["USER"]

        try:
            __sgt = sgt.Person()
        except Exception,err:
            logger.critical("Problem creating User: {}".format(err))
            sys.exit(err)
        else:
            self.name=__sgt.dabname
            self.number=__sgt.dabnumber





if __name__ == '__main__':
    """
    All this is testing, this  is a factory and shouldnt be called as 'main'
    """
    sh.setLevel(logging.DEBUG)
    logger.setLevel(logging.DEBUG)

    ###############################################

    uts = UtsUser()
    logger.debug( uts.name)
    logger.debug( uts.number)



