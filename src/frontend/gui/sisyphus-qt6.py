#!/usr/bin/python3

import sys
import sqlite3
import sisyphus
from collections import OrderedDict
from PyQt6 import QtCore, QtGui, QtWidgets, uic


class Sisyphus(QtWidgets.QMainWindow):
    def __init__(self):
        super(Sisyphus, self).__init__()
        uic.loadUi('/usr/share/sisyphus/ui/sisyphus.ui', self)
        self.centerOnScreen()
        self.show()

        self.filterApplications = OrderedDict([
            ('Package Name', 'pn'),
            ('Package Category', 'cat'),
            ('Package Description', 'descr')
        ])
        self.applicationFilter.addItems(self.filterApplications.keys())
        self.applicationFilter.setCurrentText('Package Name')
        self.applicationFilter.currentIndexChanged.connect(
            self.setApplicationFilter)
        Sisyphus.appFilter = self.filterApplications['Package Name']

        self.filterDatabases = OrderedDict([
            ('All Packages', 'all'),
            ('Installed Packages', 'installed'),
            ('Alien Packages', 'alien'),
            ('Available Packages', 'available'),
            ('Upgradable Packages', 'upgradable')
        ])
        self.databaseFilter.addItems(self.filterDatabases.keys())
        self.databaseFilter.setCurrentText('All Packages')
        self.databaseFilter.currentIndexChanged.connect(self.setDatabaseFilter)
        Sisyphus.dbFilter = self.filterDatabases['All Packages']

        Sisyphus.searchTerm = "'%%'"

        self.databaseTable.clicked.connect(self.rowClicked)

        self.inputBox.textEdited.connect(self.searchDatabase)

        self.settingsButton.clicked.connect(self.showMirrorWindow)
        self.licenseButton.clicked.connect(self.showLicenseWindow)

        sys.stdout = MainWorker(
            workerOutput=self.updateProgress)  # capture stdout

        self.updateWorker = MainWorker()
        self.updateThread = QtCore.QThread()
        self.updateWorker.moveToThread(self.updateThread)
        self.updateWorker.started.connect(self.showProgress)
        self.updateThread.started.connect(self.updateWorker.startUpdate)
        self.updateThread.finished.connect(self.hideProgress)
        self.updateWorker.finished.connect(self.updateThread.quit)

        self.installButton.clicked.connect(self.packageInstall)
        self.installWorker = MainWorker()
        self.installThread = QtCore.QThread()
        self.installWorker.moveToThread(self.installThread)
        self.installWorker.started.connect(self.showProgress)
        self.installThread.started.connect(self.installWorker.startInstall)
        self.installWorker.workerOutput.connect(self.updateProgress)
        self.installThread.finished.connect(self.hideProgress)
        self.installWorker.finished.connect(self.installThread.quit)

        self.uninstallButton.clicked.connect(self.packageUninstall)
        self.uninstallWorker = MainWorker()
        self.uninstallThread = QtCore.QThread()
        self.uninstallWorker.moveToThread(self.uninstallThread)
        self.uninstallWorker.started.connect(self.showProgress)
        self.uninstallThread.started.connect(
            self.uninstallWorker.startUninstall)
        self.uninstallWorker.workerOutput.connect(self.updateProgress)
        self.uninstallThread.finished.connect(self.hideProgress)
        self.uninstallWorker.finished.connect(self.uninstallThread.quit)

        self.upgradeButton.clicked.connect(self.systemUpgrade)
        self.upgradeWorker = MainWorker()
        self.upgradeThread = QtCore.QThread()
        self.upgradeWorker.moveToThread(self.upgradeThread)
        self.upgradeWorker.started.connect(self.showProgress)
        self.upgradeThread.started.connect(self.upgradeWorker.startUpgrade)
        self.upgradeWorker.workerOutput.connect(self.updateProgress)
        self.upgradeThread.finished.connect(self.hideProgress)
        self.upgradeWorker.finished.connect(self.upgradeThread.quit)

        self.autoremoveButton.clicked.connect(self.autoRemove)
        self.autoremoveWorker = MainWorker()
        self.autoremoveThread = QtCore.QThread()
        self.autoremoveWorker.moveToThread(self.autoremoveThread)
        self.autoremoveWorker.started.connect(self.showProgress)
        self.autoremoveThread.started.connect(
            self.autoremoveWorker.startAutoremove)
        self.autoremoveWorker.workerOutput.connect(self.updateProgress)
        self.autoremoveThread.finished.connect(self.hideProgress)
        self.autoremoveWorker.finished.connect(self.autoremoveThread.quit)

        self.updateSystem()
        self.progressBar.hide()
        self.progressBox.hide()

        self.exitButton.clicked.connect(self.sisyphusExit)

    def centerOnScreen(self):
        screenGeometry = QtGui.QGuiApplication.primaryScreen().geometry()
        windowGeometry = self.geometry()
        horizontalPosition = int(
            (screenGeometry.width() - windowGeometry.width()) / 2)
        verticalPosition = int(
            (screenGeometry.height() - windowGeometry.height()) / 2)
        self.move(horizontalPosition, verticalPosition)

    def rowClicked(self):
        Sisyphus.pkgSelect = len(
            self.databaseTable.selectionModel().selectedRows())
        self.showPackageCount()

    def showPackageCount(self):
        self.statusBar().showMessage("Found: %d, Selected: %d packages" %
                                     (Sisyphus.pkgCount, Sisyphus.pkgSelect))

    def setApplicationFilter(self):
        Sisyphus.appFilter = self.filterApplications[self.applicationFilter.currentText(
        )]
        self.loadDatabase()

    def setDatabaseFilter(self):
        Sisyphus.dbFilter = self.filterDatabases[self.databaseFilter.currentText(
        )]
        Sisyphus.SELECT = self.databaseFilter.currentText()
        self.loadDatabase()

    def loadDatabase(self):
        filter = Sisyphus.dbFilter
        cat = '%' + self.inputBox.text() + '%' if self.applicationFilter.currentText() == 'Package Category' else ''
        pn = '%' + self.inputBox.text() + '%' if self.applicationFilter.currentText() == 'Package Name' else ''
        desc = '%' + self.inputBox.text() + '%' if self.applicationFilter.currentText() == 'Package Description' else ''

        query = sisyphus.querydb.start(filter, cat, pn, desc)
        with sqlite3.connect(sisyphus.getfs.lcl_db) as db:
            cursor = db.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            Sisyphus.pkgCount = len(rows)
            Sisyphus.pkgSelect = 0
            model = QtGui.QStandardItemModel(len(rows), 5)
            model.setHorizontalHeaderLabels(
                ['Package Category', 'Package Name', 'Installed Version', 'Available Version', 'Package Description'])
            for row in rows:
                indx = rows.index(row)
                for column in range(0, 5):
                    item = QtGui.QStandardItem("%s" % (row[column]))
                    model.setItem(indx, column, item)
            self.databaseTable.setModel(model)
            self.showPackageCount()

    def searchDatabase(self):
        Sisyphus.searchTerm = "'%" + self.inputBox.text() + "%'"
        self.loadDatabase()

    def updateSystem(self):
        self.loadDatabase()
        self.statusBar().showMessage("I am syncing myself, hope to finish soon ...")
        self.updateThread.start()

    def getSelectedPackages(self):
        def byRow(e):
            return e['row']

        pkg_categs = [{'row': pkg.row(), 'cat': pkg.data()}
                      for pkg in self.databaseTable.selectionModel().selectedRows(0)]
        pkg_names = [{'row': pkg.row(), 'name': pkg.data()}
                     for pkg in self.databaseTable.selectionModel().selectedRows(1)]
        pkg_categs = sorted(pkg_categs, key=byRow)
        pkg_names = sorted(pkg_names, key=byRow)
        selected_pkgs = [pkg_categs[i]['cat'] + '/' +
                         pkg_names[i]['name'] for i in range(len(pkg_categs))]
        return (selected_pkgs)

    def packageInstall(self):
        if not self.databaseTable.selectionModel().hasSelection():
            self.statusBar().showMessage("No package selected, please pick at least one!")
        else:
            Sisyphus.pkgname = self.getSelectedPackages()
            self.statusBar().showMessage("I am installing requested package(s), please wait ...")
            self.installThread.start()

    def packageUninstall(self):
        if not self.databaseTable.selectionModel().hasSelection():
            self.statusBar().showMessage("No package selected, please pick at least one!")
        else:
            Sisyphus.pkgname = self.getSelectedPackages()
            self.statusBar().showMessage("I am removing requested package(s), please wait ...")
            self.uninstallThread.start()

    def systemUpgrade(self):
        self.statusBar().showMessage("I am upgrading the system, please be patient ...")
        self.upgradeThread.start()

    def autoRemove(self):
        self.statusBar().showMessage("I am busy with some cleaning, please don't rush me ...")
        self.autoremoveThread.start()

    def enableUiInput(self):
        self.databaseTable.show()
        self.installButton.setEnabled(True)
        self.uninstallButton.setEnabled(True)
        self.autoremoveButton.setEnabled(True)
        self.upgradeButton.setEnabled(True)
        self.exitButton.setEnabled(True)
        self.licenseButton.setEnabled(True)
        self.settingsButton.setEnabled(True)
        self.applicationFilter.setEnabled(True)
        self.databaseFilter.setEnabled(True)
        self.inputBox.setEnabled(True)
        self.label1.setEnabled(True)
        self.label2.setEnabled(True)

    def disableUiInput(self):
        self.databaseTable.hide()
        self.installButton.setEnabled(False)
        self.uninstallButton.setEnabled(False)
        self.autoremoveButton.setEnabled(False)
        self.upgradeButton.setEnabled(False)
        self.exitButton.setEnabled(False)
        self.licenseButton.setEnabled(False)
        self.settingsButton.setEnabled(False)
        self.applicationFilter.setEnabled(False)
        self.databaseFilter.setEnabled(False)
        self.inputBox.setEnabled(False)
        self.label1.setEnabled(False)
        self.label2.setEnabled(False)

    def showProgressBar(self):
        self.progressBar.setRange(0, 0)
        self.progressBar.show()

    def hideProgressBar(self):
        self.progressBar.setRange(0, 1)
        self.progressBar.setValue(1)
        self.progressBar.hide()

    def clearProgressBox(self):
        self.progressBox.clear()

    def showProgressBox(self):
        self.progressBox.show()

    def hideProgressBox(self):
        self.progressBox.hide()

    def setInputFocus(self):
        self.inputBox.setFocus()

    def showProgress(self):
        self.disableUiInput()
        self.showProgressBar()
        self.showProgressBox()
        self.clearProgressBox()
        self.setInputFocus()

    def hideProgress(self):
        self.enableUiInput()
        self.hideProgressBar()
        self.hideProgressBox()
        self.loadDatabase()
        self.setInputFocus()

    def updateProgress(self, workerMessage):
        self.progressBox.insertPlainText(workerMessage)
        self.progressBox.ensureCursorVisible()

    def showMirrorWindow(self):
        self.window = MirrorConfiguration()
        self.window.show()

    def showLicenseWindow(self):
        self.window = LicenseInformation()
        self.window.show()

    def sisyphusExit(self):
        self.close()

    def __del__(self):
        sys.stdout = sys.__stdout__  # restore stdout

# mirror configuration window


class MirrorConfiguration(QtWidgets.QMainWindow):
    def __init__(self):
        super(MirrorConfiguration, self).__init__()
        uic.loadUi('/usr/share/sisyphus/ui/mirrorcfg.ui', self)
        self.centerOnScreen()
        self.MIRRORLIST = sisyphus.setmirror.getList()
        self.updateMirrorList()
        self.applyButton.pressed.connect(self.mirrorCfgApply)
        self.applyButton.released.connect(self.mirrorCfgExit)
        self.mirrorCombo.activated.connect(self.setMirrorList)

    def centerOnScreen(self):
        screenGeometry = QtGui.QGuiApplication.primaryScreen().geometry()
        windowGeometry = self.geometry()
        horizontalPosition = int(
            (screenGeometry.width() - windowGeometry.width()) / 2)
        verticalPosition = int(
            (screenGeometry.height() - windowGeometry.height()) / 2)
        self.move(horizontalPosition, verticalPosition)

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
        sisyphus.setmirror.writeList(self.MIRRORLIST)

    def mirrorCfgExit(self):
        self.close()


# license information window
class LicenseInformation(QtWidgets.QMainWindow):
    def __init__(self):
        super(LicenseInformation, self).__init__()
        uic.loadUi('/usr/share/sisyphus/ui/license.ui', self)
        self.centerOnScreen()

    def centerOnScreen(self):
        screenGeometry = QtGui.QGuiApplication.primaryScreen().geometry()
        windowGeometry = self.geometry()
        horizontalPosition = int(
            (screenGeometry.width() - windowGeometry.width()) / 2)
        verticalPosition = int(
            (screenGeometry.height() - windowGeometry.height()) / 2)
        self.move(horizontalPosition, verticalPosition)


# worker/multithreading class
class MainWorker(QtCore.QObject):
    started = QtCore.pyqtSignal()
    finished = QtCore.pyqtSignal()
    workerOutput = QtCore.pyqtSignal(str)

    def write(self, text):
        self.workerOutput.emit(str(text))

    def flush(self):
        pass

    def fileno(self):
        return 0

    @QtCore.pyqtSlot()
    def startUpdate(self):
        self.started.emit()
        sisyphus.setjobs.start()
        sisyphus.syncall.start.__wrapped__(gfx_ui=True)  # undecorate
        self.finished.emit()

    @QtCore.pyqtSlot()
    def startInstall(self):
        self.started.emit()
        pkgname = Sisyphus.pkgname
        sisyphus.pkgadd.start(
            pkgname, ebuild=False, gfx_ui=True, oneshot=False, nodeps=False)
        self.finished.emit()

    @QtCore.pyqtSlot()
    def startUninstall(self):
        self.started.emit()
        pkgname = Sisyphus.pkgname
        sisyphus.pkgremove.start(
            pkgname, depclean=True, gfx_ui=True, unmerge=False)
        self.finished.emit()

    @QtCore.pyqtSlot()
    def startUpgrade(self):
        self.started.emit()
        sisyphus.sysupgrade.start(ebuild=False, gfx_ui=True)
        self.finished.emit()

    @QtCore.pyqtSlot()
    def startAutoremove(self):
        self.started.emit()
        sisyphus.sysclean.start(gfx_ui=True)
        self.finished.emit()


# launch application
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Breeze')
    window = Sisyphus()
    window.inputBox.setFocus()
    sys.exit(app.exec())
