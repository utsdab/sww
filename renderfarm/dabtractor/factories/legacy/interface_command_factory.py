#!/usr/bin/env rmanpy
"""
To do:
    cleanup routine for rib
    create a ribgen then prman version
    check and test options
    run farmuser to check is user is valid


"""

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
sh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)5.5s \t%(name)s \t%(message)s')
sh.setFormatter(formatter)
logger.addHandler(sh)

import Tkinter as tk
# from PIL import ImageTk, Image
import ttk
import tkFileDialog
import Tkconstants
import os
import renderfarm.dabtractor as dabtractor
import renderfarm.dabtractor.factories.environment_factory as envfac

class WindowBase(object):
    """ Base class for all batch jobs """
    def __init__(self):
        self.fj=envfac.TractorJob()
        self.spooljob = False
        self.validatejob = False
        self.master = tk.Tk()
        self.renderusernumber = self.fj.usernumber
        self.renderusername = self.fj.username
        self.dabrenderworkpath = self.fj.dabwork
        self.initialProjectPath = self.fj.dabwork  # self.renderuserhomefullpath

    @staticmethod
    def usedirmap(inputstring):
        # wraps a command string up as per dirmap needs in pixar tractor eg. %D(mayabatch)
        return '%D({thing})'.format(thing=inputstring)

    @staticmethod
    def expandargumentstring(inputargs=""):
        """
        This takes a string like "-r 2 -l 4" and returns
        {-r} {2} {-l} {4} which is what tractor wants for arguments
        """
        arglist = inputargs.split(" ")
        outputstring = "} {".join(arglist)
        return outputstring



class WindowCommand(WindowBase):
    """ Ui Class for render submit """
    def __init__(self):
        """ Construct the main window interface """
        super(WindowCommand, self).__init__()
        self.dirtext = 'Select your project folder, or...'
        self.filetext = 'Select your maya scene file'
        self.workspacetext = 'Select the workspace.mel file in your project'
        self.workspaceerrortext = 'Warning - no workspace.mel found!'
        self.filename = ""
        self.dirname = ""
        self.workspace = ""
        self.bgcolor1 = "white"
        self.bgcolor2 = "lemon chiffon"
        self.master.configure(background=self.bgcolor1)
        self.master.title("Tractor Maya-MentalRay Batch Submit {u} {f}".format(u=os.getenv("USER"), f="DAB"))


        ################
        self.canvas = tk.Canvas(self.master, height=200, width=300)
        self.canvas.pack(expand=True, fill=tk.BOTH)
        imagepath = os.path.join(os.path.dirname(dabtractor.__file__),"icons","UTS_logo.gif")
        image1 = tk.PhotoImage(file=imagepath)

        # keep a link to the image to stop the image being garbage collected
        self.canvas.img = image1
        self.canvas.create_image(0, 0, anchor=tk.NW, image=image1)

        __row = 1

        tk.Label(self.canvas).grid(row=__row, sticky=tk.W)
        __row += 1
        tk.Label(self.canvas).grid(row=__row, sticky=tk.W)
        __row += 1
        tk.Label(self.canvas).grid(row=__row, sticky=tk.W)
        __row += 1
        tk.Label(self.canvas).grid(row=__row, sticky=tk.W)
        __row += 1
        tk.Label(self.canvas).grid(row=__row, sticky=tk.W)
        __row += 1
        tk.Label(self.canvas).grid(row=__row, sticky=tk.W)
        __row += 1
        tk.Label(self.canvas).grid(row=__row, sticky=tk.W)
        __row += 1
        tk.Label(self.canvas).grid(row=__row, sticky=tk.W)
        __row += 1
        tk.Label(self.canvas).grid(row=__row, sticky=tk.W)
        __row += 1
        tk.Label(self.canvas).grid(row=__row, sticky=tk.W)
        __row += 1
        # tk.Label(self.canvas, bg=self.bgcolor1, text=" --MAYA---> ").grid(row=__row, column=0)
        tk.Label(self.canvas, bg=self.bgcolor1, text="Generic Shell Command").grid(
            row=__row, column=1)
        __row += 1


        # ################ Options for buttons ####################
        self.button_opt = {'fill': Tkconstants.BOTH, 'padx': 5, 'pady': 5}

        tk.Label(self.canvas, bg=self.bgcolor1, text="Project Dir").grid(row=__row, column=0)
        self.dirbut = tk.Button(self.canvas, text=self.dirtext, bg=self.bgcolor2, fg='black',
                                command=self.opendirectory)
        self.dirbut.pack(**self.button_opt)  # must pack separately to get the value to dirbut
        self.dirbut.grid(row=__row, column=1, sticky=tk.W + tk.E)
        __row += 1

        tk.Label(self.canvas, bg=self.bgcolor1, text="Workspace.mel").grid(row=__row, column=0)
        self.workspacebut = tk.Button(self.canvas, bg=self.bgcolor2, text=self.workspacetext, fg='black',
                                   command=self.openworkspace)
        self.workspacebut.pack(**self.button_opt)  # must pack separately to get the value to dirbut
        self.workspacebut.grid(row=__row, column=1, sticky=tk.W + tk.E)
        __row += 1

        tk.Label(self.canvas, bg=self.bgcolor1, text="Scene File").grid(row=__row, column=0)
        self.filebut = tk.Button(self.canvas, text=self.filetext, fg='black',
                              command=self.openfile)
        self.filebut.pack(**self.button_opt)
        self.filebut.grid(row=__row, column=1, sticky=tk.W + tk.E)
        __row += 1

        tk.Label(self.canvas, bg=self.bgcolor1,
              text="------- Maya Generic Details -------").grid(row=__row, column=1, rowspan=1)
        __row += 1

        tk.Label(self.canvas, bg=self.bgcolor1, text="Frame Start").grid(row=__row, column=0)
        self.sf = tk.StringVar()
        self.sf.set("1")
        self.bar3 = tk.Entry(self.canvas, bg=self.bgcolor2,textvariable=self.sf, width=8).grid(\
            row=__row, column=1, sticky=tk.W)
        __row += 1

        tk.Label(self.canvas, bg=self.bgcolor1, text="Frame End").grid(row=__row, column=0)
        self.ef = tk.StringVar()
        self.ef.set("4")
        self.bar4 = tk.Entry(self.canvas, bg=self.bgcolor2,textvariable=self.ef, width=8).grid(\
            row=__row, column=1, sticky=tk.W)
        __row += 1

        tk.Label(self.canvas, bg=self.bgcolor1, text="By").grid(row=__row, column=0)
        self.bf = tk.StringVar()
        self.bf.set("1")
        self.bar5 = tk.Entry(self.canvas, bg=self.bgcolor2,textvariable=self.bf, width=8).grid(\
            row=__row, column=1, sticky=tk.W)
        __row += 1

        tk.Label(self.canvas, bg=self.bgcolor1, text="Frame Chunks").grid(row=__row, column=0)
        self.fch = tk.StringVar()
        self.fch.set("4")
        self.bar6 = tk.Entry(self.canvas, bg=self.bgcolor2,
                             textvariable=self.fch, width=8).grid(row=__row, column=1, sticky=tk.W)
        __row += 1

        tk.Label(self.canvas, bg=self.bgcolor1, text="Maya Version").grid(row=__row, column=0)
        self.mversion = tk.StringVar()
        self.mversion.set("2015")
        combobox = ttk.Combobox(self.canvas, textvariable=self.mversion)
        combobox.config(values="2015")
        combobox.grid(row=__row, column=1, sticky=tk.W)
        __row += 1

        tk.Label(self.canvas, bg=self.bgcolor1, text="Resolution").grid(row=__row, column=0)
        self.resolution = tk.StringVar()
        self.resolution.set("720p")
        combobox = ttk.Combobox(self.canvas, textvariable=self.resolution)
        combobox.config(values=("720p","1080p","540p","SCENE"))
        combobox.grid(row=__row, column=1, sticky=tk.W + tk.E)
        __row += 1

        tk.Label(self.canvas, bg=self.bgcolor1, text="Output Format").grid(row=__row, column=0)
        self.outformat = tk.StringVar()
        self.outformat.set("exr")
        combobox = ttk.Combobox(self.canvas, textvariable=self.outformat)
        combobox.config(values=("exr", "jpg", "tif", "png"))
        combobox.grid(row=__row, column=1, sticky=tk.W)
        __row += 1

        tk.Label(self.canvas, bg=self.bgcolor1, text="------ Renderer Specific Details ------").grid(\
            row=__row, column=1)
        __row += 1

        tk.Label(self.canvas, bg=self.bgcolor1, text="Renderer").grid(row=__row, column=0)
        self.renderer = tk.StringVar()
        self.renderer.set("mr")
        combobox = ttk.Combobox(self.canvas, textvariable=self.renderer)
        combobox.config(values=("mr"))
        combobox.grid(row=__row, column=1, sticky=tk.W)
        __row += 1

        self.skipframes = tk.StringVar()
        self.skipframes.set(1)
        tk.Checkbutton(self.canvas, bg=self.bgcolor1, text="Skip Existing Frames", variable=self.skipframes,
                    onvalue="1", offvalue="0").grid(row=__row, column=1)
        # self.skipframes = tk.StringVar()
        __row += 1

        tk.Label(self.canvas, bg=self.bgcolor1, text="Other Options").grid(row=__row, column=0)
        self.options = tk.StringVar()
        self.options.set("")
        self.bar7 = tk.Entry(self.canvas, bg=self.bgcolor2,
                             textvariable=self.options, width=40).grid(row=__row, column=1, sticky=tk.W + tk.E)
        __row += 1

        tk.Label(self.canvas, bg=self.bgcolor1, text="------- Submit Job To Tractor  -------").grid(row=__row, column=1)
        __row += 1

        # tk.Buttons
        self.cbutton = tk.Button(self.canvas, bg=self.bgcolor1, text='SUBMIT', command=lambda: self.submit())
        self.cbutton.grid(row=__row, column=3, sticky=tk.W + tk.E)

        self.vbutton = tk.Button(self.canvas, bg=self.bgcolor1, text='VALIDATE', command=lambda: self.validate())
        self.vbutton.grid(row=__row, column=1, sticky=tk.W + tk.E)

        self.vbutton = tk.Button(self.canvas, bg=self.bgcolor1, text='CANCEL', command=lambda: self.cancel())
        self.vbutton.grid(row=__row, column=0, sticky=tk.W + tk.E)

        self.master.mainloop()

    def openfile(self):
        self.filename = tkFileDialog.askopenfilename(parent=self.master, initialdir=self.dirname,\
                                                     title=self.filetext,
                                                     filetypes=[('maya ascii', '.ma'),
                                                                ('maya binary', '.mb')])  # filename not filehandle
        self.filebut["text"] = str(self.filename) if self.filename else self.filetext

    def opendirectory(self):
        self.dirname = tkFileDialog.askdirectory(parent=self.master, initialdir=self.initialProjectPath,
                                                 title=self.dirtext)
        self.dirbut["text"] = str(self.dirname) if self.dirname else self.dirtext
        _possible = "%s/workspace.mel" % self.dirname
        if os.path.exists(_possible):
            self.workspace = _possible
            self.workspacebut["text"] = str(self.workspace) if self.workspace else self.workspacetext
        else:
            self.workspacebut["text"] = self.workspaceerrortext

    def openworkspace(self):
        self.workspace = tkFileDialog.askopenfilename(parent=self.master, initialdir=self.initialProjectPath,
                                                      title=self.workspacetext,
                                                      filetypes=[('maya workspace', '.mel')])  # filename not filehandle
        self.dirname = os.path.dirname(self.workspace)
        self.workspacebut["text"] = str(self.workspace) if self.workspace else self.workspacetext
        self.dirbut["text"] = str(self.dirname) if self.dirname else self.dirtext

    def validate(self):
        logger.info("Validate")

    def submit(self):
        try:
            logger.info("Submit")
            logger.info("Project: %s" % self.dirname)
            logger.info("SceneFile: %s" % self.filename)
            logger.info("Start: %s" % self.sf.get())
            logger.info("End: %s" % self.ef.get())
            logger.info("By: %s" % self.bf.get())
            logger.info("Chunk: %s" % self.fch.get())
            logger.info("Maya: %s" % self.mversion.get())
            # spooljob=True
            self.spooljob = True
            self.master.destroy()
        except Exception, submiterror:
            logger.warn("Problem submitting %s" % submiterror)

    def cancel(self):
        logger.info("Camcelled")
        self.master.destroy()

if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)
    w=WindowCommand()
