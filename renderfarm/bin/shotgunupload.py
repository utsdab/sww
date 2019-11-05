#!/usr/bin/python

import argparse
import os
import sys
from renderfarm.dabtractor.factories import shotgun_factory as sgt
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)5.5s \t%(name)s \t%(message)s')
sh.setFormatter(formatter)
logger.addHandler(sh)

def parseArguments():
    parser = argparse.ArgumentParser(description="Simple sendmail wrapper",  epilog="This is a pain to get right")
    parser.add_argument("-o", dest="Ownerid",  help="Shotgun Owner id")
    parser.add_argument("-p", dest="Projectid",  help="What you are sending")
    parser.add_argument("-a", dest="Assetid",   help="Shotgun asset id")
    # parser.add_argument("--atid", dest="assettypeid",   help="Shotgun asset type id")
    # parser.add_argument("--sqid", dest="sequenceid",  help="Shotgun sequence id")
    # parser.add_argument("--epid", dest="episodeid",  help="Shotgun episode id")
    parser.add_argument("-s", dest="Shotid",  help="Shotgun shot id")
    parser.add_argument("-t", dest="Taskid",   help="Shotgun task id")
    parser.add_argument("-n", dest="Versioncode",  help="Name for the version")
    parser.add_argument("-d", dest="Description", help="Description")
    parser.add_argument("-m", dest="Media",help="Full path of media")
    return parser

# #####################################################################################################
if __name__ == '__main__':

    parser = parseArguments()
    arguments = parser.parse_args()
    logger.info("%s" % arguments)
    _fail = None

    if not arguments.Ownerid:
        _fail="no ownerid"
    if not arguments.Projectid:
        _fail="no Projectid"
    if not arguments.Shotid:
        _fail="no Shotid"
    if not arguments.Media:
        _fail="no Media"
    try:
        if not os.path.isfile(arguments.Media):
            raise Exception("No file")
    except Exception, err:
        _fail="Media non existant"
        logger.critical("Media non existant: {}".format(arguments.Media))

    if not parser or  _fail:
        parser.print_help()
        logger.critical("Cant parse args: {} >> {}".format(arguments,_fail))
        logger.info("This is not good, Exiting cleanly anyway")
        sys.exit(0)
    try:
        ownerid=int(arguments.Ownerid)
        projectid=int(arguments.Projectid)
        # assetid=arguments.assetid[-1:]
        # sequenceid=arguments.sequenceid[-1:]
        shotid=int(arguments.Shotid)
        if arguments.Taskid:
            taskid=int(arguments.Taskid)
        else:
            taskid=None
        versioncode=arguments.Versioncode
        description=arguments.Description
        media=arguments.Media
    except Exception, err:
        logger.warn("Wrong type of input data: {}".format(err))
        sys.exit(0)
    try:
        sgt.Version(
                 ownerid=ownerid,
                 projectid=projectid,
                 # assetid=assetid,
                 # sequenceid=sequenceid,
                 shotid=shotid,
                 taskid=taskid,
                 versioncode=versioncode,
                 description=description,
                 media=media )
    except Exception, err:
        logger.critical("SHOTGUN SAYS {}".format(err))






