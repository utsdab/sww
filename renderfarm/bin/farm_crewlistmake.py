#!/usr/bin/env python
import os
import datetime
from renderfarm.dabtractor.factories import shotgun_factory as sgt

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


logger.info(">>>>>>> Checking if you are a Farm User <<<<<<<<")

# p=Person()
# logger.info("Shotgun Tractor User >>>> Login={number}   Name={name}  Email={email}".format(\
#     name=p.dabname,number=p.dabnumber,email=p.email))
# logger.info("-------------------------------FINISHED TESTING")


people=sgt.People()

# print "Current date and time: " , datetime.datetime.now()
# print "Or like this: " ,datetime.datetime.now().strftime("%y-%m-%d-%H-%M")
# print "Current year: ", datetime.date.today().strftime("%Y")
# print "Month of year: ", datetime.date.today().strftime("%B")
# print "Week number of the year: ", datetime.date.today().strftime("%W")
# print "Weekday of the week: ", datetime.date.today().strftime("%w")
# print "Day of year: ", datetime.date.today().strftime("%j")
# print "Day of the month : ", datetime.date.today().strftime("%d")
# print "Day of week: ", datetime.date.today().strftime("%A")
# sys.exit("stopped")

now = datetime.datetime.now().strftime("%y-%m-%d-%H-%M")
file="/Volumes/dabrender/__tmp/new_crew_list_{now}.txt".format(now=now)

## TODO  check maya prefs has a site setup

try:
    if os.path.exists(os.path.dirname(file)):
        people.writetractorcrewfile(file)
    else:
        raise Exception('Write Error')
except Exception, err:
    logger.critical("Error Writing File {}".format (file, err))
else:
    logger.info("Created temp crelist file to integrate : {}".format (file))








