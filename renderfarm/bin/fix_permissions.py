#!/usr/bin/python
'''
command to be run as a farm job by pixar   or from command line
attempts to make sure group is owned by pixar user 8888
and is
rwxrwsr_x  for directories
rw_rw_r__  for files
user:pixar

'''

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)5.5s \t%(name)s \t%(message)s')
sh.setFormatter(formatter)
logger.addHandler(sh)

import os
import argparse
import shutil

def dochmod(path):
    '''
    This is going to be octal stuff
    http://permissions-calculator.org

    0664 ---> rw_rw_r__
    0775 ---> rwxrwxr_x
    2775 ---> rwxrwxsr_x     setgid
    3775 ---> rwxrwxsr_xt    setgid and stickybit

    to call these as octal in chmod
    If you're wondering why that leading zero is important, it's because permissions are set as an octal integer,
    and Python automagically treats any integer with a leading zero as octal. So os.chmod("file", 484)
    (in decimal) would give the same result.

    '''

    for root, dirs, files in os.walk(path):

        for path in dirs:
            # os.chown(momo, 502, 20)
            try:
                os.chmod(os.path.join(root,path), 02775)
            except Exception, err:
                logger.warn("Problem on directory {} {}".format(path, err))
            else:
                logger.debug("Changed permissions to rwxrwsr_x on {}".format(path))
        for path in files:
            try:
                os.chmod(os.path.join(root,path), 0664)
            except Exception, err:
                logger.warn("Problem on file {} {}".format(path, err))
            else:
                logger.debug("Changed permissions to rw_rw_r__ on {}".format(path))


def parseArguments():
    parser = argparse.ArgumentParser(description="Simple sendmail wrapper",  epilog="This is a pain to get right")
    parser.add_argument("-p", dest="path",  help="Path to File or Directory to fix - recursive by default")
    parser.add_argument("--norecurse", dest="norecurse",   help="No recursive behaviour")
    return parser

def main(path):
    if os.path.exists(path):
        dochmod(path)
    else:
        logger.warn("No path {}".format(path))


if __name__ == '__main__':
    # Main routine - needs one path argument
    parser = parseArguments()
    arguments = parser.parse_args()
    logger.debug("%s" % arguments)
    _fail = None

    if arguments.path:
        try:
            if os.path.exists(arguments.path):
                raise Exception("No file or directory found")
        except IOError, err:
            logger.critical("{}: {}".format(err, arguments.path))
        else:
            main(arguments.path)
        finally:
            print "ok"

    else:
        logger.warn("{}".format("You need to provide a path to something, try something like: fix_permissions.py -p "
                                "/tmp/myfile"))
        logger.setLevel(logging.DEBUG)
        main("/tmp/xxx")

