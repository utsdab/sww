#!/usr/bin/env python
import os
import stat
from sww.renderfarm.dabtractor.factories import user_factory as uf
from sww.renderfarm.dabtractor.factories import environment_factory as ef
from sww.renderfarm.dabtractor.factories import utils_factory as utf
from sww.renderfarm.dabtractor.factories import shotgun_factory as sgt

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


logger.info("{:+^70}".format(" Checking if you are a Farm User "))
# #  Check if user has an LDAP account
# try:
#     a = uf.UtsUser()
#     # e = ef.Environment()
#     logger.info("LDAP ACCOUNT >>> name : %s" % (a.name))
#     logger.info("LDAP ACCOUNT >>> number : %s" % (a.number))
# except Exception, err:
#     logger.critical("Error You are NOT Known >>>> %s" % (err))
# finally:
#     pass


try:
    su=sgt.Person()
except UserWarning, err:
    logger.critical("USER NOT REGISTERED IN SHOTGUN %s" % (err))
else:
    logger.info("CHECK {:-^20} {} {}".format("[shotgun login]",su.login,su.dabname))


## TODO  check there are userprefs
try:
    up="{}/{}".format(os.environ["DABUSERPREFS"],os.environ["USER"])
    utf.ensure_dir(up)
except Exception, err:
    logger.critical("USERPREFS ### %s" % (err))
else:
    logger.info("CHECK {:-^20} {}".format("[user_prefs]",up))


## TODO  check user prefs has a config setup
try:
    config="{}/{}/config".format(os.environ["DABUSERPREFS"],os.environ["USER"])
    utf.ensure_link(config)
except Exception, err:
    logger.critical("USERPREFS ### Config Link ERROR {} : {}".format (config, err))
else:
    logger.info("CHECK {:-^20} {}".format ("[config link]",config))


## TODO  check maya prefs has a config setup
try:
    mayaprefs="{}/{}/config/mayaprefs".format(os.environ["DABUSERPREFS"],os.environ["USER"])
    utf.ensure_dir(mayaprefs)
except Exception, err:
    logger.critical("USERPREFS ### mayaprefs link ERROR {} : {}".format (mayaprefs, err))
else:
    logger.info("CHECK {:-^20} {}".format ("[mayprefs]",mayaprefs))


## TODO  check there is a user_work area
try:
    uw=os.path.join(os.environ["DABWORK"],"user_work",su.dabname)
    utf.ensure_dir(uw)
except Exception, err:
    logger.critical("USER_WORK ### ERROR %s" % (err))
else:
    logger.info("CHECK {:-^20} {}".format ("[user_work]",uw))


## TODO  check permissions are ok
mode = os.stat(uw).st_mode
stat_info = os.stat(uw)
uid = stat_info.st_uid
gid = stat_info.st_gid
# otherExec  = bool(m & 0001)
# otherWrite = bool(m & 0002)
# otherRead  = bool(m & 0004)
groupExec  = bool(mode & 0010)
groupWrite = bool(mode & 0020)
groupRead  = bool(mode & 0040)
otherRead  = bool(mode & stat.S_IROTH)
otherWrite = bool(mode & stat.S_IWOTH)
otherExec  = bool(mode & stat.S_IXOTH)

logger.info("CHECK {:-^20} {} {} {} ".format("[user_work g rwx]",groupRead,groupWrite,groupExec))
logger.info("CHECK {:-^20} {} {} {} ".format("[user_work o rwx]",otherRead,otherWrite,otherExec))
logger.info("CHECK {:-^20} {} {}".format("[user UID GID]",uid, gid))

## TODO  check in tractor crewlist

## TODO  check group special bit





