#!/usr/bin/python3
import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from libsisyphus import getMirrors, setActiveMirror

class SisyphusConfig(QtWidgets.QMainWindow):
    def __init__(self):
        super(SisyphusConfig, self).__init__()
        uic.loadUi('ui/sisyphus-config.ui', self)
        self.centerOnScreen()
        self.MIRRORLIST = getMirrors()
        self.updateMirrorList()
        self.show()
        self.applyButton.pressed.connect(self.SisyphusConfigApply)
        self.applyButton.released.connect(self.SisyphusConfigExit)
        self.mirrorCombo.activated.connect(self.setMirrorList)

    def centerOnScreen(self):
        resolution = QtWidgets.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                    (resolution.height() / 2) - (self.frameSize().height() / 2))

    def updateMirrorList(self):
        model = QtGui.QStandardItemModel()
        for row in self.MIRRORLIST:
            indx = self.MIRRORLIST.index(row)
            item = QtGui.QStandardItem()
            item.setText(row['Url'])
            model.setItem(indx, item)
            if row['isActive'] :
                self.ACTIVEMIRRORINDEX = indx
        self.mirrorCombo.setModel(model)
        self.mirrorCombo.setCurrentIndex(self.ACTIVEMIRRORINDEX)

    def setMirrorList(self):
        self.MIRRORLIST[self.ACTIVEMIRRORINDEX]['isActive'] = False
        self.ACTIVEMIRRORINDEX = self.mirrorCombo.currentIndex()
        self.MIRRORLIST[self.ACTIVEMIRRORINDEX]['isActive'] = True

    def SisyphusConfigApply(self):
        setActiveMirror(self.MIRRORLIST)

    def SisyphusConfigExit(self):
        self.close()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = SisyphusConfig()
    sys.exit(app.exec_())
