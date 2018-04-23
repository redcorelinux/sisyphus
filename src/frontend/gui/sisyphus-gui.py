#!/usr/bin/python3
import sys
import subprocess
import sqlite3
import io
import atexit
from collections import OrderedDict
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from libsisyphus import *


# main window class
class Sisyphus(QtWidgets.QMainWindow):
    def __init__(self):
        super(Sisyphus, self).__init__()
        uic.loadUi('ui/sisyphus.ui', self)
        self.centerOnScreen()
        self.show()

        self.filterApplications = OrderedDict([
            ('Search by Name', 'pn'),
            ('Search by Category', 'cat'),
            ('Search by Description', 'descr')
        ])
        self.applicationFilter.addItems(self.filterApplications.keys())
        self.applicationFilter.setCurrentText('Search by Name')
        self.applicationFilter.currentIndexChanged.connect(
            self.setApplicationFilter)
        Sisyphus.applicationView = self.filterApplications['Search by Name']

        self.filterDatabases = OrderedDict([
            ('All Packages', 'all'),
            ('Installed Packages', 'installed'),
            ('Available Packages', 'installable'),
            ('Upgradable Packages', 'upgradable')
        ])
        self.databaseFilter.addItems(self.filterDatabases.keys())
        self.databaseFilter.setCurrentText('All Packages')
        self.databaseFilter.currentIndexChanged.connect(self.setDatabaseFilter)
        Sisyphus.databaseView = self.filterDatabases['All Packages']

        Sisyphus.searchTerm = "'%%'"

        self.databaseTable.clicked.connect(self.rowClicked)

        self.inputBox.textEdited.connect(self.searchDatabase)

        self.settingsButton.clicked.connect(self.showMirrorWindow)
        self.licenseButton.clicked.connect(self.showLicenseWindow)

        self.updateWorker = MainWorker()
        self.updateThread = QtCore.QThread()
        self.updateWorker.moveToThread(self.updateThread)
        self.updateWorker.started.connect(self.showProgressBar)
        self.updateThread.started.connect(self.updateWorker.startUpdate)
        self.updateThread.finished.connect(self.jobDone)
        self.updateWorker.finished.connect(self.updateThread.quit)

        self.installButton.clicked.connect(self.packageInstall)
        self.installWorker = MainWorker()
        self.installThread = QtCore.QThread()
        self.installWorker.moveToThread(self.installThread)
        self.installWorker.started.connect(self.showProgressBar)
        self.installThread.started.connect(self.installWorker.startInstall)
        self.installWorker.strReady.connect(self.updateStatusBar)
        self.installThread.finished.connect(self.jobDone)
        self.installWorker.finished.connect(self.installThread.quit)

        self.uninstallButton.clicked.connect(self.packageUninstall)
        self.uninstallWorker = MainWorker()
        self.uninstallThread = QtCore.QThread()
        self.uninstallWorker.moveToThread(self.uninstallThread)
        self.uninstallWorker.started.connect(self.showProgressBar)
        self.uninstallThread.started.connect(
            self.uninstallWorker.startUninstall)
        self.uninstallWorker.strReady.connect(self.updateStatusBar)
        self.uninstallThread.finished.connect(self.jobDone)
        self.uninstallWorker.finished.connect(self.uninstallThread.quit)

        self.upgradeButton.clicked.connect(self.systemUpgrade)
        self.upgradeWorker = MainWorker()
        self.upgradeThread = QtCore.QThread()
        self.upgradeWorker.moveToThread(self.upgradeThread)
        self.upgradeWorker.started.connect(self.showProgressBar)
        self.upgradeThread.started.connect(self.upgradeWorker.startUpgrade)
        self.upgradeWorker.strReady.connect(self.updateStatusBar)
        self.upgradeThread.finished.connect(self.jobDone)
        self.upgradeWorker.finished.connect(self.upgradeThread.quit)

        self.orphansButton.clicked.connect(self.orphansRemove)
        self.orphansWorker = MainWorker()
        self.orphansThread = QtCore.QThread()
        self.orphansWorker.moveToThread(self.orphansThread)
        self.orphansWorker.started.connect(self.showProgressBar)
        self.orphansThread.started.connect(self.orphansWorker.cleanOrphans)
        self.orphansWorker.strReady.connect(self.updateStatusBar)
        self.orphansThread.finished.connect(self.jobDone)
        self.orphansWorker.finished.connect(self.orphansThread.quit)

        self.updateSystem()
        self.progressBar.hide()

        self.exitButton.clicked.connect(self.sisyphusExit)

    def centerOnScreen(self):
        resolution = QtWidgets.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2))

    def rowClicked(self):
        Sisyphus.pkgSelect = len(
            self.databaseTable.selectionModel().selectedRows())
        self.showPackageCount()

    def showPackageCount(self):
        self.statusBar().showMessage("Found: %d, Selected: %d packages" %
                                     (Sisyphus.pkgCount, Sisyphus.pkgSelect))

    def setApplicationFilter(self):
        Sisyphus.applicationView = self.filterApplications[self.applicationFilter.currentText(
        )]
        self.loadDatabase()

    def setDatabaseFilter(self):
        Sisyphus.databaseView = self.filterDatabases[self.databaseFilter.currentText(
        )]
        Sisyphus.SELECT = self.databaseFilter.currentText()
        self.loadDatabase()

    def loadDatabase(self):
        noVirtual = "AND cat NOT LIKE 'virtual'"
        self.SELECTS = OrderedDict([
            ('all', '''SELECT
                i.category AS cat,
                i.name as pn,
                i.version as iv,
                IFNULL(a.version, 'None') AS av,
                d.description AS descr
                FROM local_packages AS i LEFT OUTER JOIN remote_packages as a
                ON i.category = a.category
                AND i.name = a.name
                AND i.slot = a.slot
				LEFT JOIN remote_descriptions AS d ON i.name = d.name AND i.category = d.category
                WHERE %s LIKE %s %s
                UNION
                SELECT
                a.category AS cat,
                a.name as pn,
                IFNULL(i.version, 'None') AS iv,
                a.version as av,
                d.description AS descr
                FROM remote_packages AS a LEFT OUTER JOIN local_packages AS i
                ON a.category = i.category
                AND a.name = i.name
                AND a.slot = i.slot
				LEFT JOIN remote_descriptions AS d ON a.name = d.name AND a.category = d.category
                WHERE %s LIKE %s %s
            ''' % (Sisyphus.applicationView, Sisyphus.searchTerm, noVirtual, Sisyphus.applicationView, Sisyphus.searchTerm, noVirtual)),
            ('installed', '''SELECT
                i.category AS cat,
                i.name AS pn,
                i.version AS iv,
                a.version as av,
                d.description AS descr
                FROM local_packages AS i
                LEFT JOIN remote_packages AS a
                ON i.category = a.category
                AND i.name = a.name
                AND i.slot = a.slot
				LEFT JOIN remote_descriptions AS d ON i.name = d.name AND i.category = d.category
                WHERE %s LIKE %s %s
            ''' % (Sisyphus.applicationView, Sisyphus.searchTerm, noVirtual)),
            ('installable', '''SELECT
                a.category AS cat,
                a.name AS pn,
                i.version as iv,
                a.version AS av,
                d.description AS descr
                FROM remote_packages AS a
                LEFT JOIN local_packages AS i
                ON a.category = i.category
                AND a.name = i.name
                AND a.slot = i.slot
				LEFT JOIN remote_descriptions AS d ON a.name = d.name AND a.category = d.category
                WHERE %s LIKE %s %s
                AND iv IS NULL
            ''' % (Sisyphus.applicationView, Sisyphus.searchTerm, noVirtual)),
            ('upgradable', '''SELECT
                i.category AS cat,
                i.name AS pn,
                i.version as iv,
                a.version AS av,
                d.description AS descr
                FROM local_packages AS i
                INNER JOIN remote_packages AS a
                ON i.category = a.category
                AND i.name = a.name
                AND i.slot = a.slot
				LEFT JOIN remote_descriptions AS d ON i.name = d.name AND i.category = d.category
                WHERE %s LIKE %s %s
                AND iv <> av
            ''' % (Sisyphus.applicationView, Sisyphus.searchTerm, noVirtual)),
        ])
        with sqlite3.connect(sisyphusDB) as db:
            cursor = db.cursor()
            cursor.execute('%s' % (self.SELECTS[Sisyphus.databaseView]))
            rows = cursor.fetchall()
            Sisyphus.pkgCount = len(rows)
            Sisyphus.pkgSelect = 0
            model = QtGui.QStandardItemModel(len(rows), 5)
            model.setHorizontalHeaderLabels(
                ['Category', 'Name', 'Installed Version', 'Available Version', 'Description'])
            for row in rows:
                indx = rows.index(row)
                for column in range(0, 5):
                    item = QtGui.QStandardItem("%s" % (row[column]))
                    model.setItem(indx, column, item)
            self.databaseTable.setModel(model)
            self.showPackageCount()

    def searchDatabase(self):
        search = self.inputBox.text()
        Sisyphus.searchTerm = "'%" + search + "%'"
        self.loadDatabase()

    def updateSystem(self):
        self.loadDatabase()
        self.statusBar().showMessage("I am syncing myself, hope to finish soon ...")
        self.updateThread.start()

    def packageInstall(self):
        indexes = self.databaseTable.selectionModel().selectedRows(1)
        if len(indexes) == 0:
            self.statusBar().showMessage("No package selected, please pick at least one!")
        else:
            Sisyphus.pkgList = []
            for index in sorted(indexes):
                Sisyphus.pkgList.append(index.data())
            self.statusBar().showMessage("I am installing requested package(s), please wait ...")
            self.installThread.start()

    def packageUninstall(self):
        indexes = self.databaseTable.selectionModel().selectedRows(1)
        if len(indexes) == 0:
            self.statusBar().showMessage("No package selected, please pick at least one!")
        else:
            Sisyphus.pkgList = []
            for index in sorted(indexes):
                Sisyphus.pkgList.append(index.data())
            self.statusBar().showMessage("I am removing requested package(s), please wait ...")
            self.uninstallThread.start()

    def systemUpgrade(self):
        self.statusBar().showMessage("I am upgrading the system, please be patient ...")
        self.upgradeThread.start()

    def orphansRemove(self):
        self.statusBar().showMessage("I am busy with some cleaning, please don't rush me ...")
        self.orphansThread.start()

    def jobDone(self):
        self.hideProgressBar()
        self.loadDatabase()

    def showProgressBar(self):
        self.hideButtons()
        self.progressBar.setRange(0, 0)
        self.progressBar.show()

    def hideProgressBar(self):
        self.progressBar.setRange(0, 1)
        self.progressBar.setValue(1)
        self.progressBar.hide()
        self.showButtons()

    def hideButtons(self):
        self.installButton.hide()
        self.uninstallButton.hide()
        self.orphansButton.hide()
        self.upgradeButton.hide()
        self.exitButton.hide()

    def showButtons(self):
        self.installButton.show()
        self.uninstallButton.show()
        self.orphansButton.show()
        self.upgradeButton.show()
        self.exitButton.show()

    def updateStatusBar(self, workerMessage):
        self.statusBar().showMessage(workerMessage)

    def showMirrorWindow(self):
        self.window = MirrorConfiguration()
        self.window.show()

    def showLicenseWindow(self):
        self.window = LicenseInformation()
        self.window.show()

    def sisyphusExit(self):
        self.close()


# mirror configuration window class
class MirrorConfiguration(QtWidgets.QMainWindow):
    def __init__(self):
        super(MirrorConfiguration, self).__init__()
        uic.loadUi('ui/mirrorcfg.ui', self)
        self.centerOnScreen()
        self.MIRRORLIST = getMirrors()
        self.updateMirrorList()
        self.applyButton.pressed.connect(self.mirrorCfgApply)
        self.applyButton.released.connect(self.mirrorCfgExit)
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
            if row['isActive']:
                self.ACTIVEMIRRORINDEX = indx
        self.mirrorCombo.setModel(model)
        self.mirrorCombo.setCurrentIndex(self.ACTIVEMIRRORINDEX)

    def setMirrorList(self):
        self.MIRRORLIST[self.ACTIVEMIRRORINDEX]['isActive'] = False
        self.ACTIVEMIRRORINDEX = self.mirrorCombo.currentIndex()
        self.MIRRORLIST[self.ACTIVEMIRRORINDEX]['isActive'] = True

    def mirrorCfgApply(self):
        setActiveMirror(self.MIRRORLIST)

    def mirrorCfgExit(self):
        self.close()


# license information window class
class LicenseInformation(QtWidgets.QMainWindow):
    def __init__(self):
        super(LicenseInformation, self).__init__()
        uic.loadUi('ui/license.ui', self)
        self.centerOnScreen()

    def centerOnScreen(self):
        resolution = QtWidgets.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2))


# worker/multithreading class
class MainWorker(QtCore.QObject):
    started = QtCore.pyqtSignal()
    finished = QtCore.pyqtSignal()
    strReady = QtCore.pyqtSignal(str)

    @QtCore.pyqtSlot()
    def startUpdate(self):
        self.started.emit()
        startUpdate()
        self.finished.emit()

    @QtCore.pyqtSlot()
    def startInstall(self):
        self.started.emit()
        pkgList = Sisyphus.pkgList
        portageExec = subprocess.Popen(
            ['emerge', '-q'] + pkgList, stdout=subprocess.PIPE)
        atexit.register(portageKill, portageExec)
        for portageOutput in io.TextIOWrapper(portageExec.stdout, encoding="utf-8"):
            self.strReady.emit(portageOutput.rstrip())
        syncLocalDatabase()
        self.finished.emit()

    @QtCore.pyqtSlot()
    def startUninstall(self):
        self.started.emit()
        pkgList = Sisyphus.pkgList
        portageExec = subprocess.Popen(
            ['emerge', '--depclean', '-q'] + pkgList, stdout=subprocess.PIPE)
        atexit.register(portageKill, portageExec)
        for portageOutput in io.TextIOWrapper(portageExec.stdout, encoding="utf-8"):
            self.strReady.emit(portageOutput.rstrip())
        syncLocalDatabase()
        self.finished.emit()

    @QtCore.pyqtSlot()
    def startUpgrade(self):
        self.started.emit()
        portageExec = subprocess.Popen(
            ['emerge', '-uDNq', '--backtrack=100', '--with-bdeps=y', '@world'], stdout=subprocess.PIPE)
        atexit.register(portageKill, portageExec)
        for portageOutput in io.TextIOWrapper(portageExec.stdout, encoding="utf-8"):
            self.strReady.emit(portageOutput.rstrip())
        syncLocalDatabase()
        self.finished.emit()

    @QtCore.pyqtSlot()
    def cleanOrphans(self):
        self.started.emit()
        portageExec = subprocess.Popen(
            ['emerge', '--depclean', '-q'], stdout=subprocess.PIPE)
        atexit.register(portageKill, portageExec)
        for portageOutput in io.TextIOWrapper(portageExec.stdout, encoding="utf-8"):
            self.strReady.emit(portageOutput.rstrip())
        syncLocalDatabase()
        self.finished.emit()


# launch application
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Sisyphus()
    sys.exit(app.exec_())
