#!/usr/bin/env rmanpy

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
import sys
import os
from Tkinter import *
from ttk import *
from Tkconstants import *
from tkFileDialog import *
from tkMessageBox import *

import datetime
import tractor.api.author as author
import sww.renderfarm.dabtractor.factories.environment_factory as envfac

BASE = RAISED
SELECTED = FLAT

class Tab(Frame):
    """ """
    def __init__(self, master, name):
        Frame.__init__(self, master)
        self.tab_name = name

class TabBar(Frame):
    def __init__(self, master=None, init_name=None):
        Frame.__init__(self, master)
        self.tabs = {}
        self.buttons = {}
        self.current_tab = None
        self.init_name = init_name

    def show(self):
        self.pack(side=TOP, expand=YES, fill=X)
        self.switch_tab(self.init_name or self.tabs.keys()[-1])# switch the tab to the first tab

    def add(self, tab):
        tab.pack_forget()									# hide the tab on init

        self.tabs[tab.tab_name] = tab						# add it to the list of tabs
        b = Button(self, text=tab.tab_name, relief=BASE,	# basic button stuff
            command=(lambda name=tab.tab_name: self.switch_tab(name)))	# set the command to switch tabs
        b.pack(side=LEFT)												# pack the buttont to the left mose of self
        self.buttons[tab.tab_name] = b						# add it to the list of buttons

    def delete(self, tabname):

        if tabname == self.current_tab:
            self.current_tab = None
            self.tabs[tabname].pack_forget()
            del self.tabs[tabname]
            self.switch_tab(self.tabs.keys()[0])

        else: del self.tabs[tabname]

        self.buttons[tabname].pack_forget()
        del self.buttons[tabname]


    def switch_tab(self, name):
        if self.current_tab:
            self.buttons[self.current_tab].config(relief=BASE)
            self.tabs[self.current_tab].pack_forget()			# hide the current tab
        self.tabs[name].pack(side=BOTTOM)							# add the new tab to the display
        self.current_tab = name									# set the current tab to itself

        self.buttons[name].config(relief=SELECTED)					# set it to the selected style

class TabbedPanel(Frame):
    """ TabbedPanel """
    def __init__(self, isapp=True, name='notebookpanel'):
        Frame.__init__(self, name=name,bg="red", borderwidth=4 )
        self.pack(expand=Y, fill=BOTH)
        self.isapp = isapp
        self._create_widgets()

    def _create_widgets(self):
        self._create_tabbed_panel()

    def _create_tabbed_panel(self):
        Panel = Frame(self, name='demo')
        Panel.pack(side=TOP, fill=BOTH, expand=Y)

        # create the notebook
        nb = Notebook(Panel, name='notebook')

        # extend bindings to top level window allowing
        #   CTRL+TAB - cycles thru tabs
        #   SHIFT+CTRL+TAB - previous tab
        #   ALT+K - select tab using mnemonic (K = underlined letter)
        nb.enable_traversal()

        nb.pack(fill=BOTH, expand=Y, padx=2, pady=3)
        self._rmf_tab(nb)
        self._create_bash_tab(nb)
        self._create_nuke_tab(nb)

    def _rmf_tab(self, nb):
        """ renderman for maya tab """
        frame = Frame(nb, name='rmf')

        # widgets to be displayed on 'Description' tab
        msg = [
            "Ttk is the new Tk themed widget set. One of the widgets ",
            "it includes is the notebook widget, which provides a set ",
            "of tabs that allow the selection of a group of panels, ",
            "each with distinct content. They are a feature of many ",
            "modern user interfaces. Not only can the tabs be selected ",
            "with the mouse, but they can also be switched between ",
            "using Ctrl+Tab when the notebook page heading itself is ",
            "selected. Note that the second tab is disabled, and cannot "
            "be selected."]

        lbl = Label(frame, wraplength='4i', justify=LEFT, anchor=N,
                        text=''.join(msg))
        neatVar = StringVar()
        btn = Button(frame, text='Neat!', underline=0,
                         command=lambda v=neatVar: self._say_neat(v))
        neat = Label(frame, textvariable=neatVar, name='neat')

        # position and set resize behaviour
        lbl.grid(row=0, column=0, columnspan=2, sticky='new', pady=5)
        btn.grid(row=1, column=0, pady=(2,4))
        neat.grid(row=1, column=1,  pady=(2,4))
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure((0,1), weight=1, uniform=1)

        # bind for button short-cut key
        # (must be bound to toplevel window)
        self.winfo_toplevel().bind('<Alt-n>', lambda e, v=neatVar: self._say_neat(v))

        # add to notebook (underline = index for short-cut character)
        nb.add(frame, text='RMF', underline=0, padding=2)

    def _say_neat(self, v):
        v.set('Yeah, I know...')
        self.update()
        self.after(500, v.set(''))

    # =============================================================================
    def _create_bash_tab(self, nb):
        # Populate the second pane. Note that the content doesn't really matter
        frame = Frame(nb)
        nb.add(frame, text='Disabled', state='disabled')

    # =============================================================================
    def _create_nuke_tab(self, nb):
        # populate the third frame with a text widget
        frame = Frame(nb)

        txt = Text(frame, wrap=WORD, width=40, height=10)
        vscroll = Scrollbar(frame, orient=VERTICAL, command=txt.yview)
        txt['yscroll'] = vscroll.set
        vscroll.pack(side=RIGHT, fill=Y)
        txt.pack(fill=BOTH, expand=Y)

        # add to notebook (underline = index for short-cut character)
        nb.add(frame, text='Nuke', underline=0)

class WindowBase(object):
    def __init__(self):
        """ Base the main window interface """
        self.fj = envfac.FarmJob()
        self.env = envfac.Environment2()


class Window2(WindowBase):
    def __init__(self, master):
        """ Construct the main window interface """
        super(Window2, self).__init__()
        self.master = master
        self.master.title("Farm Submit {n} {d}".format(n=self.fj.username,d=datetime.date.today()))
        self.dirtext = 'Select your project folder'
        self.workspaceerrortext = 'Warning - no workspace.mel found!'
        self.workspacetext = 'wsb'
        self.filetext = 'Select your maya scene file'

        self.button_opt = {'fill': BOTH, 'padx': 5, 'pady': 5}
        self.frame_opt  = {'side': TOP}

        self.topframe=Frame(self.master,
                            # bg="green",
                            borderwidth=4)

        self.label1=Label(self.topframe, text="Project Dir").grid(row=1, column=0)
        self.dirbut = Button(self.topframe, text=self.dirtext,
                             # fg='black',
                             command=self.opendirectory)
        self.dirbut.pack(**self.button_opt)  ## must pack separately to get the value to dirbut
        self.dirbut.grid(row=1, column=1, sticky=W + E)

        self.topframe.pack(**self.frame_opt)

        self.bottomframe=Frame(self.master,bg="red", borderwidth=10)
        # self.nb=TabbedPanel()
        self.tb=TabBar(self.master)

        self.mayatab=Tab(self.tb,"Maya")
        Label(self.mayatab, text="Sunjay sunjay-varma.com", bg="white", fg="red").pack(side=TOP, expand=YES, fill=BOTH)
        Button(self.mayatab, text="PRESS ME!", command=(\
            lambda: write("YOU PRESSED ME!"))).pack(side=BOTTOM,fill=BOTH, expand=YES)
        Button(self.mayatab, text="KILL THIS TAB", command=(\
            lambda: self.tb.delete("Wow..."))).pack(side=BOTTOM, fill=BOTH, expand=YES)


        self.tb.add(self.mayatab)
        self.tb.add(self.mayatab)

        self.bottomframe.pack(**self.frame_opt)

        self.tb.show()


    def opendirectory(self):
        self.dirname = askdirectory(parent=self.master, initialdir=self.fj.dabwork,title=self.dirtext)
        self.dirbut["text"] = str(self.dirname) if self.dirname else self.dirtext
    #     _possible = "%s/workspace.mel" % (self.dirname)
    #     if os.path.exists(_possible):
    #         self.workspace = _possible
    #         self.workspacebut["text"] = str(self.workspace) if self.workspace else self.msg_workspaceok
    #     else:
    #         self.workspacebut["text"] = self.msg_workspacebad
    #
    # def openfile(self):
    #     self.filename = askopenfilename(\
    #         parent=self.master, initialdir=self.dirname,title=self.msg_selectscene,
    #         filetypes=[('maya ascii', '.ma'),('maya binary', '.mb')])  ## filename not filehandle
    #     self.filebut["text"] = str(self.filename) if self.filename else self.msg_selectscene

class Window(object):
    def __init__(self, master):
        """Construct the main window interface
        """
        self.master = master
        self.fj = envfac.FarmJob()
        self.dirtext = 'Select your project folder'
        self.filetext = 'Select your maya scene file'
        self.workspacetext = 'Select the workspace.mel file in your project'
        self.workspaceerrortext = 'Warning - no workspace.mel found!'
        self.filename=""
        self.test = False
        self.env=envfac.Environment2()
        # vcmd = (self.register(self._validate), '%s', '%P')
        # okayCommand = self.register(isOkay)

        # Options for buttons
        self.button_opt = {'fill': BOTH, 'padx': 5, 'pady': 5}

        Label(master, text="Project Dir").grid(row=1, column=0)
        self.dirbut = Button(self.master, text=self.dirtext, fg='black', command=self.opendirectory)
        self.dirbut.pack(**self.button_opt)  ## must pack separately to get the value to dirbut
        self.dirbut.grid(row=1, column=1, sticky=W + E)

        Label(master, text="Workspace.mel").grid(row=2, column=0)
        self.workspacebut = Button(self.master, text=self.workspacetext, fg='black', command=self.openworkspace)
        self.workspacebut.pack(**self.button_opt)  ## must pack separately to get the value to dirbut
        self.workspacebut.grid(row=2, column=1, sticky=W + E)

        Label(master, text="Scene File").grid(row=3, column=0)
        self.filebut = Button(self.master, text=self.filetext, fg='black',command=self.openfile)
        self.filebut.pack(**self.button_opt)
        self.filebut.grid(row=3, column=1, sticky=W + E)

        Label(master, text="Frame Start").grid(row=6, column=0)
        self.sf = StringVar()
        self.sf.set("1")
        self.bar3 = Entry(self.master, textvariable=self.sf, width=8).grid(row=6, column=1, sticky=W)

        Label(master, text="Frame End").grid(row=7, column=0)
        self.ef = StringVar()
        self.ef.set("100")
        self.bar4 = Entry(self.master, textvariable=self.ef, width=8).grid(row=7, column=1, sticky=W)

        Label(master, text="By").grid(row=8, column=0)
        self.bf = StringVar()
        self.bf.set("1")
        self.bar5 = Entry(self.master, textvariable=self.bf, width=8).grid(row=8, column=1, sticky=W)

        Label(master, text="Frame Chunks").grid(row=9, column=0)
        self.fch = StringVar()
        self.fch.set("5")
        self.bar6 = Entry(self.master, textvariable=self.fch, width=8).grid(row=9, column=1, sticky=W)

        Label(self.master, text="Maya Version").grid(row=10, column=0)
        self.mversion = StringVar()
        self.mversion.set("2015")
        combobox = Combobox(master, textvariable=self.mversion)
        combobox.config(values=("2015"))
        combobox.grid(row=10, column=1, sticky=W)

        Label(self.master, text="Renderer").grid(row=11, column=0)
        self.renderer = StringVar()
        self.renderer.set("rman")
        okayCommand = master.register(self.isOkay)
        combobox1 = Combobox(master, textvariable=self.renderer, postcommand=lambda: self.optionspostcommand(),
                                    # validate='all', validatecommand=lambda: self.optionscommand())
                                    validate='all', validatecommand=(okayCommand, '%P', '%V', '%s', '%S'))
        combobox1.config(values=("mr", "maya", "rman"))
        combobox1.grid(row=11, column=1, sticky=W)

        Label(self.master, text="Output").grid(row=12, column=0)
        self.outputname = StringVar()
        self.outputname.set("<Scene>/<Scene>")
        combobox = Combobox(master, textvariable=self.outputname)
        combobox.config(values=("<Scene>/<Scene>",
                                "<Scene>/<Scene>-<Camera>",
                                "<Scene>/<Scene>-<Camera>-<Layer>"))
        combobox.grid(row=12, column=1, sticky=W + E)

        Label(self.master, text="Resolution").grid(row=13, column=0)
        self.resolution = StringVar()
        self.resolution.set("720p")
        combobox = Combobox(master, textvariable=self.resolution)
        combobox.config(values=("720p","1080p","540p", ""))
        combobox.grid(row=13, column=1, sticky=W + E)

        Label(master, text="Other Options").grid(row=14, column=0)
        self.options = StringVar()
        self.options.set("")
        self.bar7 = Entry(self.master, textvariable=self.options, width=40).grid(\
            row=14, column=1, sticky=W+E)


        # Buttons
        self.cbutton = Button(self.master, text='SUBMIT', command=lambda: self.submit())
        self.cbutton.grid(row=15, column=3, sticky=W + E)

        self.vbutton = Button(self.master, text='VALIDATE', command=lambda: self.validate())
        self.vbutton.grid(row=15, column=1, sticky=W + E)

        self.vbutton = Button(self.master, text='CANCEL', command=lambda: self.cancel())
        self.vbutton.grid(row=15, column=0, sticky=W + E)

    def openfile(self):
        self.filename = askopenfilename(parent=self.master, initialdir=self.dirname,title=self.filetext,
                         filetypes=[('maya ascii', '.ma'), ('maya binary', '.mb')])  ## filename not filehandle
        self.filebut["text"] = str(self.filename) if self.filename else self.filetext

    def opendirectory(self):
        self.dirname = askdirectory(parent=self.master, initialdir=self.env.environ["DABWORK"],
                                                 title=self.dirtext)
        self.dirbut["text"] = str(self.dirname) if self.dirname else self.dirtext
        _possible = "%s/workspace.mel" % (self.dirname)
        if os.path.exists(_possible):
            self.workspace = _possible
            self.workspacebut["text"] = str(self.workspace) if self.workspace else self.workspacetext
        else:
            self.workspacebut["text"] = self.workspaceerrortext

    def openworkspace(self):
        self.workspace = askopenfilename(parent=self.master, initialdir=self.fj.dabwork,title=self.workspacetext,
                filetypes=[('maya workspace', '.mel')])  ## filename not filehandle
        self.dirname = os.path.dirname(self.workspace)
        self.workspacebut["text"] = str(self.workspace) if self.workspace else self.workspacetext
        self.dirbut["text"] = str(self.dirname) if self.dirname else self.dirtext

    def validate(self):
        logger.info("Validate")

    def optionspostcommand(self):
        logger.info("Renderer change - Options post will change from %s" % self.renderer.get())
        # logger.info("oo %s" % window.bar7.current([0])

    def optionscommand(self):
        logger.info("Renderer change - Options validate will change to %s" % self.renderer.get())

    def isOkay(self, why, where, what, other):
        logger.info("isOkay: %s : %s : %s : %s :" % (why, what, where, other))

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

            self.master.destroy()
        except Exception, err:
            logger.warn("Problem submitting %s" % err)

    def cancel(self):
        logger.info("Camcelled")
        self.master.destroy()

    def selectRenderHome(self):
        logger.info("Select render home")


class MayaBatchJob(object):
    """
    This is a maya batch job
    """

    def __init__(self,  mayaversion="2015",
                        projectpath="/Volumes/dabrender/",
                        scenefile="scene.0001.ma",
                        start=1, end=100, by=1,
                        renderer="rman",
                        renderdirectory="renderout",
                        options=""):

        self.mayaversion = mayaversion
        self.mayaprojectpath = projectpath
        self.mayascene = scenefile
        self.startframe = start
        self.endframe = end
        self.byframe = by
        self.framechunks = 10
        self.renderer = renderer
        self.renderdirectory = renderdirectory
        self.imagetemplate = "<Scene>/<Scene>-<Camera>_<Layer>"
        self.options = options
        self.localhost = "localhost"
        self.localworkarea = "/scratch2/dabRenderJobs/"
        self.centralworkarea = "138.25.195.200"
        self.fj=envfac.FarmJob()
        self.job = self.fj.author.Job(title="Render Job - (maya)",
                      priority=100,
                      envkey=["maya%s" % self.mayaversion],
                      service="PixarRender")

    def getValues(entries):
        for entry in entries:
            field = entry[0]
            text = entry[1].get()
            logger.info('%s: "%s"' % ( field, text))

    def expandArgumentString(self, inputargs=""):
        """
        This takes a string like "-r 2 -l 4" and returns
        {-r} {2} {-l} {4} which is what tractor wants for arguments
        """
        arglist=inputargs.split(" ")
        outputstring = "} {".join(arglist)
        return outputstring

    def usedirmap(self,inputstring):
        """
        wraps a string in the bits needed for dirmap functionality in tractor eg %D(mayabatch)
        :param inputstring: mayabatch
        :return: %D(mayabatch)
        """
        return '%D({thing})'.format(thing=inputstring)

    def build(self):
        """
        main build of job
        :return:
        """
        self.__mayascenefullpath = "%s/%s" % (self.mayaprojectpath, self.mayascene)
        self.__mayascenebase = os.path.splitext(self.mayascene)[0]

        env = self.fj.author.Command(argv = ["printenv"])
        pwd = self.fj.author.Command(argv = ["pwd"])

        task1 = author.Task(title="Make output directory", service="PixarRender")
        makediectory = author.Command(argv=["mkdir", os.path.join(self.mayaprojectpath, "images")])
        task1.addCommand(makediectory)
        self.job.addChild(task1)

        task2 = author.Task(title="Copy Project Locally", service="PixarRender")
        copyin = author.Command(argv=["scp", "%s:%s" % (self.centralworkarea, self.mayaprojectpath),
                                      "%s:%s" % (self.localhost, self.localworkarea)])
        task2.addCommand(copyin)
        self.job.addChild(task2)

        if self.renderer == "mr":
            pass
        elif self.renderer == "rman":
            pass
        elif self.renderer == "maya":
            pass

        task3 = author.Task(title="Rendering", service="PixarRender")

        if (self.endframe - self.startframe) < self.framechunks:
            self.framechunks = 1
            chunkend = self.endframe
        else:
            chunkend = self.startframe + self.framechunks

        chunkstart = self.startframe
        while self.endframe >= chunkstart:
            if chunkend >= self.endframe:
                chunkend = self.endframe

            commonargs = [
                "Render",
                "-r", self.renderer,
                "-proj", self.mayaprojectpath,
                "-start", "%s" % chunkstart,
                "-end", "%s" % chunkend,
                "-by", self.byframe,
                "-rd", self.renderdirectory,
                "-im", self.imagetemplate
                ]

            rendererspecificargs = [
                self.expandArgumentString(self.options),
                self.__mayascenefullpath
                ]
            finalargs = commonargs + rendererspecificargs
            render = author.Command(argv=finalargs)
            task3.addCommand(render)
            chunkstart = chunkend + 1
            chunkend += self.framechunks

        self.job.addChild(task3)

        # ############## task 4 ###############
        task4 = author.Task(title="Copy Project Back", service="PixarRender")
        copyout = author.Command(argv=["scp", "%s:%s" % (self.localhost, self.localworkarea),
                                       "%s:%s" % (self.centralworkarea, self.mayaprojectpath)])
        task4.addCommand(copyout)
        self.job.addChild(task4)

        print "\n{}".format(self.job.asTcl())

    def spool(self):
        try:
            logger.info("Spooled correctly")
            # all jobs owner by pixar user on the farm
            self.job.spool(owner="pixar")
        except Exception, spoolerror:
            logger.warn("A spool error %s" % spoolerror)


if __name__ == '__main__':

    # NotebookDemo().mainloop()

    root = Tk()
    window = Window2(root)
    root.mainloop()

    job = MayaBatchJob()

    try:
        # job.mayascene = window.filename
        # job.projectpath = window.dirname
        # job.framechunks = int(window.fch.get())
        # job.startframe = int(window.sf.get())
        # job.endframe = int(window.ef.get())
        # job.byframe = int(window.bf.get())
        # # job.renderer = window.renderer.get()
        # job.renderdirectory = "%s/images" % window.dirname
        # job.imagetemplate = window.outputname.get()
        # job.options = window.options.get()
        #
        # job.build()
        # j.spool()
        pass
    except Exception, err:
        logger.warn("Something wrong %s" % err)
    try:
        root.destroy()
    except Exception, err:
        logger.warn("Cant destroy the window %s" % err)
