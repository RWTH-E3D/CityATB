import os
from PyQt4 import QtGui, QtCore


def screenSizer(self, posx, posy, width, height):
    """func to get size of screen and scale window accordingly"""
    sizefactor = round(QtGui.QDesktopWidget().screenGeometry().height()*0.001)              # factor for scaling window, depending on height
    posx *= sizefactor
    posy *= sizefactor
    width *= sizefactor
    height *= sizefactor
    return posx, posy, width, height, sizefactor



def windowSetup(self, posx, posy, width, height, pypath, title, winFac = 1):
    """func for loading icon, setting size and title"""
    try:                                                                            # try to load e3d Icon
        self.setWindowIcon(QtGui.QIcon(os.path.join(pypath, r'pictures\e3d.ico')))
    except:
        print('error finding file icon')
    self.setGeometry(posx, posy, width * winFac, height * winFac)                   # setting window size
    self.setFixedSize(width * winFac, height * winFac)                                                # fixing window size
    self.setWindowTitle(title)                                                      # setting title



def close_application(self):
    """quit dialog, to confirm exiting"""
    choice = QtGui.QMessageBox.question(self, 'Attention!', 'Do you want to quit?',
                                        QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
    if choice == QtGui.QMessageBox.Yes:
        QtCore.QCoreApplication.instance().quit()
    else:
        pass



def dimensions(self):
    """gets current dimensions of window"""
    posx = self.geometry().x()
    posy = self.geometry().y()
    return posx, posy



def next_window(self, window, close=True):
    """calls next window, closes current if True"""
    self.next_window_jump = window
    self.next_window_jump.show()
    if close == True:
        self.hide()



def load_banner(self, path, sizefactor, banner_size=150):
    """loading image from path to self.vbox"""
    try:
        self.banner = QtGui.QLabel(self)
        self.banner.setPixmap(QtGui.QPixmap(path))
        self.banner.setScaledContents(True)
        self.banner.setMinimumHeight(banner_size*sizefactor)
        self.banner.setMaximumHeight(banner_size*sizefactor)
        self.vbox.addWidget(self.banner)
    except:
        print('error finding banner picture')
