#!/usr/bin/python3

import os
import sys
import sqlite3
import signal
import sisyphus
from collections import OrderedDict
from PyQt6 import QtCore, QtGui, QtWidgets, uic


class CenterMixin:
    def centerOnScreen(self):
        screenGeometry = QtGui.QGuiApplication.primaryScreen().geometry()
        windowGeometry = self.geometry()
        horizontalPosition = (screenGeometry.width() -
                              windowGeometry.width()) // 2
        verticalPosition = (screenGeometry.height() -
                            windowGeometry.height()) // 2
        self.move(horizontalPosition, verticalPosition)


class FirstRun(CenterMixin, QtWidgets.QDialog):
    finishedFirstRun = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.settingsWindow = None
        self.progressWindow = ProgressWindow(parent=None)
        self.progressWindow.hideButton.hide()
        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)
        uic.loadUi('/usr/share/sisyphus/ui/firstrun.ui', self)
        self.show()

        self.abortButton.clicked.connect(self.abortFirstRun)
        self.configureButton.clicked.connect(self.showSettingsWindow)

    def showProgress(self):
        self.abortButton.setEnabled(False)
        self.configureButton.setEnabled(False)
        if self.progressWindow:
            self.progressWindow.show()

    def hideProgress(self):
        self.abortButton.setEnabled(True)
        self.configureButton.setEnabled(True)
        if self.progressWindow:
            self.progressWindow.hide()

        self.finishedFirstRun.emit()
        self.close()

    def abortFirstRun(self):
        self.close()

    def showSettingsWindow(self):
        if self.settingsWindow is None or not self.settingsWindow.isVisible():
            self.settingsWindow = SettingsWindow(
                self, self.progressWindow, auto_show_progress=True, first_run=True)

            self.settingsWindow.showProgressRequested.connect(
                self.showProgress)
            self.settingsWindow.hideProgressRequested.connect(
                self.hideProgress)
            self.settingsWindow.destroyed.connect(self.onSettingsWindowClosed)

        self.settingsWindow.show()
        self.settingsWindow.raise_()
        self.settingsWindow.activateWindow()

    def onSettingsWindowClosed(self):
        self.settingsWindow = None


class Sisyphus(CenterMixin, QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.progressWindow = None
        self.settingsWindow = None
        uic.loadUi('/usr/share/sisyphus/ui/sisyphus.ui', self)
        signal.signal(signal.SIGTERM, self.handleSigterm)
        self.show()

        # Worker Threads
        self.updateWorker = MainWorker()
        self.updateThread = QtCore.QThread()
        self._setup_worker_thread(
            self.updateWorker, self.updateThread, self.updateWorker.startUpdate)

        self.installWorker = MainWorker()
        self.installThread = QtCore.QThread()
        self._setup_worker_thread(
            self.installWorker, self.installThread, self.installWorker.startInstall)

        self.uninstallWorker = MainWorker()
        self.uninstallThread = QtCore.QThread()
        self._setup_worker_thread(
            self.uninstallWorker, self.uninstallThread, self.uninstallWorker.startUninstall)

        self.upgradeWorker = MainWorker()
        self.upgradeThread = QtCore.QThread()
        self._setup_worker_thread(
            self.upgradeWorker, self.upgradeThread, self.upgradeWorker.startUpgrade)

        self.autoremoveWorker = MainWorker()
        self.autoremoveThread = QtCore.QThread()
        self._setup_worker_thread(
            self.autoremoveWorker, self.autoremoveThread, self.autoremoveWorker.startAutoremove)

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

        self.installButton.clicked.connect(self.packageInstall)
        self.uninstallButton.clicked.connect(self.packageUninstall)
        self.upgradeButton.clicked.connect(self.systemUpgrade)
        self.autoremoveButton.clicked.connect(self.autoRemove)
        self.exitButton.clicked.connect(self.closeMainWindow)

        self.updateSystem()

    def _setup_worker_thread(self, worker, thread, start_slot):
        worker.moveToThread(thread)
        worker.started.connect(self.showProgress)
        thread.started.connect(start_slot)
        thread.finished.connect(self.hideProgress)
        worker.finished.connect(thread.quit)

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
        filter_val = Sisyphus.dbFilter
        cat = '%' + self.inputBox.text() + \
            '%' if self.applicationFilter.currentText() == 'Package Category' else ''
        pn = '%' + self.inputBox.text() + \
            '%' if self.applicationFilter.currentText() == 'Package Name' else ''
        desc = '%' + self.inputBox.text() + \
            '%' if self.applicationFilter.currentText() == 'Package Description' else ''

        query = sisyphus.querydb.start(filter_val, cat, pn, desc)
        with sqlite3.connect(sisyphus.getfs.lcl_db) as db:
            cursor = db.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            Sisyphus.pkgCount = len(rows)
            Sisyphus.pkgSelect = 0
            model = QtGui.QStandardItemModel(len(rows), 6)
            model.setHorizontalHeaderLabels(
                ['Package Category', 'Package Name', 'SLOT', 'Installed Version', 'Available Version', 'Package Description'])
            for indx, row in enumerate(rows):
                for column in range(6):
                    item = QtGui.QStandardItem(str(row[column]))
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
        selected_pkgs = [
            f"{pkg_categs[i]['cat']}/{pkg_names[i]['name']}:{pkg_slots[i]['slot']}" for i in range(len(pkg_categs))]
        return selected_pkgs

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

    def setProgressBarVisible(self, visible):
        self.progressBar.setRange(0, 0 if visible else 1)
        if visible:
            self.progressBar.show()
        else:
            self.progressBar.hide()

    def setUiButtonsVisible(self, visible):
        for btn in (self.installButton, self.uninstallButton, self.autoremoveButton, self.upgradeButton, self.exitButton):
            btn.setVisible(visible)

    def setButtonEnabled(self, button, enabled):
        button.setEnabled(enabled)

    def showProgress(self):
        self.setUiButtonsVisible(False)
        self.setButtonEnabled(self.settingsButton, False)
        self.setButtonEnabled(self.progressButton, True)
        self.setProgressBarVisible(True)
        self.inputBox.setFocus()

    def hideProgress(self):
        self.setUiButtonsVisible(True)
        self.setButtonEnabled(self.settingsButton, True)
        self.setButtonEnabled(self.progressButton, False)
        self.setProgressBarVisible(False)
        self.inputBox.setFocus()
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

    def connectSettingsWindowSignals(self, settings_window):
        settings_window.showProgressRequested.connect(self.showProgress)
        settings_window.hideProgressRequested.connect(self.hideProgress)
        settings_window.updateSystemRequested.connect(self.updateSystem)
        settings_window.destroyed.connect(self.onSettingsWindowClosed)

    def showSettingsWindow(self):
        if self.settingsWindow is None or not self.settingsWindow.isVisible():
            self.settingsWindow = SettingsWindow(
                self, self.progressWindow, auto_show_progress=False, first_run=False)
            self.connectSettingsWindowSignals(self.settingsWindow)
        self.settingsWindow.show()
        self.settingsWindow.raise_()
        self.settingsWindow.activateWindow()

    def onSettingsWindowClosed(self):
        self.settingsWindow = None

    def closeMainWindow(self):
        self.close()

    def handleSigterm(self, signum, frame):
        self.close()

    def __del__(self):
        sys.stdout = sys.__stdout__


class ProgressWindow(CenterMixin, QtWidgets.QMainWindow):
    progress_messages = []

    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('/usr/share/sisyphus/ui/progress.ui', self)
        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)
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


class SettingsWindow(CenterMixin, QtWidgets.QMainWindow):
    showProgressRequested = QtCore.pyqtSignal()
    hideProgressRequested = QtCore.pyqtSignal()
    updateSystemRequested = QtCore.pyqtSignal()

    def __init__(self, parent=None, progressWindow=None, auto_show_progress=False, first_run=False):
        super().__init__(parent)
        self.progressWindow = progressWindow
        self.auto_show_progress = auto_show_progress
        self.first_run = first_run
        uic.loadUi('/usr/share/sisyphus/ui/settings.ui', self)

        self.MIRRORLIST = sisyphus.setmirror.getList()
        self.updateMirrorList()
        self.mirrorCombo.activated.connect(self.setMirrorList)

        self.branches = OrderedDict([
            ('Branch Master (stable)', 'master'),
            ('Branch Next (testing)', 'next')
        ])

        self.branchCombo.blockSignals(True)
        self.branchCombo.addItems(self.branches.keys())
        self.branchCombo.setCurrentText('master')
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

    def showProgress(self):
        self.showProgressRequested.emit()
        if self.progressWindow is None:
            self.progressWindow = ProgressWindow(None)
            self.branchWorker.workerOutput.connect(
                self.progressWindow.updateProgressWindow)

        if self.auto_show_progress and self.progressWindow is not None:
            self.progressWindow.show()
        self.close()

    def hideProgress(self):
        self.hideProgressRequested.emit()
        self.updateSystemRequested.emit()
        self.MIRRORLIST = sisyphus.setmirror.getList()
        self.updateMirrorList()
        if self.first_run and self.progressWindow is not None:
            self.progressWindow.hide()


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

    if not sisyphus.getmarkers.markers_exist():
        first_run = FirstRun()

        def launch_main():
            global window
            window = Sisyphus()
            window.inputBox.setFocus()
            window.show()

        first_run.finishedFirstRun.connect(launch_main)
        window = first_run
    else:
        window = Sisyphus()
        window.inputBox.setFocus()

    sys.exit(app.exec())
