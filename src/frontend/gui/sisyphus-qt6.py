#!/usr/bin/python3

import sys
import sqlite3
import signal
import sisyphus
from collections import OrderedDict
from PyQt6 import QtCore, QtGui, QtWidgets, uic


class Sisyphus(QtWidgets.QMainWindow):
    def __init__(self):
        super(Sisyphus, self).__init__()
        self.progressWindow = None
        self.settingsWindow = None
        uic.loadUi('/usr/share/sisyphus/ui/sisyphus.ui', self)
        signal.signal(signal.SIGTERM, self.handleSigterm)
        self.centerOnScreen()
        self.show()

        def setupWorkerThread(worker, thread, start_slot):
            worker.moveToThread(thread)
            worker.started.connect(self.showProgress)
            thread.started.connect(start_slot)
            thread.finished.connect(self.hideProgress)
            worker.finished.connect(thread.quit)

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
        self.progressButton.clicked.connect(self.showProgressWindow)
        self.settingsButton.clicked.connect(self.showSettingsWindow)

        self.updateWorker = MainWorker()
        self.updateThread = QtCore.QThread()
        setupWorkerThread(self.updateWorker, self.updateThread,
                          self.updateWorker.startUpdate)

        self.installButton.clicked.connect(self.packageInstall)
        self.installWorker = MainWorker()
        self.installThread = QtCore.QThread()
        setupWorkerThread(self.installWorker, self.installThread,
                          self.installWorker.startInstall)

        self.uninstallButton.clicked.connect(self.packageUninstall)
        self.uninstallWorker = MainWorker()
        self.uninstallThread = QtCore.QThread()
        setupWorkerThread(self.uninstallWorker, self.uninstallThread,
                          self.uninstallWorker.startUninstall)

        self.upgradeButton.clicked.connect(self.systemUpgrade)
        self.upgradeWorker = MainWorker()
        self.upgradeThread = QtCore.QThread()
        setupWorkerThread(self.upgradeWorker, self.upgradeThread,
                          self.upgradeWorker.startUpgrade)

        self.autoremoveButton.clicked.connect(self.autoRemove)
        self.autoremoveWorker = MainWorker()
        self.autoremoveThread = QtCore.QThread()
        setupWorkerThread(self.autoremoveWorker, self.autoremoveThread,
                          self.autoremoveWorker.startAutoremove)

        self.updateSystem()

        self.exitButton.clicked.connect(self.closeMainWindow)

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
        cat = '%' + self.inputBox.text() + \
            '%' if self.applicationFilter.currentText() == 'Package Category' else ''
        pn = '%' + self.inputBox.text() + \
            '%' if self.applicationFilter.currentText() == 'Package Name' else ''
        desc = '%' + self.inputBox.text() + \
            '%' if self.applicationFilter.currentText() == 'Package Description' else ''

        query = sisyphus.querydb.start(filter, cat, pn, desc)
        with sqlite3.connect(sisyphus.getfs.lcl_db) as db:
            cursor = db.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            Sisyphus.pkgCount = len(rows)
            Sisyphus.pkgSelect = 0
            model = QtGui.QStandardItemModel(len(rows), 6)
            model.setHorizontalHeaderLabels(
                ['Package Category', 'Package Name', 'SLOT', 'Installed Version', 'Available Version', 'Package Description'])
            for row in rows:
                indx = rows.index(row)
                for column in range(0, 6):
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
        pkg_slots = [{'row': pkg.row(), 'slot': pkg.data()}
                     for pkg in self.databaseTable.selectionModel().selectedRows(2)]
        pkg_categs = sorted(pkg_categs, key=byRow)
        pkg_names = sorted(pkg_names, key=byRow)
        pkg_slots = sorted(pkg_slots, key=byRow)
        selected_pkgs = [pkg_categs[i]['cat'] + '/' + pkg_names[i]['name'] +
                         ':' + pkg_slots[i]['slot'] for i in range(len(pkg_categs))]
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

    def disableProgressButton(self):
        self.progressButton.setEnabled(False)

    def enableProgressButton(self):
        self.progressButton.setEnabled(True)

    def disableSettingsButton(self):
        self.settingsButton.setEnabled(False)

    def enableSettingsButton(self):
        self.settingsButton.setEnabled(True)

    def hideUiButtons(self):
        self.installButton.hide()
        self.uninstallButton.hide()
        self.autoremoveButton.hide()
        self.upgradeButton.hide()
        self.exitButton.hide()

    def showUiButtons(self):
        self.installButton.show()
        self.uninstallButton.show()
        self.autoremoveButton.show()
        self.upgradeButton.show()
        self.exitButton.show()

    def hideProgressBar(self):
        self.progressBar.setRange(0, 1)
        self.progressBar.setValue(1)
        self.progressBar.hide()

    def showProgressBar(self):
        self.progressBar.setRange(0, 0)
        self.progressBar.show()

    def setInputFocus(self):
        self.inputBox.setFocus()

    def showProgress(self):
        self.hideUiButtons()
        self.disableSettingsButton()
        self.enableProgressButton()
        self.showProgressBar()
        self.setInputFocus()

    def hideProgress(self):
        self.showUiButtons()
        self.enableSettingsButton()
        self.disableProgressButton()
        self.hideProgressBar()
        self.setInputFocus()
        self.loadDatabase()

    def showProgressWindow(self):
        if self.progressWindow is None:
            self.progressWindow = ProgressWindow(self)

            self.installWorker.workerOutput.connect(
                self.progressWindow.updateProgressWindow)
            self.uninstallWorker.workerOutput.connect(
                self.progressWindow.updateProgressWindow)
            self.upgradeWorker.workerOutput.connect(
                self.progressWindow.updateProgressWindow)
            self.autoremoveWorker.workerOutput.connect(
                self.progressWindow.updateProgressWindow)

        self.progressWindow.show()

    def showSettingsWindow(self):
        if self.settingsWindow is None:
            self.settingsWindow = SettingsWindow(self, self.progressWindow)

            self.settingsWindow.showProgressRequested.connect(
                self.showProgress)
            self.settingsWindow.hideProgressRequested.connect(
                self.hideProgress)
            self.settingsWindow.updateSystemRequested.connect(
                self.updateSystem)

        self.settingsWindow.show()

    def closeMainWindow(self):
        self.close()

    def handleSigterm(self, signum, frame):
        self.close()

    def __del__(self):
        sys.stdout = sys.__stdout__

    def centerOnScreen(self):
        screenGeometry = QtGui.QGuiApplication.primaryScreen().geometry()
        windowGeometry = self.geometry()
        horizontalPosition = int(
            (screenGeometry.width() - windowGeometry.width()) / 2)
        verticalPosition = int(
            (screenGeometry.height() - windowGeometry.height()) / 2)
        self.move(horizontalPosition, verticalPosition)


class ProgressWindow(QtWidgets.QMainWindow):
    progress_messages = []

    def __init__(self, parent=None):
        super(ProgressWindow, self).__init__(parent)
        uic.loadUi('/usr/share/sisyphus/ui/progress.ui', self)
        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)
        self.centerOnScreen()
        self.refreshProgressWindow()

        self.clearButton.clicked.connect(self.clearProgressWindow)
        self.hideButton.clicked.connect(self.hideProgressWindow)

        sys.stdout = MainWorker(workerOutput=self.updateProgressWindow)

    def updateProgressWindow(self, workerMessage):
        ProgressWindow.progress_messages.append(workerMessage)
        self.progressBox.insertPlainText(workerMessage)
        self.progressBox.ensureCursorVisible()

    def refreshProgressWindow(self):
        self.progressBox.clear()
        self.progressBox.setPlainText(
            ''.join(ProgressWindow.progress_messages))
        self.progressBox.ensureCursorVisible()

    def clearProgressWindow(self):
        self.progressBox.clear()
        ProgressWindow.progress_messages.clear()

    def hideProgressWindow(self):
        self.hide()

    def centerOnScreen(self):
        screenGeometry = QtGui.QGuiApplication.primaryScreen().geometry()
        windowGeometry = self.geometry()
        horizontalPosition = int(
            (screenGeometry.width() - windowGeometry.width()) / 2)
        verticalPosition = int(
            (screenGeometry.height() - windowGeometry.height()) / 2)
        self.move(horizontalPosition, verticalPosition)


class SettingsWindow(QtWidgets.QMainWindow):
    showProgressRequested = QtCore.pyqtSignal()
    hideProgressRequested = QtCore.pyqtSignal()
    updateSystemRequested = QtCore.pyqtSignal()

    def __init__(self, parent=None, progressWindow=None):
        super(SettingsWindow, self).__init__(parent)
        self.progressWindow = progressWindow
        selected_branch = None
        selected_remote = None
        uic.loadUi('/usr/share/sisyphus/ui/settings.ui', self)
        self.centerOnScreen()

        self.MIRRORLIST = sisyphus.setmirror.getList()
        self.updateMirrorList()
        self.mirrorCombo.activated.connect(self.setMirrorList)

        self.branches = OrderedDict([
            ('Branch Master (stable)', 'master'),
            ('Branch Next (testing)', 'next')
        ])

        self.branchCombo.blockSignals(True)
        self.branchCombo.addItems(self.branches.keys())
        system_branch = sisyphus.getenv.sys_brch()
        self.branchCombo.setCurrentText(next(name for name, value in self.branches.items(
        ) if value == system_branch))  # default to current branch, we have an API for it
        self.branchCombo.blockSignals(False)
        self.branchCombo.currentIndexChanged.connect(self.loadBranchRemote)

        self.remotes = OrderedDict([
            ('Github Remote : https://github.com/redcorelinux', 'github'),
            ('Gitlab Remote : https://gitlab.com/redcore', 'gitlab'),
            ('Pagure Remote : https://pagure.io/redcore', 'pagure')
        ])

        self.remoteCombo.blockSignals(True)
        self.remoteCombo.addItems(self.remotes.keys())
        self.remoteCombo.setCurrentText(
            'Gitlab Remote : https://gitlab.com/redcore')
        self.remoteCombo.blockSignals(False)
        self.remoteCombo.currentIndexChanged.connect(self.loadBranchRemote)

        self.mirrorButton.clicked.connect(self.writeMirrorList)
        self.branchButton.clicked.connect(self.changeBranchRemote)

        self.branchWorker = MainWorker()
        self.branchThread = QtCore.QThread()
        self.branchWorker.moveToThread(self.branchThread)
        self.branchWorker.started.connect(self.showProgress)
        self.branchThread.started.connect(self.branchWorker.setBranch)
        self.branchThread.finished.connect(self.hideProgress)
        self.branchWorker.finished.connect(self.branchThread.quit)

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

    def writeMirrorList(self):
        sisyphus.setmirror.writeList(self.MIRRORLIST)

    def loadBranchRemote(self):
        selected_branch = self.branches[self.branchCombo.currentText()]
        selected_remote = self.remotes[self.remoteCombo.currentText()]

        return selected_branch, selected_remote

    def changeBranchRemote(self):
        selected_branch, selected_remote = self.loadBranchRemote()

        self.branchWorker.selected_branch = selected_branch
        self.branchWorker.selected_remote = selected_remote

        self.branchThread.start()

    def disableUiButtons(self):
        self.mirrorButton.setEnabled(False)
        self.branchButton.setEnabled(False)

    def enableUiButtons(self):
        self.mirrorButton.setEnabled(True)
        self.branchButton.setEnabled(True)

    def showProgress(self):
        self.disableUiButtons()
        self.showProgressRequested.emit()

        if self.progressWindow is None:
            self.progressWindow = ProgressWindow(self)
            self.branchWorker.workerOutput.connect(
                self.progressWindow.updateProgressWindow)

    def hideProgress(self):
        self.hideProgressRequested.emit()
        self.updateSystemRequested.emit()
        self.MIRRORLIST = sisyphus.setmirror.getList()
        self.updateMirrorList()
        self.enableUiButtons()

    def centerOnScreen(self):
        screenGeometry = QtGui.QGuiApplication.primaryScreen().geometry()
        windowGeometry = self.geometry()
        horizontalPosition = int(
            (screenGeometry.width() - windowGeometry.width()) / 2)
        verticalPosition = int(
            (screenGeometry.height() - windowGeometry.height()) / 2)
        self.move(horizontalPosition, verticalPosition)


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
        sisyphus.pkgadd.start(pkgname, ebuild=False, gfx_ui=True,
                              oneshot=False, nodeps=False, onlydeps=False)
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
        sisyphus.sysclean.start(depclean=True, gfx_ui=True)
        self.finished.emit()

    @QtCore.pyqtSlot()
    def setBranch(self):
        self.started.emit()
        sisyphus.setbranch.start(self.selected_branch,
                                 self.selected_remote, gfx_ui=True)
        self.finished.emit()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Breeze')
    window = Sisyphus()
    window.inputBox.setFocus()
    sys.exit(app.exec())
