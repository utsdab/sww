#!/usr/bin/env python2
'''
Build Interface for Arnold submission
'''

import Tkinter as tk
import ttk
import tkFileDialog
import Tkconstants
import os
import renderfarm.dabtractor as dabtractor
import render_arnold_factory as rfac
import utils_factory as utils
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)5.5s \t%(name)s \t%(message)s')
sh.setFormatter(formatter)
logger.addHandler(sh)


class WindowBase(object):
    """ Base class for all batch jobs """
    def __init__(self):
        self.spooljob = False
        self.validatejob = False
        self.master = tk.Tk()
        try:
            self.job = rfac.Job()
            logger.info("Created job definition")
        except Exception, err:
            logger.warn("Couldnt get the job definition {}".format(err))
        else:
            self.shotgun = self.job.sgtperson
            self.job.shotgunOwner = self.shotgun.shotgunname
            self.job.shotgunOwnerId = self.shotgun.shotgun_id

class Window(WindowBase):
    """ Ui Class for render submit  """
    def __init__(self):
        """ Construct the main window interface  """
        super(Window, self).__init__()
        self.msg_selectproject = 'Select your maya project'
        self.msg_selectscene = 'Select your maya scene file'
        self.msg_selectshow = 'Select your SHOW'
        self.msg_workspaceok = 'workspace.mel FOUND'
        self.msg_workspacebad = 'WARNING - no workspace.mel in your project'
        self.msg_selectSgtProject = 'Select your shotgun PROJECT'
        self.msg_selectSgtSequence = 'Now Select your  SEQUENCE'
        self.msg_selectSgtAssetType = 'Now Select your ASSET TYPE'
        self.msg_selectSgtShot = 'Now Select your  SHOT'
        self.msg_selectSgtAsset = 'Now Select your  ASSET'
        self.msg_selectSgtTask = 'Optionally Select your TASK'
        self.msg_selectSgtClass = 'ASSETS or SHOTS ?'
        self.msg_null = ""
        self.filefullpath = ""
        self.projfullpath = ""
        self.workspace = ""
        self.bgcolor0 = "light cyan"
        self.bgcolor1 = "white"
        self.bgcolor2 = "light grey"
        self.bgcolor3 = "pale green"
        self.master.configure(background=self.bgcolor1)
        self.user = os.getenv("USER")
        self.master.title("Arnold Tractor Submit: {u}".format(u=self.user))

        # ################ Options for buttons and canvas ####################
        self.button_opt = {'fill': Tkconstants.BOTH, 'padx': 5, 'pady': 5}
        self.label_opt = {'fill': Tkconstants.BOTH, 'padx': 5, 'pady': 5}

        self.canvas = tk.Canvas(self.master, height=200, width=300)
        self.canvas.pack(expand=False, fill=tk.BOTH)

        imagepath = os.path.join(os.path.dirname(dabtractor.__file__),"icons","Arnold_logo_small.gif")
        imagetk = tk.PhotoImage(file=imagepath)
        # keep a link to the image to stop the image being garbage collected
        self.canvas.img = imagetk
        tk.Label(self.canvas, image=imagetk).grid(row=0, column=0, columnspan=4,sticky=tk.NW + tk.NE)
        __row = 1

        # ###################################################################
        tk.Label(self.canvas, bg=self.bgcolor3, text="Maya ASS generation then kick").grid(row=__row, column=0, columnspan=5, sticky=tk.W + tk.E)
        __row += 1

        # ###################################################################
        tk.Label(self.canvas, bg=self.bgcolor1, text="$DABWORK").grid(row=__row, column=0, sticky=tk.E)
        self.dabworklab = tk.Label(self.canvas, text=self.job.dabwork, bg=self.bgcolor1, fg='black')
        self.dabworklab.grid(row=__row, column=1, columnspan=4, sticky=tk.W + tk.E)
        __row += 1

        # ###################################################################
        tk.Label(self.canvas, bg=self.bgcolor1,text="$TYPE").grid(row=__row, column=0, sticky=tk.E)
        self.envtype = tk.StringVar()
        # _default=self.job.config.getdefault("class", "worktype")

        self.envtype.set(self.job.config.getdefault("class", "worktype"))
        self.job.envtype=self.job.config.getdefault("class", "worktype")
        self.envtypebox = ttk.Combobox(self.canvas, textvariable=self.envtype)
        ###
        # get from the json config
        # self.job.config.getoptions("class", "worktype")
        self.envtypebox.config(values=self.job.config.getoptions("class", "worktype"), justify=tk.CENTER)
        self.envtypebox.grid(row=__row, column=1, columnspan=4,sticky=tk.W + tk.E)
        self.envtypebox.bind("<<ComboboxSelected>>", self.settype)
        __row += 1

        # ###################################################################
        tk.Label(self.canvas, bg=self.bgcolor1, text="$SHOW").grid(row=__row, column=0, sticky=tk.E)
        self.envshowbut = tk.Button(self.canvas, text=self.msg_selectshow, bg=self.bgcolor1, fg='black', command = self.setshow)
        self.envshowbut.grid(row=__row, column=1, columnspan=4, sticky=tk.W + tk.E)
        self.setshow()
        __row += 1

        # ###################################################################
        tk.Label(self.canvas, bg=self.bgcolor1, text="$PROJECT MayaProj").grid(row=__row, column=0, sticky=tk.E)
        self.envproj = tk.StringVar()
        self.envprojbut = tk.Button(self.canvas, text=self.msg_selectproject, bg=self.bgcolor1, fg='black', command=self.setproject)
        self.envprojbut.grid(row=__row, column=1, columnspan=4, sticky=tk.W + tk.E)
        __row += 1

        # ###################################################################
        self.workspacelab = tk.Label(self.canvas, bg=self.bgcolor1, text=self.msg_workspacebad, fg='black')
        self.workspacelab.grid(row=__row, column=1, columnspan=4, sticky=tk.W + tk.E)
        __row += 1

        # ###################################################################
        tk.Label(self.canvas, bg=self.bgcolor1,text="$SCENE (Maya Scene)").grid(row=__row, column=0, sticky=tk.E)
        self.envscenebut = tk.Button(self.canvas, text=self.msg_selectscene, fg='black', command=self.setscene)
        self.envscenebut.grid(row=__row, column=1, columnspan=4, sticky=tk.W + tk.E)
        __row += 1

        # # ###################################################################
        # tk.Label(self.canvas, bg=self.bgcolor3,text="Upload as new version to SHOTGUN").grid(row=__row, column=0, columnspan=4, rowspan=1, sticky=tk.W + tk.E)
        # __row += 1
        #
        # self.sgtProject = tk.StringVar()
        # self.sgtClass = tk.StringVar()
        # self.sgtShotAss = tk.StringVar()
        # self.sgtSeqAssType = tk.StringVar()
        # self.sgtTask = tk.StringVar()

        # # ########################### S H O T G U N ############################
        # _txt="Send the resulting proxy to Shotgun"
        # self.sendToShotgun = tk.IntVar()
        # self.sendToShotgun.set(1)
        # self.job.sendToShotgun = True
        # self.sendtoshotgunbut=ttk.Checkbutton(self.canvas, variable=self.sendToShotgun, command=self.setSendToShotgun)
        # self.sendtoshotgunbut.config(text=_txt)
        # self.sendtoshotgunbut.grid(row=__row,column=1,sticky=tk.W)
        # __row += 1
        #
        # # ###################################################################
        # tk.Label(self.canvas, bg=self.bgcolor1,text="SHOTGUN PROJ").grid(row=__row, column=0, sticky=tk.E)
        # self.sgtProject.set(self.msg_selectSgtProject)
        # self.sgtProjectBox = ttk.Combobox(self.canvas, textvariable=self.sgtProject)
        # self.sgtProjectBox.config(values=self.getSgtProjectValues(), justify=tk.CENTER)
        # self.sgtProjectBox.grid(row=__row, column=1, columnspan=4, sticky=tk.W + tk.E)
        # self.sgtProjectBox.bind("<<ComboboxSelected>>", self.setSgtProject)
        # __row += 1
        #
        # # ###################################################################
        # tk.Label(self.canvas, bg=self.bgcolor1,text="CLASS").grid(row=__row, column=0, sticky=tk.E)
        # self.sgtClass.set(self.msg_null)
        # self.sgtClassBox = ttk.Combobox(self.canvas, textvariable=self.sgtClass)
        # self.sgtClassBox.config(values=self.getSgtClassValues(), justify=tk.CENTER)
        # self.sgtClassBox.grid(row=__row, column=1, columnspan=4, sticky=tk.W + tk.E)
        # self.sgtClassBox.bind("<<ComboboxSelected>>", self.setSgtClass)
        # __row += 1
        #
        # # ###################################################################
        # tk.Label(self.canvas, bg=self.bgcolor1, text="SEQUENCE or ASSETTYPE").grid(row=__row, column=0, sticky=tk.E)
        # self.sgtSeqAssType.set(self.msg_null)
        # self.sgtSeqAssTypeBox = ttk.Combobox(self.canvas, textvariable=self.sgtSeqAssType)
        # self.sgtSeqAssTypeBox.config(values=self.getSgtSeqAssTypeValues(), justify=tk.CENTER)
        # self.sgtSeqAssTypeBox.grid(row=__row, column=1, columnspan=4, sticky=tk.W + tk.E)
        # self.sgtSeqAssTypeBox.bind("<<ComboboxSelected>>", self.setSgtSeqAssetType)
        # __row += 1
        #
        # # ###################################################################
        # tk.Label(self.canvas, bg=self.bgcolor1,text="SHOT or ASSET").grid(row=__row, column=0, sticky=tk.E)
        # self.sgtShotAss.set(self.msg_null)
        # self.sgtShotAssBox = ttk.Combobox(self.canvas, textvariable=self.sgtShotAss)
        # self.sgtShotAssBox.config(values=self.getSgtShotAssValues(), justify=tk.CENTER)
        # self.sgtShotAssBox.grid(row=__row, column=1, columnspan=4, sticky=tk.W + tk.E)
        # self.sgtShotAssBox.bind("<<ComboboxSelected>>", self.setSgtShotAss)
        # __row += 1
        #
        # # ###################################################################
        # tk.Label(self.canvas, bg=self.bgcolor1,text="TASK").grid(row=__row, column=0, sticky=tk.E)
        # self.sgtTask.set(self.msg_null)
        # self.sgtTaskBox = ttk.Combobox(self.canvas, textvariable=self.sgtTask)
        # self.sgtTaskBox.config(values=self.getSgtTaskValues(), justify=tk.CENTER)
        # self.sgtTaskBox.grid(row=__row, column=1, columnspan=4, sticky=tk.W + tk.E)
        # self.sgtTaskBox.bind("<<ComboboxSelected>>", self.setSgtTask)
        # __row += 1
        #
        # ########################## M A Y A ##########################
        tk.Label(self.canvas, bg=self.bgcolor3,text="Maya Generic Details").grid(row=__row, column=0, columnspan=4, rowspan=1, sticky=tk.W + tk.E)
        __row += 1

        # ###################################################################
        tk.Label(self.canvas, bg=self.bgcolor1,text="Maya Version").grid(row=__row, column=0, sticky=tk.E)
        self.mayaversion = tk.StringVar()
        self.mayaversion.set(self.job.config.getdefault("maya","version"))
        self.mayaversionbox = ttk.Combobox(self.canvas, textvariable=self.mayaversion)
        self.mayaversionbox.config(values=self.job.config.getoptions("maya","version"), justify=tk.CENTER)
        self.mayaversionbox.grid(row=__row, column=1, columnspan=4, sticky=tk.W + tk.E)
        __row += 1

        # ###################################################################
        tk.Label(self.canvas, bg=self.bgcolor1, text="Department").grid(row=__row, column=0, sticky=tk.E)
        self.departmentlab = tk.Label(self.canvas, text=self.job.department, bg=self.bgcolor1, fg='black')
        self.departmentlab.grid(row=__row, column=1, columnspan=4, sticky=tk.W + tk.E)
        __row += 1

        # ###################################################################
        tk.Label(self.canvas, bg=self.bgcolor1,text="Farm Tier").grid(row=__row, column=0, sticky=tk.E)
        self.tier = tk.StringVar()
        self.tier.set(self.job.config.getdefault("renderjob","tier"))
        self.tierbox = ttk.Combobox(self.canvas, textvariable=self.tier)
        self.tierbox.config(values=self.job.config.getoptions("renderjob","tier"), justify=tk.CENTER)
        self.tierbox.grid(row=__row, column=1, columnspan=4, sticky=tk.W + tk.E)
        __row += 1

        # ###################################################################
        tk.Label(self.canvas, bg=self.bgcolor1, text="Frame Start").grid(row=__row, column=0, sticky=tk.E)
        self.sf = tk.StringVar()
        self.sf.set("1")
        self.bar3 = tk.Entry(self.canvas, bg=self.bgcolor1,textvariable=self.sf,width=8).grid(row=__row, column=1, sticky=tk.W)

        tk.Label(self.canvas, bg=self.bgcolor1,text="Frame End").grid(row=__row, column=3, sticky=tk.W)
        self.ef = tk.StringVar()
        self.ef.set("4")
        self.bar4 = tk.Entry(self.canvas, bg=self.bgcolor1, textvariable=self.ef, width=8).grid(row=__row, column=2,sticky=tk.E)
        __row += 1
        # ###################################################################

        tk.Label(self.canvas, bg=self.bgcolor1, text="By").grid(row=__row, column=0, sticky=tk.E)
        self.bf = tk.StringVar()
        self.bf.set("1")
        self.bar5 = tk.Entry(self.canvas, bg=self.bgcolor2,textvariable=self.bf, width=8).grid(row=__row, column=1, sticky=tk.W)

        tk.Label(self.canvas, bg=self.bgcolor1,text="Resolution").grid(row=__row, column=0, sticky=tk.E)
        self.resolution = tk.StringVar()
        self.resolution.set(self.job.config.getdefault("render", "resolution"))
        self.resolutionbox = ttk.Combobox(self.canvas, textvariable=self.resolution)
        self.resolutionbox.config(values=self.job.config.getoptions("render", "resolution"), justify=tk.CENTER)
        self.resolutionbox.grid(row=__row, column=1, columnspan=4, sticky=tk.W + tk.E)
        __row += 1

        # ############################ D E T A I L S ##########################
        tk.Label(self.canvas, bg=self.bgcolor3,text="Renderer Specific Details").grid(row=__row,column=0, columnspan=4,sticky=tk.W + tk.E)
        __row += 1

        # # ###################################################################
        # tk.Label(self.canvas, bg=self.bgcolor1,text="Arnold Version").grid(row=__row, column=0, sticky=tk.E)
        # self.rendermanversion = tk.StringVar()
        # self.rendermanversion.set(self.job.config.getdefault("arnold","version"))
        # self.rendermanversionbox = ttk.Combobox(self.canvas, textvariable=self.rendermanversion)
        # self.rendermanversionbox.config(values=self.job.config.getoptions("arnold","version"), justify=tk.CENTER)
        # self.rendermanversionbox.grid(row=__row, column=1, columnspan=4, sticky=tk.W + tk.E)
        # __row += 1

        # # ###################################################################
        # tk.Label(self.canvas, bg=self.bgcolor1,text="Intergrator").grid(row=__row, column=0, sticky=tk.E)
        # self.integrator = tk.StringVar()
        # self.integrator.set(self.job.config.getdefault("renderman","integrator"))
        # self.integratorbox = ttk.Combobox(self.canvas, textvariable=self.integrator)
        # self.integratorbox.config(values=self.job.config.getoptions("renderman","integrator"), justify=tk.CENTER)
        # self.integratorbox.grid(row=__row, column=1, columnspan=4, sticky=tk.W + tk.E)
        # __row += 1

        # ###################################################################
        tk.Label(self.canvas, bg=self.bgcolor1,text="Max Samples").grid(row=__row, column=0, sticky=tk.E)
        self.maxsamples = tk.StringVar()
        self.maxsamples.set(self.job.config.getdefault("render","maxsamples"))
        self.maxsamplesbox = ttk.Combobox(self.canvas, textvariable=self.maxsamples)
        self.maxsamplesbox.config(values=self.job.config.getoptions("render","maxsamples"), justify=tk.CENTER)
        self.maxsamplesbox.grid(row=__row, column=1, columnspan=4, sticky=tk.W + tk.E)
        __row += 1

        # ###################################################################
        tk.Label(self.canvas, bg=self.bgcolor1,text="Render Threads").grid(row=__row, column=0, sticky=tk.E)
        self.threads = tk.StringVar()
        self.threads.set(self.job.config.getdefault("render","threads"))
        self.threadsbox = ttk.Combobox(self.canvas, textvariable=self.threads)
        self.threadsbox.config(values=self.job.config.getoptions("render","threads"), justify=tk.CENTER)
        self.threadsbox.grid(row=__row, column=1, columnspan=4, sticky=tk.W + tk.E)
        __row += 1

        # ###################################################################
        tk.Label(self.canvas, bg=self.bgcolor1,text="Render Memory").grid(row=__row, column=0, sticky=tk.E)
        self.memory = tk.StringVar()
        self.memory.set(self.job.config.getdefault("render","memory"))
        self.memorybox = ttk.Combobox(self.canvas, textvariable=self.memory)
        self.memorybox.config(values=self.job.config.getoptions("render","memory"), justify=tk.CENTER)
        self.memorybox.grid(row=__row, column=1, columnspan=4, sticky=tk.W + tk.E)
        __row += 1

        # ###################################################################
        tk.Label(self.canvas, bg=self.bgcolor1,text="Render Chunks").grid(row=__row, column=0, sticky=tk.E)
        self.chunks = tk.StringVar()
        self.chunks.set(self.job.config.getdefault("render","chunks"))
        self.chunksbox = ttk.Combobox(self.canvas, textvariable=self.chunks)
        self.chunksbox.config(values=self.job.config.getoptions("render","chunks"), justify=tk.CENTER)
        self.chunksbox.grid(row=__row, column=1, columnspan=4, sticky=tk.W + tk.E)
        __row += 1

        # # ###################################################################
        # _txt="Dont Re-Render Existing Frames"
        # self.skipframes = tk.IntVar()
        # self.skipframes.set(1)
        # tk.Checkbutton(self.canvas, bg=self.bgcolor1, text=_txt, variable=self.skipframes).grid(row=__row, column=1,sticky=tk.W)
        # __row += 1

        # ###################################################################
        tk.Label(self.canvas, bg=self.bgcolor1, text="Other Options").grid(row=__row, column=0)
        self.options = tk.StringVar()
        self.options.set("")
        self.bar7 = tk.Entry(self.canvas, bg=self.bgcolor2, textvariable=self.options, width=40).grid(row=__row,column=1, columnspan=4,sticky=tk.W + tk.E)
        __row += 1

        # # ###################################################################
        # tk.Label(self.canvas, bg=self.bgcolor3,text="Make Proxy").grid(row=__row,column=0,columnspan=4,sticky=tk.W + tk.E)
        # __row += 1

        # # ########################### P R O X Y ############################
        # _txt="Make Movie from Finished Frames"
        # self.makeproxy = tk.IntVar()
        # self.makeproxy.set(1)
        # tk.Checkbutton(self.canvas, bg=self.bgcolor1, text=_txt, variable=self.makeproxy).grid(row=__row, column=1,sticky=tk.W)
        # __row += 1

        # # ########################### N O T I F I C A T I O N S #############
        # _txt="Tractor Notifications"
        # tk.Label(self.canvas, bg=self.bgcolor3, text=_txt).grid(row=__row,column=0,columnspan=4,sticky=tk.W + tk.E)
        # __row += 1
        #
        # # ###################################################################
        # self.emailjobstart = tk.IntVar()
        # self.emailjobstart.set(1)
        # self.emailjobstartbut=tk.Checkbutton(self.canvas, variable=self.emailjobstart, bg=self.bgcolor1, text="Job Start").grid(row=__row, column=1,sticky=tk.W)
        #
        #
        # self.emailjobend = tk.IntVar()
        # self.emailjobend.set(1)
        # self.emailjobendbut=tk.Checkbutton(self.canvas, variable=self.emailjobend, bg=self.bgcolor1,text="Job End").grid(row=__row, column=2, sticky=tk.W)
        # __row += 1

        # # ###################################################################
        # self.emailtaskend = tk.IntVar()
        # self.emailtaskend.set(0)
        # self.emailtaskendbut=tk.Checkbutton(self.canvas, variable=self.emailtaskend, bg=self.bgcolor1, text="Each Frame End").grid(row=__row, column=1, sticky=tk.W)
        # __row += 1
        #
        # # ###################################################################
        # tk.Label(self.canvas, bg=self.bgcolor3, text="Submit Job To Tractor").grid(row=__row, column=0, columnspan=4, sticky=tk.W + tk.E)
        # __row += 1

        # ###################################################################
        # tk.Buttons
        self.cbutton = tk.Button(self.canvas, bg=self.bgcolor1,text='SUBMIT', command=lambda: self.submit())
        self.cbutton.grid(row=__row, column=3, sticky=tk.W + tk.E)
        self.vbutton = tk.Button(self.canvas, bg=self.bgcolor1,text='VALIDATE', command=lambda: self.validate())
        self.vbutton.grid(row=__row, column=1, columnspan=2, sticky=tk.W + tk.E)
        self.vbutton = tk.Button(self.canvas, bg=self.bgcolor1, text='CANCEL', command=lambda: self.cancel())
        self.vbutton.grid(row=__row, column=0, sticky=tk.W + tk.E)

        self.master.mainloop()


    # ############################################################
    def setSendToShotgun(self):
        logger.debug("Run: {}".format("setSendToShotgun"))
        if  not self.sendToShotgun.get():
            self.sgtProjectBox.set(self.msg_null)
            self.sgtSeqAssType.set(self.msg_null)
            self.sgtShotAss.set(self.msg_null)
            self.sgtTask.set(self.msg_null)
            self.sgtClass.set(self.msg_null)
            self.sgtProjectBox.config(values=[], justify=tk.CENTER)
            self.sgtSeqAssTypeBox.configure(values=[], justify=tk.CENTER)
            self.sgtShotAssBox.config(values=[], justify=tk.CENTER)
            self.sgtTaskBox.config(values=[],justify=tk.CENTER)
            self.job.sendToShotgun = False
            #set widget off too!
        else:
            self.sgtProjectBox.set(self.msg_selectSgtProject)
            self.sgtSeqAssType.set(self.msg_null)
            self.sgtShotAss.set(self.msg_null)
            self.sgtTask.set(self.msg_null)
            self.sgtProjectBox.config(values=self.getSgtProjectValues(), justify=tk.CENTER)
            self.job.sendToShotgun = True


    def getSgtProjectValues(self):
        logger.debug("Run: {}".format("getSgtProjectValues"))
        _ret = self.shotgun.myProjects().keys()
        _ret.sort()
        return _ret

    def setSgtProject(self, entity):
        logger.debug("Run: {}".format("setSgtProject"))
        try:
            self.sgtClass.set(self.msg_selectSgtClass)
            self.sgtShotAss.set(self.msg_null)
            self.sgtSeqAssType.set(self.msg_null)
            self.sgtTask.set(self.msg_null)
        except:
            pass

        self.job.shotgunProject = self.sgtProject.get()
        self.job.shotgunProjectId = self.shotgun.myProjects().get(self.job.shotgunProject)
        logger.info("Shotgun Project is {} id {}".format( self.job.shotgunProject, self.job.shotgunProjectId))
        self.getSgtClassValues()

    def getSgtClassValues(self):
        logger.debug("Run: {}".format("getSgtClassValues"))
        _ret = ["ASSETS", "SHOTS"]
        _ret.sort()
        return _ret

    def setSgtClass(self, event):
        logger.debug("Run: {}".format("setSgtClass"))
        # Just bind the virtual event <<ComboboxSelected>> to the Combobox widget
        self.job.shotgunClass = self.sgtClass.get()
        if self.job.shotgunClass == "ASSETS":
            self.sgtSeqAssType.set(self.msg_selectSgtAssetType)
            self.sgtShotAss.set(self.msg_null)
            self.sgtTask.set(self.msg_null)
        elif self.job.shotgunClass == "SHOTS":
            self.sgtSeqAssType.set(self.msg_selectSgtSequence)
            self.sgtShotAss.set(self.msg_null)
            self.sgtTask.set(self.msg_null)
        else:
            self.sgtClass.set(self.msg_selectSgtClass)

        logger.info("Shotgun Class is {}".format(self.job.shotgunClass))
        self.getSgtSeqAssTypeValues()


    def getSgtSeqAssTypeValues(self):
        logger.debug("Run: {}".format("getSgtSeqAssTypeValues"))
        _ret = []
        try:
            self.sgtTask.set(self.msg_null)
            self.sgtTaskBox.config(values=[], justify=tk.CENTER)
        except:
            pass

        if self.sgtClass.get() == "SHOTS":
            _ret = self.job.sgtproject.seqFromProject(self.job.shotgunProjectId).keys()

        elif self.sgtClass.get() == "ASSETS":
            # just get ones for the asset type
            _ret = self.job.sgtproject.assettypes(self.job.shotgunProjectId)

        _ret.sort()
        self.sgtSeqAssTypeBox.configure(values=_ret, justify=tk.CENTER)

    def setSgtSeqAssetType(self, entity):
        logger.debug("Run: {}".format("setSgtSeqAssetType"))
        try:
            self.sgtTask.set(self.msg_null)
            self.sgtTaskBox.config(values=[],justify=tk.CENTER)
        except:
            pass

        if self.job.shotgunClass == 'ASSETS':
            self.sgtShotAss.set(self.msg_selectSgtAsset)
            self.job.shotgunSeqAssetType = self.sgtSeqAssType.get()
            self.job.shotgunSeqAssetTypeId = None

        elif self.job.shotgunClass == 'SHOTS':
            self.sgtShotAss.set(self.msg_selectSgtShot)
            self.job.shotgunSeqAssetType = self.sgtSeqAssType.get()
            _seqs = self.job.sgtproject.seqFromProject(self.job.shotgunProjectId)
            self.job.shotgunSeqAssetTypeId = _seqs.get(self.job.shotgunSeqAssetType)
        else:
            self.sgtShotAss.set(self.msg_null)

        logger.info("Shotgun Seq/Ass is {} id {}".format(self.job.shotgunSeqAssetType, self.job.shotgunSeqAssetTypeId))
        self.getSgtShotAssValues()


    def getSgtShotAssValues(self):
        logger.debug("Run: {}".format("getSgtShotAssValues"))
        _ret = []
        if self.job.shotgunClass == 'SHOTS':
            try:
                _ret = self.job.sgtproject.shotFromSeq(self.job.shotgunProjectId,self.job.shotgunSeqAssetTypeId).keys()
            except RuntimeError:
                print "boing"
        elif self.job.shotgunClass == 'ASSETS':
            try:
                _ret = self.job.sgtproject.assetFromAssetType(self.job.shotgunProjectId, self.job.shotgunSeqAssetTypeId).keys()
            except RuntimeError:
                print "bam"
        _ret.sort()
        self.sgtShotAssBox.configure(values=_ret, justify=tk.CENTER)

    def setSgtShotAss(self, entity):
        logger.debug("Run: {}".format("setSgtShotAss"))
        try:
            self.sgtTask.set(self.msg_null)
            self.sgtTaskBox.config(values=[],justify=tk.CENTER)
        except:
            pass

        if not self.job.shotgunProjectId:
            try:
                self.sgtShotAss.set(self.msg_null)
                self.sgtTask.set(self.msg_null)
            except:
                pass
        else:
            if self.job.shotgunClass == 'SHOTS':
                self.job.shotgunShotAsset = self.sgtShotAss.get()
                _shots = self.job.sgtproject.shotFromSeq(self.job.shotgunProjectId,self.job.shotgunSeqAssetTypeId)
                self.job.shotgunShotAssetId = _shots.get(self.job.shotgunShotAsset)
            elif self.job.shotgunClass == 'ASSETS':
                self.job.shotgunShotAsset = self.sgtShotAss.get()
                _ass = self.job.sgtproject.assetFromAssetType(self.job.shotgunProjectId, self.job.shotgunSeqAssetTypeId)
                self.job.shotgunShotAssetId = _ass.get(self.job.shotgunShotAsset)
        logger.info("Shotgun Shot/Asset is {} id {}".format(self.job.shotgunShotAsset, self.job.shotgunShotAssetId))
        self.getSgtTaskValues()

    def getSgtTaskValues(self):
        logger.debug("Run: {}".format("getSgtTaskValues"))
        _ret = []
        if not self.job.shotgunShotAssetId:
            self.sgtTask.set(self.msg_null)
            self.sgtTaskBox.config(values=[],justify=tk.CENTER)
        elif self.job.shotgunClass == 'SHOTS':
            _ret=self.job.sgtproject.taskFromShot(self.job.shotgunProjectId, self.job.shotgunShotAssetId).keys()
            _ret.sort()
            self.sgtTaskBox.configure(values=_ret, justify=tk.CENTER)
            # self.job.shotgunTaskId = _ret.get(self.job.shotgunTask)
        elif self.job.shotgunClass == 'ASSETS':
            _ret=self.job.sgtproject.taskFromAsset(self.job.shotgunProjectId, self.job.shotgunShotAssetId).keys()
            _ret.sort()
            self.sgtTaskBox.configure(values=_ret, justify=tk.CENTER)
            # self.job.shotgunTaskId = _ret.get(self.job.shotgunTask)

    def setSgtTask(self, entity):
        logger.debug("Run: {}".format("setSgtTask"))
        if not self.job.shotgunShotAssetId:
            self.sgtTask.set(self.msg_selectSgtTask)
        else:
            self.job.shotgunTask = self.sgtTask.get()
            _tasks = self.job.sgtproject.taskFromShot(self.job.shotgunProjectId, self.job.shotgunShotAssetId)
            self.job.shotgunTaskId = _tasks.get(self.job.shotgunTask)
            logger.info("Shotgun Task is {} id {}".format( self.job.shotgunTask, self.job.shotgunTaskId))


    def setscene(self):
        self.filefullpath = tkFileDialog.askopenfilename(\
            parent=self.master,initialdir=self.projfullpath,title=self.msg_selectscene,
            filetypes=[('maya ascii', '.ma'),('maya binary', '.mb')]) # filename not filehandle

        _projfullpath=os.path.join(self.job.dabwork,self.job.envtype,self.job.envshow,self.job.envproject)
        _scenerelpath=os.path.relpath(self.filefullpath,_projfullpath)

        self.envscenebut["text"] = str(_scenerelpath) if self.filefullpath else self.msg_selectscene
        self.job.envscene=_scenerelpath

    def settype(self,event):
        # Just bind the virtual event <<ComboboxSelected>> to the Combobox widget
        self.job.envtype=self.envtype.get()
        self.workspacelab["text"] = self.msg_workspacebad
        self.workspacelab["bg"] = self.bgcolor1

        if self.job.envtype == "user_work":
            self.job.envshow=self.job.username
            self.envshowbut["text"]=self.job.envshow
        elif self.job.envtype == "project_work":
            self.job.envshow=None
            self.envshowbut["text"]= self.msg_selectshow
        elif self.job.envtype == "shotgun_work":
            self.job.envshow=None
            self.envshowbut["text"]= self.msg_selectshow

        self.envprojbut["text"]= self.msg_selectproject
        self.job.envproject=None
        self.envscenebut["text"]= self.msg_selectscene
        self.job.envscene=None

    def setshow(self):
        __initialdir=self.job.dabwork
        if self.job.envtype == "user_work":
            self.job.envshow=self.job.username
            self.envshowbut["text"]=self.job.envshow
        elif self.job.envtype == "project_work":
            self.envshowfullpath = tkFileDialog.askdirectory(parent=self.master, initialdir=os.path.join(self.job.dabwork,"project_work"),title=self.msg_selectshow)
            _typefullpath = os.path.join(self.job.dabwork,self.job.envtype)
            _showrelpath=os.path.relpath(self.envshowfullpath,_typefullpath)

            if os.path.exists(self.envshowfullpath):
                self.envshowbut["text"] = str(_showrelpath) if self.envshowfullpath else self.msg_selectshow
                self.job.envshow=_showrelpath
            else:
                self.job.envtype=self.envtype.get()
                self.job.envproject=None
                self.job.envshow=None
                self.job.envscene=None

        elif self.job.envtype == "shotgun_work":
            self.envshowfullpath = tkFileDialog.askdirectory(parent=self.master, initialdir=os.path.join(self.job.dabwork,"shotgun_work"),title=self.msg_selectshow)
            _typefullpath = os.path.join(self.job.dabwork,self.job.envtype)
            _showrelpath=os.path.relpath(self.envshowfullpath,_typefullpath)

            if os.path.exists(self.envshowfullpath):
                self.envshowbut["text"] = str(_showrelpath) if self.envshowfullpath else self.msg_selectshow
                self.job.envshow=_showrelpath
            else:
                self.job.envtype=self.envtype.get()
                self.job.envproject=None
                self.job.envshow=None
                self.job.envscene=None

    def setproject(self):
        __initialdir=os.path.join(self.job.dabwork,self.job.envtype,self.job.envshow)
        self.projfullpath = tkFileDialog.askdirectory(parent=self.master, initialdir=__initialdir, title=self.msg_selectproject)
        _typefullpath = os.path.join(self.job.dabwork,self.job.envtype,self.job.envshow)
        _projectrelpath=os.path.relpath(self.projfullpath,_typefullpath)

        _possible = "%s/workspace.mel" % self.projfullpath
        # print _possible
        if os.path.exists(_possible):
            # print "ok"
            self.envprojbut["text"] = str(_projectrelpath)  #if self.projfullpath else self.msg_selectproject
            self.workspacelab["text"] = self.msg_workspaceok
            self.workspacelab["bg"] = self.bgcolor3
            self.job.envproject=_projectrelpath
        else:
            # print "not ok"
            self.workspacelab["text"] = self.msg_workspacebad
            self.workspacelab["bg"] = self.bgcolor1
            self.envprojbut["text"] = self.msg_selectproject
            self.envscenebut["text"] = self.msg_selectscene

            self.job.envproject=None
            self.job.envscene=None

    def consolidate(self):
        try:
            _checkpath=utils.hasBadNaming(self.filefullpath)
            print _checkpath
        except Exception, err:
            logger.critical("Problem validating filepath {} : {}".format(self.filefullpath, err))
        else:
            if _checkpath:
                logger.critical("Problem with naming {}".format(_checkpath))
        try:
            self.job.mayaprojectfullpath=self.projfullpath
            self.job.mayascenefullpath=self.filefullpath
            # self.job.optionskipframe=self.skipframes.get()  # gets from the tk object
            # self.job.optionmakeproxy=self.makeproxy.get()
            self.job.optionresolution=self.resolution.get()
            # self.job.optionsendjobstartemail=self.emailjobstart.get()
            # self.job.optionsendjobendemail=self.emailjobend.get()
            # self.job.optionsendtaskendemail=self.emailtaskend.get()
            self.job.optionmaxsamples=self.maxsamples.get()  # gets from the tk object
            self.job.farmtier=self.tier.get()
            self.job.jobthreads=self.threads.get()
            self.job.jobstartframe=self.sf.get()
            self.job.jobendframe=self.ef.get()
            self.job.jobbyframe=self.bf.get()
            self.job.jobthreadmemory=self.memory.get()
            self.job.jobchunks=self.chunks.get()
            self.job.mayaversion=self.mayaversion.get()
            # self.job.renderversion=self.renderversion.get()
        except Exception,err:
            logger.warn("Pass Data {}".format(err))

    def validate(self):
        try:
            logger.info("Validate")
            logger.info("Project: %s" % self.projfullpath)
            logger.info("SceneFile: %s" % self.filefullpath)
            logger.info("Start: %s" % self.sf.get())
            logger.info("End: %s" % self.ef.get())
            logger.info("By: %s" % self.bf.get())
            # logger.info("Skip Existing Frames: %s" % self.skipframes)
            # logger.info("Make Proxy: %s" % self.makeproxy)
            self.consolidate()
            rj=rfac.Render(self.job)
            rj.build()
            rj.validate()

        except Exception, validateError:
            logger.warn("Problem validating farm sumbission {}".format(validateError))

    def submit(self):
        try:
            self.consolidate()
            self.master.destroy()
            rj=rfac.Render(self.job)
            rj.build()
            rj.validate()
            rj.spool()

        except Exception, submiterror:
            logger.warn("Problem submitting to farm {}".format(submiterror))

    def cancel(self):
        logger.info("Cancelled")
        self.master.destroy()



if __name__ == "__main__":
    w=Window()
    # for key in w.job.__dict__.keys():
    #     print "{:20} = {}".format(key,w.job.__dict__.get(key))



