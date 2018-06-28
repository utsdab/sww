#! /usr/bin/env python

from Tkinter import *
from ttk import *

# NOTE: Frame will make a top-level window if one doesn't already exist which
# can then be accessed via the frame's master attribute

# make a Frame whose parent is root, named "notebookdemo"
master = Frame(name='notebookdemo')
root = master.master  # short-cut to top-level window
master.pack()  # pack the Frame into root, defaults to side=TOP
root.title('Notebook Demo')  # name the window

# create notebook
demoPanel = Frame(master, name='demo')  # create a new frame slaved to master
demoPanel.pack()  # pack the Frame into root

# create (notebook) demo panel
nb = Notebook(demoPanel, name='notebook')  # create the ttk.Notebook widget

# extend bindings to top level window allowing
#   CTRL+TAB - cycles thru tabs
#   SHIFT+CTRL+TAB - previous tab
#   ALT+K - select tab using mnemonic (K = underlined letter)
nb.enable_traversal()

nb.pack(fill=BOTH, expand=Y, padx=2, pady=3)  # add margin

# create description tab
# frame to hold (tab) content
frame = Frame(nb, name='descrip')

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
                 command=lambda v=neatVar: _say_neat(master, v))
neat = Label(frame, textvariable=neatVar, name='neat')

# position and set resize behavior
lbl.grid(row=0, column=0, columnspan=2, sticky='new', pady=5)
btn.grid(row=1, column=0, pady=(2,4))
neat.grid(row=1, column=1,  pady=(2,4))
frame.rowconfigure(1, weight=1)
frame.columnconfigure((0,1), weight=1, uniform=1)

# bind for button short-cut key
# (must be bound to toplevel window)
master.winfo_toplevel().bind('<Alt-n>', lambda e, v=neatVar: self._say_neat(v))

# add to notebook (underline = index for short-cut character)
nb.add(frame, text='Description', underline=0, padding=2)

def _say_neat(master, v):
    v.set('Yeah, I know...')
    master.update()
    master.after(500, v.set(''))

# create disabled tab
# Populate the second pane. Note that the content doesn't really matter
disabled_frame = Frame(nb)
nb.add(disabled_frame, text='Disabled', state='disabled')

# create text tab
# populate the third frame with a text widget
txt_frame = Frame(nb)

txt = Text(txt_frame, wrap=WORD, width=40, height=10)
vscroll = Scrollbar(txt_frame, orient=VERTICAL, command=txt.yview)
txt['yscroll'] = vscroll.set
vscroll.pack(side=RIGHT, fill=Y)
txt.pack(fill=BOTH, expand=Y)

# add to notebook (underline = index for short-cut character)
nb.add(txt_frame, text='Text Editor', underline=0)

master.mainloop()
