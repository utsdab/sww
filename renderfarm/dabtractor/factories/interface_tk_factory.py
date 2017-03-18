# Use Tkinter for python 2, tkinter for python 3
from Tkinter import *
from ttk import *
from Tkconstants import *
import sys




class Navbar(Frame):
    """
    """
    def __init__(self, parent):
        self.parent=parent
        print "*** navbar init"

        self.button=Button(self.parent, text="BUTTON_N1")
        self.button.pack()

        self.button2=Button(self.parent, text="BUTTON_N2")
        self.button2.pack()

class Toolbar(Frame):
    """

    """
    def __init__(self, parent):
        self.parent=parent
        print "*** toolbar init"

        self.button=Button(self.parent, text="BUTTON_T1")
        self.button.pack()

        self.button2=Button(self.parent, text="BUTTON_T2")
        self.button2.pack()

class Statusbar(Frame):
    """

    """
    def __init__(self, parent):
        self.parent=parent
        print "*** statusbar init"

        self.button=Button(self.parent, text="BUTTON_S1")
        self.button.pack()

        self.button2=Button(self.parent, text="BUTTON_S2")
        self.button2.pack()


class Main(Frame):
    """

    """
    def __init__(self, parent):
        self.parent=parent
        print "*** main init"

        self.button=Button(self.parent, text="BUTTON_M1")
        self.button.pack()

        self.button2=Button(self.parent, text="BUTTON_M2")
        self.button2.pack()


class FarmSubmitBase(Frame):
    def __init__(self, *args, **kwargs):
        self.root=Tk()
        self.root.title("Farm Submit")
        Frame.__init__(self, self.root, *args, **kwargs)


class FarmSubmit(FarmSubmitBase):
    def __init__(self, *args, **kwargs):
        FarmSubmitBase.__init__(self, *args, **kwargs)

        self.navbar = Navbar(self.root)
        self.toolbar = Toolbar(self.root)
        self.main = Main(self.root)
        self.statusbar = Statusbar(self.root)


        # self.statusbar.pack(side="bottom", fill="x")
        # self.toolbar.pack(side="top", fill="x")
        # self.navbar.pack(side="left", fill="y")
        # self.main.pack(side="right", fill="both", expand=True)

        self.root.mainloop()

if __name__ == "__main__":
    fs=FarmSubmit()




# class Demo1:
#     def __init__(self, master):
#         self.master = master
#         self.frame = Frame(self.master)
#         self.button1 = Button(self.frame, text = 'New Window', width = 25, command = self.new_window)
#         self.button1.pack()
#         self.frame.pack()
#     def new_window(self):
#         self.newWindow = Toplevel(self.master)
#         self.app = Demo2(self.newWindow)
#
# class Demo2:
#     def __init__(self, master):
#         self.master = master
#         self.frame = Frame(self.master)
#         self.quitButton = Button(self.frame, text = 'Quit', width = 25, command = self.close_windows)
#         self.quitButton.pack()
#         self.frame.pack()
#     def close_windows(self):
#         self.master.destroy()
#
# def main():
#     root = Tk()
#     app = Demo1(root)
#     root.mainloop()
#
# if __name__ == '__main__':
#     main()
