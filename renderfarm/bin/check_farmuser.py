#!/usr/bin/env python
import os
import stat
from sww.renderfarm.dabtractor.factories import user_factory as uf
from sww.renderfarm.dabtractor.factories import environment_factory as ef
from sww.renderfarm.dabtractor.factories import utils_factory as utf

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


##  Check if user has an LDAP account
# try:
#     a = uf.UtsUser()
#     e = ef.Environment()
#     logger.info("LDAP ACCOUNT >>> name : %s" % (a.name))
#     logger.info("LDAP ACCOUNT >>> number : %s" % (a.number))
# except Exception, err:
#     logger.critical("Error You are NOT Known >>>> %s" % (err))
# finally:
#     pass




## TODO  check user is in map file
try:
    mu=uf.FarmUser()
except Exception, err:
    logger.critical("MAP FILE ### ERROR %s" % (err))
else:
    logger.info("MAP FILE >>> {} {} {}".format (\
                    mu.getusername(),
                    mu.getusernumber(),
                    mu.getenrolmentyear()))

## TODO  check there are userprefs
try:
    up="{}/{}".format(os.environ["DABUSERPREFS"],os.environ["USER"])
    utf.ensure_dir(up)
except Exception, err:
    logger.critical("USERPREFS ### %s" % (err))
else:
    logger.info("USERPREFS >>> {}".format(up))


## TODO  check user prefs has a config setup
try:
    config="{}/{}/config".format(os.environ["DABUSERPREFS"],os.environ["USER"])
    utf.ensure_link(config)
except Exception, err:
    logger.critical("USERPREFS ### Config Link ERROR {} : {}".format (config, err))
else:
    logger.info("USERPREFS >>> config link : {}".format (config))


## TODO  check maya prefs has a config setup
try:
    mayaprefs="{}/{}/mayaprefs".format(os.environ["DABUSERPREFS"],os.environ["USER"])
    utf.ensure_link(mayaprefs)
except Exception, err:
    logger.critical("USERPREFS ### mayaprefs link ERROR {} : {}".format (mayaprefs, err))
else:
    logger.info("USERPREFS >>> mayaprefs link : {}".format (mayaprefs))


## TODO  check there is a user_work area
try:
    uw=os.path.join(os.environ["DABWORK"],"user_work",mu.getusername())
    utf.ensure_dir(uw)
except Exception, err:
    logger.critical("USER_WORK ### ERROR %s" % (err))
else:
    logger.info("USER_WORK >>> {}".format (uw))


## TODO  check permissions are ok
# Use os.access() with flags os.R_OK, os.W_OK, and os.X_OK.
# >>> import os
# >>> statinfo = os.stat('somefile.txt')
# >>> statinfo
# os.stat_result(st_mode=33188, st_ino=7876932, st_dev=234881026,
# st_nlink=1, st_uid=501, st_gid=501, st_size=264, st_atime=1297230295,
# st_mtime=1297230027, st_ctime=1297230027)
# >>> statinfo.st_size
# 264
statinfo = os.stat(up)
print statinfo.st_gid, statinfo.st_uid
print stat.S_IFDIR, stat.S_IFLNK,stat.S_IMODE(statinfo.st_mode)

mode = os.stat(uw).st_mode
# otherExec  = bool(m & 0001)
# otherWrite = bool(m & 0002)
# otherRead  = bool(m & 0004)
groupExec  = bool(mode & 0010)
groupWrite = bool(mode & 0020)
groupRead  = bool(mode & 0040)
otherRead  = bool(mode & stat.S_IROTH)
otherWrite = bool(mode & stat.S_IWOTH)
otherExec  = bool(mode & stat.S_IXOTH)
os.chmod(uw,stat.S_IWOTH)
print groupRead,groupWrite,groupExec
print otherRead,otherWrite,otherExec
# uw="/Users/120988/testfile"
try:
    os.chmod(uw,0775) # -rwxr-xr-x octal
except Exception, err:
    print "failed",err
else:
    print uw

## TODO  check in tractor crewlist



