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

import argparse
import os
import sys
import string
import sww.renderfarm.dabtractor.factories.shotgun_factory as sgt


def main():
    """
    This funtion calls from shotgun all the valid tractor users and creates the user_work area required if it does not exit.
    It will also move those it finds to a deprecated space.

    :return:
    """
    people=sgt.People()


    peoplelist=[]
    dabwork = people.env.environ["DABWORK"]

    for person in people.people:
        peoplelist.append(sgt.People.cleanname(person.get('email')))

    makedirectorytree(dabwork,peoplelist)
    deprecatedirectory(dabwork,peoplelist)

def makedirectorytree(rootpath,rootnames=[]):

    try:
        for i, root in enumerate(rootnames):
            roottomake=os.path.join(rootpath,"user_work",root)
            if not os.path.exists(roottomake):
                logger.info("Someone missing: Making directory {}".format(roottomake))
                os.mkdir(roottomake)

    except Exception, err:
        logger.warn("Error making directories {}".format(err))
    else:
        pass
    finally:
        pass

def deprecatedirectory(rootpath,rootnames=[]):
    # existingusers= os.listdir(os.path.join(rootpath,"user_work"))
    # print existingusers(rootpath)
    # print rootnames
    directoriestozap=diff(existingusers(rootpath),rootnames)
    print "Difference:",directoriestozap
    zapdir=os.path.join(rootpath,"user_work",".zapped")
    userworkdir=os.path.join(rootpath,"user_work")
    if not os.path.exists(zapdir):
        os.mkdir(zapdir)
    for i,each in enumerate(directoriestozap):
        print each
        os.rename(os.path.join(userworkdir,each),
                  os.path.join(zapdir,each))

def existingusers(rootpath):
    directoriespresent=os.listdir(os.path.join(rootpath,"user_work"))
    cleaned=[]
    for i,each in enumerate(directoriespresent):
        firstletter = each[:1]
        if  firstletter != ".":
            cleaned.append(each)
    return cleaned


def diff(first, second):
        second = set(second)
        differences= [item for item in first if item not in second]
        print len(first),len(second),len(differences)
        return differences

def setpermissionsontree(rootpath):
    pass

def parseArguments():
    parser = argparse.ArgumentParser(description="Simple sendmail wrapper",
                                     epilog="This is a pain to get right")

    parser.add_argument("-s", dest="mailsubject",
                        action="append",
                        default=["Subject"],
                        help="The Subject of the mail")
    parser.add_argument("-b", dest="mailbody",
                        action="append",
                        default=["Body"],
                        help="What you are sending")
    parser.add_argument("-t", dest="mailto",
                        action="append",
                        default=["120988@uts.edu.au"],
                        help="who you are sending to")
    parser.add_argument("-f", dest="mailfrom",
                        action="append",
                        default=["pixar@uts.edu.au"],
                        help="Who you are sending as or from")

    return parser.parse_args()

# #####################################################################################################
if __name__ == '__main__':

    arguments = parseArguments()
    logger.debug("%s" % arguments)

    if not (parseArguments()):
        logger.critical("Cant parse args %s" % (arguments))
        sys.exit("ERROR Cant parse arguments")
    else:
        main()





