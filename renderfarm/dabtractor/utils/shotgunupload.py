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
from sww.renderfarm.dabtractor.factories import shotgun_factory as sgt



'''
    a = ShotgunBase()
    b=NewVersion(projectid=171,
                 shotid=3130,
                 taskid=9374,
                 versioncode='from tractor 1',
                 description='test version using shotgun_repos api',
                 ownerid=381,
                 media='/Users/Shared/UTS_Dev/Volumes/dabrender/work/user_work/matthewgidney/testing2017/movies/seq1.mov')

'''

def parseArguments():
    parser = argparse.ArgumentParser(description="Simple sendmail wrapper",  epilog="This is a pain to get right")
    parser.add_argument("-o", dest="Ownerid",  help="Shotgun Owner id")
    parser.add_argument("-p", dest="Projectid",  help="What you are sending")
    # parser.add_argument("--aid", dest="assetid",   help="Shotgun asset id")
    # parser.add_argument("--atid", dest="assettypeid",   help="Shotgun asset type id")
    # parser.add_argument("--sqid", dest="sequenceid",  help="Shotgun sequence id")
    # parser.add_argument("--epid", dest="episodeid",  help="Shotgun episode id")
    parser.add_argument("-s", dest="Shotid",  help="Shotgun shot id")
    parser.add_argument("-t", dest="Taskid",   help="Shotgun task id")
    parser.add_argument("-n", dest="Versioncode",  help="Name for the version")
    parser.add_argument("-d", dest="Description", help="Description")
    parser.add_argument("-m", dest="Media",help="Full path of media")
    return parser.parse_args()

# #####################################################################################################
if __name__ == '__main__':

    arguments = parseArguments()
    logger.debug("%s" % arguments)

    if not (parseArguments()):
        logger.critical("Cant parse args %s" % (arguments))
        sys.exit("ERROR Cant parse arguments")
    else:
        ownerid=int(arguments.Ownerid)
        projectid=int(arguments.Projectid)
        # assetid=arguments.assetid
        # assettypeid=arguments.assettypeid
        # sequenceid=arguments.sequenceid
        # episodeid=arguments.episodeid
        shotid=int(arguments.Shotid)
        if arguments.Taskid:
            taskid=int(arguments.Taskid)
        else:
            taskid=None
        versioncode=arguments.Versioncode
        description=arguments.Description
        media=arguments.Media

        sgt.NewVersion(
                 ownerid=ownerid,
                 projectid=projectid,
                 # assetid=assetid,
                 # assetid=assettypeid,
                 # episodeid=episodeid,
                 # sequenceid=sequenceid,
                 shotid=shotid,
                 taskid=taskid,
                 versioncode=versioncode,
                 description=description,
                 media=media
        )





