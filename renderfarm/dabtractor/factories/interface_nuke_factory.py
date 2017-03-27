#!/usr/bin/env rmanpy

# TODO move this into a tabbed single interface
# TODO handle layers
# TODO handle integrators
# TODO handle ribgen only


###############################################################
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)5.5s \t%(name)s \t%(message)s')
sh.setFormatter(formatter)
logger.addHandler(sh)
###############################################################

import Tkinter as tk
import ttk
import tkFileDialog
import Tkconstants
import os
import sys
import sww.renderfarm.dabtractor as dabtractor
import sww.renderfarm.dabtractor.factories.environment_factory as envfac
import sww.renderfarm.dabtractor.factories.render_nuke_factory as rfac


class WindowBase(object):
    """ Base class for all batch jobs """
    def __init__(self):
        self.spooljob = False
        self.validatejob = False
        self.master = tk.Tk()
        self.job=rfac.Job()


class Window(WindowBase):
    """ Ui Class for render submit  """
    def __init__(self):
        """ Construct the main window interface  """
        super(Window, self).__init__()
        self.msg_selectproject = 'Select your project'
        self.msg_selectscene = 'Select your nuke script file'
        self.msg_selectshow = 'Select your SHOW'
        self.msg_workspaceok = 'workspace.mel FOUND'
        # self.msg_workspacebad = 'WARNING - no workspace.mel in your project'
        self.filefullpath = ""
        self.projfullpath = ""
        self.workspace = ""
        self.bgcolor0 = "light cyan"
        self.bgcolor1 = "white"
        self.bgcolor2 = "light grey"
        self.bgcolor3 = "pale green"
        self.master.configure(background=self.bgcolor1)
        self.user = os.getenv("USER")
        self.master.title("Nuke Tractor Submit: {u}".format(u=self.user))

        # ################ Options for buttons and canvas ####################
        self.button_opt = {'fill': Tkconstants.BOTH, 'padx': 5, 'pady': 5}
        self.label_opt = {'fill': Tkconstants.BOTH, 'padx': 5, 'pady': 5}
        self.canvas = tk.Canvas(self.master, height=200, width=300)
        self.canvas.pack(expand=True, fill=tk.BOTH)

        imagepath = os.path.join(os.path.dirname(dabtractor.__file__),"icons","Nuke_logo.gif")
        imagetk = tk.PhotoImage(file=imagepath)
        # keep a link to the image to stop the image being garbage collected
        self.canvas.img = imagetk
        tk.Label(self.canvas, image=imagetk).grid(row=0, column=0, columnspan=4,sticky=tk.NW + tk.NE)
        __row = 1

        # ###################################################################
        tk.Label(self.canvas, bg=self.bgcolor3, text="Nuke Batch Render").grid(row=__row, column=0, columnspan=5, sticky=tk.W + tk.E)
        __row += 1

        # ###################################################################
        tk.Label(self.canvas, bg=self.bgcolor1, text="$DABWORK").grid(row=__row, column=0, sticky=tk.E)
        self.dabworklab = tk.Label(self.canvas, text=self.job.dabwork, bg=self.bgcolor1, fg='black')
        self.dabworklab.grid(row=__row, column=1, columnspan=4, sticky=tk.W + tk.E)
        __row += 1

        # ###################################################################
        tk.Label(self.canvas, bg=self.bgcolor1,text="$TYPE").grid(row=__row, column=0, sticky=tk.E)
        self.envtype = tk.StringVar()
        self.envtype.set("user_work")
        self.job.envtype="user_work"
        self.envtypebox = ttk.Combobox(self.canvas, textvariable=self.envtype)
        self.envtypebox.config(values=["user_work","project_work"], justify=tk.CENTER)
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
        tk.Label(self.canvas, bg=self.bgcolor1, text="$PROJECT").grid(row=__row, column=0, sticky=tk.E)
        self.envproj = tk.StringVar()
        self.envprojbut = tk.Button(self.canvas, text=self.msg_selectproject, bg=self.bgcolor1, fg='black', command=self.setproject)
        self.envprojbut.grid(row=__row, column=1, columnspan=4, sticky=tk.W + tk.E)
        __row += 1

        # ###################################################################
        tk.Label(self.canvas, bg=self.bgcolor1,text="$SCENE (Nuke Script)").grid(row=__row, column=0, sticky=tk.E)
        self.envscenebut = tk.Button(self.canvas, text=self.msg_selectscene, fg='black', command=self.setscene)
        self.envscenebut.grid(row=__row, column=1, columnspan=4, sticky=tk.W + tk.E)
        __row += 1

        # ###################################################################
        tk.Label(self.canvas, bg=self.bgcolor3,text="Nuke Generic Details").grid(row=__row, column=0, columnspan=4, rowspan=1, sticky=tk.W + tk.E)
        __row += 1

        # ###################################################################
        tk.Label(self.canvas, bg=self.bgcolor1,text="Nuke Version").grid(row=__row, column=0, sticky=tk.E)
        self.nukeversion = tk.StringVar()
        self.nukeversion.set(self.job.env.getdefault("nuke","version"))
        self.nukeversionbox = ttk.Combobox(self.canvas, textvariable=self.nukeversion)
        self.nukeversionbox.config(values=self.job.env.getoptions("nuke","version"), justify=tk.CENTER)
        self.nukeversionbox.grid(row=__row, column=1, columnspan=4, sticky=tk.W + tk.E)
        __row += 1

        # ###################################################################
        tk.Label(self.canvas, bg=self.bgcolor1, text="Department").grid(row=__row, column=0, sticky=tk.E)
        self.departmentlab = tk.Label(self.canvas, text=self.job.department, bg=self.bgcolor1, fg='black')
        self.departmentlab.grid(row=__row, column=1, columnspan=4, sticky=tk.W + tk.E)
        __row += 1

        # ###################################################################
        tk.Label(self.canvas, bg=self.bgcolor1,text="Farm Tier").grid(row=__row, column=0, sticky=tk.E)
        self.tier = tk.StringVar()
        self.tier.set(self.job.env.getdefault("renderjob","tier"))
        self.tierbox = ttk.Combobox(self.canvas, textvariable=self.tier)
        self.tierbox.config(values=self.job.env.getoptions("renderjob","tier"), justify=tk.CENTER)
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
        self.resolution.set(self.job.env.getdefault("render", "resolution"))
        self.resolutionbox = ttk.Combobox(self.canvas, textvariable=self.resolution)
        self.resolutionbox.config(values=self.job.env.getoptions("render", "resolution"), justify=tk.CENTER)
        self.resolutionbox.grid(row=__row, column=1, columnspan=4, sticky=tk.W + tk.E)
        __row += 1

        # ###################################################################
        tk.Label(self.canvas, bg=self.bgcolor3,text="Renderer Specific Details").grid(row=__row,column=0, columnspan=4,sticky=tk.W + tk.E)
        __row += 1

        # ###################################################################
        # tk.Label(self.canvas, bg=self.bgcolor1,text="Renderman Version").grid(row=__row, column=0, sticky=tk.E)
        # self.rendermanversion = tk.StringVar()
        # self.rendermanversion.set(self.job.env.getdefault("renderman","version"))
        # self.rendermanversionbox = ttk.Combobox(self.canvas, textvariable=self.rendermanversion)
        # self.rendermanversionbox.config(values=self.job.env.getoptions("renderman","version"), justify=tk.CENTER)
        # self.rendermanversionbox.grid(row=__row, column=1, columnspan=4, sticky=tk.W + tk.E)
        # __row += 1

        # ###################################################################
        # tk.Label(self.canvas, bg=self.bgcolor1,text="Intergrator").grid(row=__row, column=0, sticky=tk.E)
        # self.integrator = tk.StringVar()
        # self.integrator.set(self.job.env.getdefault("renderman","integrator"))
        # self.integratorbox = ttk.Combobox(self.canvas, textvariable=self.integrator)
        # self.integratorbox.config(values=self.job.env.getoptions("renderman","integrator"), justify=tk.CENTER)
        # self.integratorbox.grid(row=__row, column=1, columnspan=4, sticky=tk.W + tk.E)
        # __row += 1

        # ###################################################################
        # tk.Label(self.canvas, bg=self.bgcolor1,text="Max Samples").grid(row=__row, column=0, sticky=tk.E)
        # self.maxsamples = tk.StringVar()
        # self.maxsamples.set(self.job.env.getdefault("render","maxsamples"))
        # self.maxsamplesbox = ttk.Combobox(self.canvas, textvariable=self.maxsamples)
        # self.maxsamplesbox.config(values=self.job.env.getoptions("render","maxsamples"), justify=tk.CENTER)
        # self.maxsamplesbox.grid(row=__row, column=1, columnspan=4, sticky=tk.W + tk.E)
        # __row += 1

        # ###################################################################
        tk.Label(self.canvas, bg=self.bgcolor1,text="Render Threads").grid(row=__row, column=0, sticky=tk.E)
        self.threads = tk.StringVar()
        self.threads.set(self.job.env.getdefault("render","threads"))
        self.threadsbox = ttk.Combobox(self.canvas, textvariable=self.threads)
        self.threadsbox.config(values=self.job.env.getoptions("render","threads"), justify=tk.CENTER)
        self.threadsbox.grid(row=__row, column=1, columnspan=4, sticky=tk.W + tk.E)
        __row += 1

        # ###################################################################
        tk.Label(self.canvas, bg=self.bgcolor1,text="Render Memory").grid(row=__row, column=0, sticky=tk.E)
        self.memory = tk.StringVar()
        self.memory.set(self.job.env.getdefault("render","memory"))
        self.memorybox = ttk.Combobox(self.canvas, textvariable=self.memory)
        self.memorybox.config(values=self.job.env.getoptions("render","memory"), justify=tk.CENTER)
        self.memorybox.grid(row=__row, column=1, columnspan=4, sticky=tk.W + tk.E)
        __row += 1

        # ###################################################################
        tk.Label(self.canvas, bg=self.bgcolor1,text="Render Chunks").grid(row=__row, column=0, sticky=tk.E)
        self.chunks = tk.StringVar()
        self.chunks.set(self.job.env.getdefault("render","chunks"))
        self.chunksbox = ttk.Combobox(self.canvas, textvariable=self.chunks)
        self.chunksbox.config(values=self.job.env.getoptions("render","chunks"), justify=tk.CENTER)
        self.chunksbox.grid(row=__row, column=1, columnspan=4, sticky=tk.W + tk.E)
        __row += 1

        # ###################################################################
        _txt="Dont Re-Render Existing Frames"
        self.skipframes = tk.IntVar()
        self.skipframes.set(1)
        tk.Checkbutton(self.canvas, bg=self.bgcolor1, text=_txt, variable=self.skipframes).grid(row=__row, column=1,sticky=tk.W)
        __row += 1

        # ###################################################################
        tk.Label(self.canvas, bg=self.bgcolor1, text="Other Options").grid(row=__row, column=0)
        self.options = tk.StringVar()
        self.options.set("")
        self.optionsbar = tk.Entry(self.canvas, bg=self.bgcolor2, textvariable=self.options, width=40).grid(row=__row,column=1, columnspan=4,sticky=tk.W + tk.E)
        __row += 1

        # ###################################################################
        tk.Label(self.canvas, bg=self.bgcolor3,text="Make Proxy").grid(row=__row,column=0,columnspan=4,sticky=tk.W + tk.E)
        __row += 1

        # ###################################################################
        _txt="Make Movie from Finished Frames"
        self.makeproxy = tk.IntVar()
        self.makeproxy.set(1)
        tk.Checkbutton(self.canvas, bg=self.bgcolor1, text=_txt, variable=self.makeproxy).grid(row=__row, column=1,sticky=tk.W)
        __row += 1

        # ###################################################################
        _txt="Tractor Notifications"
        tk.Label(self.canvas, bg=self.bgcolor3, text=_txt).grid(row=__row,column=0,columnspan=4,sticky=tk.W + tk.E)
        __row += 1

        # ###################################################################
        self.emailjobstart = tk.IntVar()
        self.emailjobstart.set(1)
        self.emailjobstartbut=tk.Checkbutton(self.canvas, variable=self.emailjobstart, bg=self.bgcolor1, text="Job Start").grid(row=__row, column=1,sticky=tk.W)


        self.emailjobend = tk.IntVar()
        self.emailjobend.set(1)
        self.emailjobendbut=tk.Checkbutton(self.canvas, variable=self.emailjobend, bg=self.bgcolor1,text="Job End").grid(row=__row, column=2, sticky=tk.W)
        __row += 1

        # ###################################################################
        self.emailtaskend = tk.IntVar()
        self.emailtaskend.set(0)
        self.emailtaskendbut=tk.Checkbutton(self.canvas, variable=self.emailtaskend, bg=self.bgcolor1, text="Each Frame End").grid(row=__row, column=1, sticky=tk.W)
        __row += 1

        # ###################################################################
        tk.Label(self.canvas, bg=self.bgcolor3, text="Submit Job To Tractor").grid(\
            row=__row, column=0, columnspan=4, sticky=tk.W + tk.E)
        __row += 1

        # ###################################################################
        # tk.Buttons
        self.cbutton = tk.Button(self.canvas, bg=self.bgcolor1,text='SUBMIT', command=lambda: self.submit())
        self.cbutton.grid(row=__row, column=3, sticky=tk.W + tk.E)
        self.vbutton = tk.Button(self.canvas, bg=self.bgcolor1,text='VALIDATE', command=lambda: self.validate())
        self.vbutton.grid(row=__row, column=1, columnspan=2, sticky=tk.W + tk.E)
        self.vbutton = tk.Button(self.canvas, bg=self.bgcolor1, text='CANCEL', command=lambda: self.cancel())
        self.vbutton.grid(row=__row, column=0, sticky=tk.W + tk.E)

        self.master.mainloop()


    def setscene(self):
        self.filefullpath = tkFileDialog.askopenfilename(\
            parent=self.master,initialdir=self.projfullpath,title=self.msg_selectscene,
            filetypes=[('nuke script', '.nk')]) # filename not filehandle

        _projfullpath=os.path.join(self.job.dabwork,self.job.envtype,self.job.envshow,self.job.envproject)
        _scenerelpath=os.path.relpath(self.filefullpath,_projfullpath)

        self.envscenebut["text"] = str(_scenerelpath) if self.filefullpath else self.msg_selectscene
        self.job.envscene=_scenerelpath

    def settype(self,event):
        # Just bind the virtual event <<ComboboxSelected>> to the Combobox widget
        self.job.envtype=self.envtype.get()

        if self.job.envtype == "user_work":
            self.job.envshow=self.job.username
            self.envshowbut["text"]=self.job.envshow
        elif self.job.envtype == "project_work":
            self.job.envshow=None
            self.envshowbut["text"]= self.msg_selectshow

        self.envprojbut["text"]= self.msg_selectproject
        self.job.envproject=None
        self.envscenebut["text"]= self.msg_selectscene
        self.job.envscene=None

    def setshow(self):
        if self.job.envtype == "user_work":
            self.job.envshow=self.job.username
            self.envshowbut["text"]=self.job.envshow
        elif self.job.envtype == "project_work":
            self.envshowfullpath = tkFileDialog.askdirectory(parent=self.master,\
                    initialdir=os.path.join(self.job.dabwork,"project_work"),title=self.msg_selectshow)
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
        _typefullpath = os.path.join(self.job.dabwork, self.job.envtype, self.job.envshow)
        _projectrelpath = os.path.relpath(self.projfullpath, _typefullpath)

        self.job.envproject=_projectrelpath
        self.envprojbut["text"]= _projectrelpath

    def consolidate(self):
        try:
            self.job.projectfullpath=self.projfullpath
            self.job.nukescriptfullpath=self.filefullpath
            self.job.optionskipframe=self.skipframes.get()  # gets from the tk object
            self.job.optionmakeproxy=self.makeproxy.get()
            self.job.optionresolution=self.resolution.get()
            self.job.optionsendjobstartemail=self.emailjobstart.get()
            self.job.optionsendjobendemail=self.emailjobend.get()
            self.job.optionsendtaskendemail=self.emailtaskend.get()
            self.job.options=self.options.get()  # gets from the tk object
            self.job.farmtier=self.tier.get()
            self.job.jobthreads=self.threads.get()
            self.job.jobstartframe=self.sf.get()
            self.job.jobendframe=self.ef.get()
            self.job.jobbyframe=self.bf.get()
            self.job.jobthreadmemory=self.memory.get()
            self.job.jobchunks=self.chunks.get()
            self.job.softwareversion=self.nukeversion.get()
        except Exception,err:
            logger.warn("consolidate %s"%err)

    def validate(self):
        self.consolidate()
        logger.info("Validate")
        logger.info("Project: %s" % self.projfullpath)
        logger.info("SceneFile: %s" % self.filefullpath)
        logger.info("Start: %s" % self.sf.get())
        logger.info("End: %s" % self.ef.get())
        logger.info("By: %s" % self.bf.get())
        logger.info("Skip Existing Frames: %s" % self.skipframes.get())

        try:
            rj=rfac.Render(self.job)
        except Exception, validateError:
            logger.warn("Problem validating %s" % validateError)
        else:
            rj.build()
            rj.validate()

    def submit(self):
        try:
            self.consolidate()
            self.master.destroy()
            rj=rfac.Render(self.job)
            rj.build()
            rj.validate()
            rj.spool()

        except Exception, submiterror:
            logger.warn("Problem submitting %s" % submiterror)

    def cancel(self):
        logger.info("Camcelled")
        self.master.destroy()


if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)
    w=Window()
    # for key in w.job.__dict__.keys():
    #     print "{:20} = {}".format(key,w.job.__dict__.get(key))

