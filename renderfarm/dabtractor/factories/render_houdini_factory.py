#!/usr/bin/env python2
'''
Houdini Render Job
'''
#TODO make this work

import json
import os
import time
import sys
import utils_factory as utils
import environment_factory as envfac
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)5.5s \t%(name)s \t%(message)s')
sh.setFormatter(formatter)
logger.addHandler(sh)

class Job(envfac.TractorJob):
    ''' The payload of gui-data needed to describe the render job '''
    def __init__(self):
        super(Job, self).__init__()
        self.projectfullpath=None
        self.scenefilefullpath=None
        # This gets department from shotgun and checks it is a valid one in the json file
        # the department is year1 or year2 etc a user can only be in one department.
        if self.department in self.config.getoptions("renderjob", "projectgroup"):
            logger.info("Department {}".format(self.department))
        else:
            self.department="Other"
        self.adminemail = self.config.getdefault("admin", "email")
        logger.info("admin is {}".format(self.adminemail))


class Render(object):
    ''' Mantra job defined using the tractor api '''
    def __init__(self, job):
        self.job=job
        # utils.printdict( self.job.__dict__)
        self.job.dabwork="$DABWORK"
        self.job.envprojectalias = "$PROJECT"
        self.projectpathalias = "$DABRENDER/$TYPE/$SHOW/$PROJECT"
        self.scenefilefullpathalias = "$DABRENDER/$TYPE/$SHOW/$PROJECT/$SCENE"
        self.renderpathalias = "$DABRENDER/$TYPE/$SHOW/$PROJECT/$SCENENAME"
        self.renderimagesalias = "$DABRENDER/$TYPE/$SHOW/$PROJECT/$SCENENAME/images"

        self.projectpath = os.path.join(self.job.dabwork, self.job.envtype, self.job.envshow, self.job.envproject)
        self.scenefilefullpath = os.path.join( self.job.dabwork, self.job.envtype, self.job.envshow, self.job.envproject,self.job.envscene)
        self.scenename = os.path.basename(self.job.envscene)
        self.scenebasename = os.path.splitext(self.scenename)[0]
        self.sceneext = os.path.splitext(self.scenename)[1]
        self.renderpath = os.path.join( self.job.dabwork, self.job.envtype, self.job.envshow, self.job.envproject,"houdini",self.scenebasename)
        self.renderdirectory = os.path.join(self.renderpath,"images")
        self.envkey_houdini = "houdini{}".format(self.job.houdiniversion)
        self.options = ""
        self.outformat = "exr"
        self.finaloutputimagebase = "{}/{}".format(self.renderpath,self.scenebasename)
        self.thedate=time.strftime("%d-%B-%Y")

    def build(self):
        ''' Main method to build the job '''
        logger.info("Starting job BUILD")

        # ################# Job Metadata as JSON
        _jobMetaData={}
        _jobMetaData["email"] = self.job.useremail
        _jobMetaData["name"] = self.job.username
        _jobMetaData["number"] = self.job.usernumber
        _jobMetaData["scenename"] = self.scenename
        _jobMetaData["projectpath"] = self.projectpath
        _jobMetaData["startframe"] = self.job.jobstartframe
        _jobMetaData["endframe"] = self.job.jobendframe
        _jobMetaData["jobtype"] = "HOU"
        _jsonJobMetaData = json.dumps(_jobMetaData)

        # ################ 0 JOB ################
        self.renderjob = self.job.author.Job(title="HOU: {} {} {}-{}".format(
              self.job.username, self.scenename, self.job.jobstartframe, self.job.jobendframe),
              priority=10,
              envkey=["ProjectX",
                    "TYPE={}".format(self.job.envtype),
                    "SHOW={}".format(self.job.envshow),
                    "PROJECT={}".format(self.job.envproject),
                    "SCENE={}".format(self.job.envscene),
                    "SCENENAME={}".format(self.scenebasename)],
              metadata=_jsonJobMetaData,
              comment="User is {} {} {}".format(self.job.useremail,self.job.username,self.job.usernumber),
              projects=[str(self.job.department)],
              tier=str(self.job.farmtier),
              tags=["theWholeFarm", ],
              service="ShellServices")


        # ############## 0 ThisJob #################
        task_job = self.job.author.Task(title="Houdini Mantra Job")
        task_job.serialsubtasks = 1

        # ############## 4 NOTIFY ADMIN OF TASK START ##########
        logger.info("admin email = {}".format(self.job.adminemail))
        task_notify_admin_start = self.job.author.Task(title="Register", service="ShellServices")
        task_notify_admin_start.addCommand( self.mail(self.job.adminemail,"HOUDINI REGISTER", "{na}".format(na=self.job.username), "{na} {no} {em} {sc}".format(na=self.job.username, no=self.job.usernumber,em=self.job.useremail, sc=self.scenefilefullpath)))
        task_job.addChild(task_notify_admin_start)

        # ############## 5 NOTIFY USER OF JOB START ###############
        if self.job.optionsendjobstartemail:
            logger.info("email = {}".format(self.job.useremail))
            task_notify_start = self.job.author.Task(title="Notify Start", service="ShellServices")
            task_notify_start.addCommand(self.mail(self.job.useremail, "JOB", "START", "{}".format(self.scenefilefullpath)))
            task_job.addChild(task_notify_start)

        # ####### make a render directory as needed
        # _proj = self.projectpath
        _ifdDir = os.path.join(self.projectpath,"ifds")
        _imgDir = os.path.join(self.projectpath,"render",self.scenebasename)
        task_prefilight = self.job.author.Task(title="Make render directory")

        command_mkdirs1 = self.job.author.Command(argv=[ "mkdir","-p", _ifdDir ],
                tags=["houdini", "theWholeFarm"],
                atleast=int(self.job.jobthreads),
                atmost=int(self.job.jobthreads),
                service="ShellServices")
        command_mkdirs4 = self.job.author.Command(argv=[ "mkdir", "-p",_imgDir ],
                tags=["houdini", "theWholeFarm"],
                atleast=int(self.job.jobthreads),
                atmost=int(self.job.jobthreads),
                service="ShellServices")

        task_prefilight.addCommand(command_mkdirs1)
        task_prefilight.addCommand(command_mkdirs4)
        task_job.addChild(task_prefilight)

        # ############## 3 GENERATE INTERMEDIATE FILES ##############
        task_render_allframes = self.job.author.Task(title="RENDER FRAMES")
        task_render_allframes.serialsubtasks = 1
        task_gen_allframes = self.job.author.Task(title="IFDGEN {}-{}".format(self.job.jobstartframe,self.job.jobendframe))

        # divide the frame range up into chunks
        _totalframes = int(self.job.jobendframe) - int(self.job.jobstartframe) + 1
        _chunks = int(self.job.jobchunks)
        _framesperchunk = _totalframes
        if _chunks < _totalframes:
            _framesperchunk = int( _totalframes / _chunks )
        else:
            _chunks = 1

        #TODO not needed now - can use quotes


        for i, chunk in enumerate(range( 1, _chunks + 1 )):
            _offset = i * _framesperchunk
            _chunkstart = int(self.job.jobstartframe) + _offset
            _chunkend = _chunkstart + _framesperchunk - 1
            if chunk >= _chunks:
                _chunkend = int(self.job.jobendframe)
            logger.info("Chunk {} is frames {}-{}".format(chunk, _chunkstart, _chunkend))
            task_generate_ifd = self.job.author.Task(title="_IFDGEN Chunk {} frames {}-{}".format( chunk, _chunkstart, _chunkend ))

            #TODO is this hrender or hscript or hbatch
            command_hserver = "hserver"

            '''
            hscript  -R -v 3 -c "render /out/mantra1" -c "quit" /Volumes/dabrender/work/project_work/mattg/TESTING_Renderfarm/HoudiniProjects/houdini17_test_01/primitives_test.hipnc
            hrender /Users/Shared/UTS_Jobs/TESTING_HOUDINI/HoudiniProjects/testProject01/scripts/torus1.hipnc -d mantra1 -v -f 1 240 -i 1
            '''
            __command = "hscript -R -i -v 3 -c {command} -c {quit} -f {start} {end} -d {scene}".format(
                start=_chunkstart,
                end=_chunkend,
                scene=self.scenefilefullpath,
                command="\'render /out/mantra1\'",
                quit = "quit")
            '''
            "hrender -R -e -f 1 4 -i 1 -v -d mantra1 
            -o $DABWORK/project_work/mattg/TESTING_Renderfarm/HoudiniProjects/houdini17_test_01/ifds/out.$F.ifd $DABWORK/project_work/mattg/TESTING_Renderfarm/HoudiniProjects/houdini17_test_01/primitives_test.hipnc"
            '''
            command_hrender = "hrender -R -e -f {start} {end} -i {step} -v -d {node} -o {output} {scenefile}".format(
                node="mantra1",
                start=_chunkstart,
                end=_chunkend,
                step=1,
                threads = self.job.jobthreads,
                output = "{dir}/{scenebase}.$F.ifd".format(dir=_ifdDir, scenebase=self.scenebasename),
                scenefile=self.scenefilefullpath)

            command_hserver = self.job.author.Command(
                argv=[ command_hserver ],
                samehost = 1,
                tags=["houdini", "theWholeFarm"],
                atleast=int(self.job.jobthreads),
                atmost=int(self.job.jobthreads),
                envkey=[self.envkey_houdini],
                service="Houdini")
            command_generate_ifd = self.job.author.Command(
                argv=[ command_hrender ],
                samehost = 1,
                tags=["houdini", "theWholeFarm"],
                atleast=int(self.job.jobthreads),
                atmost=int(self.job.jobthreads),
                envkey=[self.envkey_houdini],
                service="Houdini")
            # task_generate_ifd.addCommand(command_hserver)
            task_generate_ifd.addCommand(command_generate_ifd)
            task_gen_allframes.addChild(task_generate_ifd)

        task_render_allframes.addChild(task_gen_allframes)

        # ############### 4 RENDER ##############
        task_render_frames = self.job.author.Task(title="RENDER {}-{}".format(self.job.jobstartframe,self.job.jobendframe))
        task_render_frames.serialsubtasks = 0

        for frame in range( int(self.job.jobstartframe), int(self.job.jobendframe) + 1, int(self.job.jobbyframe) ):
            # ################# Job Metadata as JSON
            _ifdfile = "{dir}/{node}.{frame:01d}.ifd".format(dir=_ifdDir, node="mantra1", scenebase=self.scenebasename, frame=frame)
            _outfile = "{dir}/{scenebase}.{frame:04d}.exr".format(dir=_imgDir, node="mantra1", scenebase=self.scenebasename, frame=frame)
            _shotgunupload = "PR:{} SQ:{} SH:{} TA:{}".format(self.job.shotgunProject, self.job.shotgunSeqAssetType, self.job.shotgunShotAsset, self.job.shotgunTask)
            _taskMetaData={}
            _taskMetaData["imgfile"] = _outfile
            _taskMetaData["ifdfile"] = _ifdfile
            _taskMetaData["shotgunupload"] = _shotgunupload
            _jsontaskMetaData = json.dumps(_taskMetaData)
            _title = "RENDER Frame {}".format(frame)
            task_render_ifd = self.job.author.Task(title=_title, metadata=_jsontaskMetaData)

            _commonargs = [ "mantra", "-f", _ifdfile, _outfile ]
            _rendererspecificargs = [ "-V", "3", ]

            # if self.job.optionmaxsamples != "FROMFILE":
            # rendererspecificargs.extend([ "-maxsamples", "{}".format(self.job.optionmaxsamples) ])
            # if self.job.jobthreadmemory != "FROMFILE":
            #     rendererspecificargs.extend([ "-memorylimit", "{}".format(self.job.jobthreadmemory) ])

            _rendererspecificargs.extend([
                "-t", "{}".format(self.job.jobthreads),
            ])
            _userspecificargs = [ utils.expandargumentstring(self.options)]
            _finalargs = _commonargs + _rendererspecificargs
            command_render = self.job.author.Command(
                argv=_finalargs,
                tags=["mantra", "theWholeFarm"],
                atleast=int(self.job.jobthreads),
                atmost=int(self.job.jobthreads),
                envkey=[self.envkey_houdini],
                service="Houdini")

            # task_render_ifd.addCommand(command_hserver)
            task_render_ifd.addCommand(command_render)

            task_render_frames.addChild(task_render_ifd)

        task_render_allframes.addChild(task_render_frames)
        task_job.addChild(task_render_allframes)

        # ############## 5 PROXY ###############
        if self.job.optionmakeproxy:
            #TODO  switch to ffmpeg here

            task_proxy = self.job.author.Task(title="PROXY MAKE".format(self.job.jobstartframe,self.job.jobendframe))
            task_rvio_proxy = self.job.author.Task(title="_PROXY RVIO".format(self.job.jobstartframe,self.job.jobendframe))
            task_ffmpeg_proxy = self.job.author.Task(title="_PROXY FFMPEG".format(self.job.jobstartframe,self.job.jobendframe))

            #### making proxys with rvio
            # TODO we need to find the actual output frames - right now we huess
            # (self.job.seqbasename,self.job.seqtemplatename)=utils.getSeqTemplate(self.job.selectedframename)

            self.job.proxy_output_base = "{}_{}.mov".format(self.scenebasename,utils.getnow())
            self.job.proxy_output_base2 = "{}_{}_2.mov".format(self.scenebasename,utils.getnow())

            self.job.proxy_input_seqbase = "{scene}_beauty.####.exr".format(scene=self.scenebasename)
            self.job.proxy_input_image_seqbase2 = "{scene}_beauty.%04d.exr".format(scene=self.scenebasename)

            self.job.proxy_input_directory = "{proj}/images/{scene}/".format(proj=self.projectpath, scene=self.scenebasename)
            self.job.proxy_output_directory = "{proj}/movies/".format(proj=self.projectpath, scene=self.scenebasename)

            self.job.proxy_input_seq = os.path.join(self.job.proxy_input_directory, self.job.proxy_input_seqbase)
            self.job.proxy_input_seq2 = os.path.join(self.job.proxy_input_directory, self.job.proxy_input_image_seqbase2)

            self.job.proxy_output = os.path.join(self.job.proxy_output_directory, self.job.proxy_output_base)
            self.job.proxy_output2 = os.path.join(self.job.proxy_output_directory, self.job.proxy_output_base2)


            # _imgfile = "{proj}/images/{scenebase}/{scenebase}_beauty.{frame:04d}.{ext}".format( proj=self.projectpath, scenebase=self.scenebasename, frame=frame, ext=self.outformat)

            try:
                utils.makedirectoriesinpath(os.path.dirname(self.job.proxy_output_directory))
            except Exception, err:
                logger.warn("Cant make proxy output directory {}".format(err))

            try:
                _option1 = "-v -fps 25 -rthreads {threads} -outres {xres} {yres} -t {start}-{end}".format(
                           threads="4",
                           xres="1280",
                           yres="720",
                           start=self.job.jobstartframe,
                           end=self.job.jobendframe)
                _option2 = "-out8 -outgamma 2.2"
                _option3 = "-overlay frameburn 0.5 1.0 30 -leader simpleslate UTS_BDES_ANIMATION Type={} Show={} Project={} File={} Student={}-{} Group={} Date={}".format(
                              self.job.envtype,
                              self.job.envshow,
                              self.job.envproject,
                              self.job.proxy_output_base,
                              self.job.usernumber,
                              self.job.username,
                              self.job.department,
                              self.thedate)

                _output = "-o %s" % self.job.proxy_output
                _rvio_cmd = [ utils.expandargumentstring("rvio %s %s %s %s %s" % (self.job.proxy_input_seq, _option1, _option2, _option3, _output)) ]
                task_proxy = self.job.author.Task(title="Proxy Generation")
                rviocommand = self.job.author.Command(argv=_rvio_cmd, service="Transcoding",tags=["rvio", "theWholeFarm"],atleast=int(self.job.jobthreads), atmost=int(self.job.jobthreads),envkey=["ShellServices"])

                task_rvio_proxy.addCommand(rviocommand)
                task_proxy.addChild(task_rvio_proxy)

            except Exception, proxyerror:
                logger.warn("Cant make an rvio proxy {}".format(proxyerror))

            # ffmpeg proxy
            # ffmpeg version 4.1 Copyright (c) 2000-2018 the FFmpeg developers is best
            try:
                # ffmpeg -y -gamma 2.2 -i rmf22_test_cube_textured_100.0001__perspShape_beauty.%04d.exr -vcodec libx264 -pix_fmt yuv420p -preset slow -crf 18 -filter:v scale=1280:720 -r 25 out.mov
                _option1 = "-y -gamma 2.2 "
                _option2 = "-i {input} -vcodec libx264 -pix_fmt yuv420p -preset slow -crf 18 -filter:v scale=1280:720 -r 25 ".format(input = self.job.proxy_input_seq2)
                _option3 = "{outfile}".format(outfile=self.job.proxy_output2)
                _cmd = [ utils.expandargumentstring("ffmpeg %s %s %s" % ( _option1, _option2, _option3)) ]
                ffmpegcommand = self.job.author.Command(argv=_cmd, service="Transcoding",tags=["rvio", "theWholeFarm"],atleast=int(self.job.jobthreads), atmost=int(self.job.jobthreads),envkey=["ShellServices"])

                task_ffmpeg_proxy.addCommand(ffmpegcommand)
                task_proxy.addChild(task_ffmpeg_proxy)

            except Exception, proxyerror:
                logger.warn("Cant make an ffmpeg proxy {}".format(proxyerror))
            task_job.addChild(task_proxy)

        else:
            logger.info("make proxy = {}".format(str(self.job.optionmakeproxy)))

        # ############## 6 SEND TO SHOTGUN ###############
        if self.job.sendToShotgun:
            logger.info("Sending to Shotgun = {} {} {} {}".format(self.job.shotgunProjectId,self.job.shotgunSeqAssetTypeId,self.job.shotgunShotAssetId,self.job.shotgunTaskId))
            _description = "Auto Uploaded from {} {} {} {}".format(self.job.envtype,self.job.envproject, self.job.envshow,self.job.envscene)
            _uploadcmd = ""
            if self.job.shotgunTaskId:
                _uploadcmd = ["shotgunupload.py",
                              "-o", str(self.job.shotgunOwnerId),
                              "-p", str(self.job.shotgunProjectId),
                              "-s", str(self.job.shotgunShotAssetId),
                              "-a", str(self.job.shotgunShotAssetId),
                              "-t", str(self.job.shotgunTaskId),
                              "-n", self.job.proxy_output_base2,
                              "-d", _description,
                              "-m", self.job.proxy_output2 ]
            elif not self.job.shotgunTaskId:
                _uploadcmd = ["shotgunupload.py",
                              "-o", str(self.job.shotgunOwnerId),
                              "-p", str(self.job.shotgunProjectId),
                              "-s", str(self.job.shotgunShotAssetId),
                              "-a", str(self.job.shotgunShotAssetId),
                              "-n", self.job.proxy_output_base2,
                              "-d", _description,
                              "-m", self.job.proxy_output2 ]
            task_upload = self.job.author.Task(title="SHOTGUN Upload P:{} SQ:{} SH:{} T:{}".format( self.job.shotgunProject,self.job.shotgunSeqAssetType,self.job.shotgunShotAsset, self.job.shotgunTask))

            uploadcommand = self.job.author.Command(
                argv=_uploadcmd, service="ShellServices",
                tags=["shotgun", "theWholeFarm"],
                envkey=["PixarRender"])
            task_upload.addCommand(uploadcommand)
            task_job.addChild(task_upload)

        # ############## 5 NOTIFY JOB END ###############
        if self.job.optionsendjobendemail:
            logger.info("email = {}".format(self.job.useremail))
            task_notify_end = self.job.author.Task(title="Notify End", service="ShellServices")
            task_notify_end.addCommand(self.mail(self.job.useremail, "JOB", "COMPLETE", "{}".format(self.scenefilefullpath)))
            task_job.addChild(task_notify_end)
        self.renderjob.addChild(task_job)
        logger.info("Ending job BUILD")

    def validate(self):
        #TODO  check to see if there is already this job on the farm
        logger.info("Starting job VALIDATE")
        logger.info("\n\n{:_^80}\n{}\n{:_^80}".format("snip", self.renderjob.asTcl(),"snip"))
        logger.info("Ending job VALIDATE")

    def mail(self, to=None, level="Level", trigger="Trigger", body="Render Progress Body"):
        if not to:
            to = self.job.adminemail
        bodystring = "Houdini Render Progress: \nLevel: {}\nTrigger: {}\n\n{}".format(level, trigger, body)
        subjectstring = "FARM JOB: {} {} {} {}".format(level,trigger, str(self.scenebasename), self.job.username)
        mailcmd = self.job.author.Command(
            argv=["sendmail.py", "-t", to, "-b", bodystring, "-s", subjectstring],
            service="ShellServices")
        return mailcmd

    def spool(self):
        # double check scene file exists
        logger.info("Starting job SPOOL")
        logger.info("Double Checking: {}".format(os.path.expandvars(self.scenefilefullpath)))
        if os.path.exists(os.path.expandvars(self.scenefilefullpath)):
            try:
                logger.info("Spooled correctly")
                self.renderjob.spool(owner=self.job.config.getdefault("tractor","jobowner"),port=int(self.job.config.getdefault("tractor","port")))
            except Exception, spoolerr:
                logger.warn("A spool error %s" % spoolerr)
        else:
            message = "Houdini scene file non existant %s" % self.scenefilefullpath
            logger.critical(message)
            logger.critical(os.path.normpath(self.scenefilefullpath))
            logger.critical(os.path.expandvars(self.scenefilefullpath))
            sys.exit(message)
        logger.info("Ending job SPOOL")


###############################################################################
if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)
'''

ASSUMPTION
houdini_project
    abc/
    audio/
    backup/
    comp/
    desk/
    flip/
    geo/
    hda/
    ifds/
        {scene}/
            *.ifd
    primitives_test.hipnc (this is the scene)
    render/
        {scene}/
            *.exr
    scripts/
    sim/
    tex/
    video/

DABMLB0606627MG:testProject01 120988$

hrender /Users/Shared/UTS_Jobs/TESTING_HOUDINI/HoudiniProjects/testProject01/scripts/torus1.hipnc
 -d mantra1 -v -f 1 240 -i 1

hrender -e -f 1 100 -v  -d mantra2 primitives_test.hipnc

Usage:

Single frame:   hrender    [options] driver|cop file.hip [imagefile]
Frame range:    hrender -e [options] driver|cop file.hip

driver|cop:     -c /img/imgnet
                -c /img/imgnet/cop_name
                -d output_driver

options:        -w pixels       Output width
                -h pixels       Output height
                -F frame        Single frame
                -b fraction     Image processing fraction (0.01 to 1.0)
		-t take		Render a specified take
                -o output       Output name specification
                -v              Run in verbose mode
                -I              Interleaved, hscript render -I

with "-e":	-f start end    Frame range start and end
                -i increment    Frame increment

Notes:  1)  For output name use $F to specify frame number (e.g. -o $F.pic).
        2)  If only one of width (-w) or height (-h) is specified, aspect ratio
            will be maintained based upon aspect ratio of output driver.

Error: Cannot specify frame range without -e.




mantra -f frame0001.ifd rendered_frame0001.pic
mantra -V 3 -f ifds/mantra1.1.ifd

cd /Applications/Houdini/Houdini17.0.416
./Frameworks/Houdini.framework/Versions/Current/Resources/houdini_setup
./Frameworks/Houdini.framework/Versions/Current/Resources/houdini_setup_bash


------  HFS

export HFS=/Applications/Houdini/Current/Frameworks/Houdini.framework/Versions/Current/Resources

------
if [ ! -d houdini  -o  !  -d bin ]; then
    echo "You must cd to the Houdini installation directory before"
    echo "sourcing this script. This allows the script to determine"
    echo "the installed location."
else
    export HFS="$PWD"

    #
    #  The following are some handy shortcuts:
    #
    export H="${HFS}"
    export HB="${H}/bin"
    export HDSO="${H}/../Libraries"
    export HD="${H}/demo"
    export HH="${H}/houdini"
    export HHC="${HH}/config"
    export HT="${H}/toolkit"
    export HSB="${HH}/sbin"

    #
    #  The following is used as the generic /tmp path.  This is also
    # set on Windows to the temporary directory, so can be used for
    # system independent .hip files.
    #
    export TEMP=/tmp

    #
    # Look for java.
    #
    export JAVA_HOME=/Library/Java/Home

    PATH="${HB}:${HSB}:$PATH"
    export PATH

    export HOUDINI_MAJOR_RELEASE=17
    export HOUDINI_MINOR_RELEASE=0
    export HOUDINI_BUILD_VERSION=416
    export HOUDINI_VERSION="${HOUDINI_MAJOR_RELEASE}.${HOUDINI_MINOR_RELEASE}.${HOUDINI_BUILD_VERSION}"

    # Build machine related stuff
    export HOUDINI_BUILD_KERNEL="17.7.0"
    export HOUDINI_BUILD_PLATFORM="`sw_vers -productName sw_vers -productVersion`"
    export HOUDINI_BUILD_COMPILER="9.0.0.9000037"

    if [ $?prompt ]; then
	if [ "$1" != "-q" ]; then
	    echo "The Houdini ${HOUDINI_VERSION} environment has been initialized."
	fi
    fi
fi
--------------


DABMLB0606627aMG:~ 120988$ hscript -h

Usage: hbatch [-R][-e name=value][-c <command>][-j nproc][-h][-i][-q][-v][file.hip ...]

hbatch shell.  This is the non-graphical interface to a hip
file.  Type "help" for a list of commands.

Any number of .hip, .cmd, or .otl files may be specified on the
command line.  Multiple .hip files are merged together.

The -e option sets the named enviroment variable to the given
	value.  There should be no spaces around the '=' separator between
	the name and value (i.e. -e foo=bar)

The -c option will run the option argument as an hscript command, after
	the specified files have been loaded.

The -f option forces the use of asset definitions found in OTL
	files specified on the command line.

The -j option sets the HOUDINI_MAXTHREADS to the given value.
The -h option shows this message
The -q option prevents the version information from being printed
The -w option suppresses load warnings and errors from being printed
The -v option specifies verbose handling of renders
The -i option uses a simpler interface for reading input
	when running hbatch from other applications (like Pixar's
	Alfred), it may be necessary to use this option.  Use of this
	option will disable several commands (openport and atjob)
The -R option will request a non-graphics token instead
	of a graphical one.
	----------

this produces ifd files if mantra is setup and there is a camera

hscript  -R -i -c "render /out/mantra1" -c "quit"  /Volumes/dabrender/work/project_work/mattg/TESTING_Renderfarm/HoudiniProjects/houdini17_test_01/primitives_test.hipnc


            rvio cameraShape1/StillLife.####.exr  -v -fps 25
            -rthreads 4
            -outres 1280 720 -out8
            -leader simpleslate "UTS" "Artist=Anthony" "Show=Still_Life" "Shot=Testing"
            -overlay frameburn .4 1.0 30.0  -overlay matte 2.35 0.3 -overlay watermark "UTS 3D LAB" .2
            -outgamma 2.2
            -o cameraShape1_StillLife.mov
            '''
