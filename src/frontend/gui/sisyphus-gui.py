#!/usr/bin/python3
import sys
import subprocess
import sqlite3
import io
import atexit
from collections import OrderedDict
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from libsisyphus import *
from sisyphusconfig import SisyphusConfig


class Sisyphus(QtWidgets.QMainWindow):
    def __init__(self):
        super(Sisyphus, self).__init__()
        uic.loadUi('ui/sisyphus-gui.ui', self)
        self.centerOnScreen()
        self.show()

        self.filterApplications = OrderedDict([
            ('Search by Name', 'pn'),
            ('Search by Category', 'cat'),
            ('Search by Description', 'descr')
        ])
        self.applicationFilter.addItems(self.filterApplications.keys())
        self.applicationFilter.setCurrentText('Search by Name')
        self.applicationFilter.currentIndexChanged.connect(self.setApplicationFilter)
        Sisyphus.applicationView = self.filterApplications['Search by Name']

        self.filterDatabases = OrderedDict([
            ('All Packages', 'all'),
            ('Installed Packages', 'instaled'),
            ('Installable Packages', 'installable'),
            ('Safely Removable Packages', 'removable'),
            ('Upgradable/Rebuilt Packages', 'upgradable')
        ])
        self.databaseFilter.addItems(self.filterDatabases.keys())
        self.databaseFilter.setCurrentText('All Packages')
        self.databaseFilter.currentIndexChanged.connect(self.setDatabaseFilter)
        Sisyphus.databaseView = self.filterDatabases['All Packages']

        Sisyphus.searchTerm = "'%%'"

        self.databaseTable.clicked.connect(self.rowClicked)

        self.inputBox.textEdited.connect(self.searchDatabase)

        self.settingsButton.clicked.connect(self.sisyphusSettings)

        self.updateWorker = UpdateWorker()
        self.updateThread = QtCore.QThread()
        self.updateWorker.moveToThread(self.updateThread)
        self.updateWorker.started.connect(self.showProgressBar)
        self.updateWorker.finished.connect(self.updateThread.quit)
        self.updateThread.started.connect(self.updateWorker.startUpdate)
        self.updateThread.finished.connect(self.jobDone)

        self.installButton.clicked.connect(self.packageInstall)
        self.installWorker = InstallWorker()
        self.installThread = QtCore.QThread()
        self.installWorker.moveToThread(self.installThread)
        self.installWorker.started.connect(self.showProgressBar)
        self.installWorker.strReady.connect(self.updateStatusBar)
        self.installWorker.finished.connect(self.installThread.quit)
        self.installThread.started.connect(self.installWorker.startInstall)
        self.installThread.finished.connect(self.jobDone)

        self.uninstallButton.clicked.connect(self.packageUninstall)
        self.uninstallWorker = UninstallWorker()
        self.uninstallThread = QtCore.QThread()
        self.uninstallWorker.moveToThread(self.uninstallThread)
        self.uninstallWorker.started.connect(self.showProgressBar)
        self.uninstallWorker.strReady.connect(self.updateStatusBar)
        self.uninstallWorker.finished.connect(self.uninstallThread.quit)
        self.uninstallThread.started.connect(
            self.uninstallWorker.startUninstall)
        self.uninstallThread.finished.connect(self.jobDone)

        self.upgradeButton.clicked.connect(self.systemUpgrade)
        self.upgradeWorker = UpgradeWorker()
        self.upgradeThread = QtCore.QThread()
        self.upgradeWorker.moveToThread(self.upgradeThread)
        self.upgradeWorker.started.connect(self.showProgressBar)
        self.upgradeWorker.strReady.connect(self.updateStatusBar)
        self.upgradeWorker.finished.connect(self.upgradeThread.quit)
        self.upgradeThread.started.connect(self.upgradeWorker.startUpgrade)
        self.upgradeThread.finished.connect(self.jobDone)

        self.orphansButton.clicked.connect(self.orphansRemove)
        self.orphansWorker = OrphansWorker()
        self.orphansThread = QtCore.QThread()
        self.orphansWorker.moveToThread(self.orphansThread)
        self.orphansWorker.started.connect(self.showProgressBar)
        self.orphansWorker.strReady.connect(self.updateStatusBar)
        self.orphansWorker.finished.connect(self.orphansThread.quit)
        self.orphansThread.started.connect(self.orphansWorker.cleanOrphans)
        self.orphansThread.finished.connect(self.jobDone)

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
                IFNULL(a.version, 'None') AS av,
                i.version AS iv,
                i.description AS descr
                FROM local_packages AS i LEFT OUTER JOIN remote_packages as a
                ON i.category = a.category
                AND i.name = a.name
                AND i.slot = a.slot
                WHERE %s LIKE %s %s
                UNION
                SELECT
                a.category AS cat,
                a.name as pn,
                a.version AS av,
                IFNULL(i.version, 'None') AS iv,
                a.description AS descr
                FROM remote_packages AS a LEFT OUTER JOIN local_packages AS i
                ON a.category = i.category
                AND a.name = i.name
                AND a.slot = i.slot
                WHERE %s LIKE %s %s
            ''' % (Sisyphus.applicationView, Sisyphus.searchTerm, noVirtual, Sisyphus.applicationView, Sisyphus.searchTerm, noVirtual)),
            ('instaled', '''SELECT
                i.category AS cat,
                i.name AS pn,
                a.version AS av,
                i.version AS iv,
                i.description AS descr
                FROM local_packages AS i
                LEFT JOIN remote_packages AS a
                ON i.category = a.category
                AND i.name = a.name
                AND i.slot = a.slot
                WHERE %s LIKE %s %s
            ''' % (Sisyphus.applicationView, Sisyphus.searchTerm, noVirtual)),
            ('installable', '''SELECT
                a.category AS cat,
                a.name AS pn,
                a.version AS av,
                i.version AS iv,
                a.description AS descr
                FROM remote_packages AS a
                LEFT JOIN local_packages AS i
                ON a.category = i.category
                AND a.name = i.name
                AND a.slot = i.slot
                WHERE %s LIKE %s %s
                AND iv IS NULL
            ''' % (Sisyphus.applicationView, Sisyphus.searchTerm, noVirtual)),
            ('removable', '''SELECT
                i.category AS cat,
                i.name AS pn,
                a.version AS av,
                i.version AS iv,
                i.description AS descr
                FROM local_packages AS i
                LEFT JOIN remote_packages AS a
                ON i.category = a.category
                AND i.name = a.name
                AND i.slot = a.slot
                INNER JOIN removable_packages as rm
                ON i.category = rm.category
                AND i.name = rm.name
                AND i.slot = rm.slot
                WHERE %s LIKE %s %s
            ''' % (Sisyphus.applicationView, Sisyphus.searchTerm, noVirtual)),
            ('upgradable', '''SELECT
                i.category AS cat,
                i.name AS pn,
                CASE WHEN a.version = i.version THEN 'Rebuilt' ELSE a.version END AS av,
                i.version AS iv,
                i.description AS descr
                FROM local_packages AS i
                INNER JOIN remote_packages AS a
                ON i.category = a.category
                AND i.name = a.name
                AND i.slot = a.slot
                WHERE %s LIKE %s %s
                AND a.timestamp > i.timestamp
            ''' % (Sisyphus.applicationView, Sisyphus.searchTerm, noVirtual)),
        ])
        with sqlite3.connect(sisyphus_database_path) as db:
            cursor = db.cursor()
            cursor.execute('%s' % (self.SELECTS[Sisyphus.databaseView]))
            rows = cursor.fetchall()
            Sisyphus.pkgCount = len(rows)
            Sisyphus.pkgSelect = 0
            model = QtGui.QStandardItemModel(len(rows), 5)
            model.setHorizontalHeaderLabels(
                ['Category', 'Name', 'Available Version', 'Installed Version', 'Description'])
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

    def sisyphusSettings(self):
        self.window = SisyphusConfig()
        self.window.show()

    def sisyphusExit(self):
        self.close()


class UpdateWorker(QtCore.QObject):
    started = QtCore.pyqtSignal()
    finished = QtCore.pyqtSignal()

    @QtCore.pyqtSlot()
    def startUpdate(self):
        self.started.emit()
        sisyphus_pkg_system_update()
        self.finished.emit()


class InstallWorker(QtCore.QObject):
    started = QtCore.pyqtSignal()
    finished = QtCore.pyqtSignal()
    strReady = QtCore.pyqtSignal(str)

    @QtCore.pyqtSlot()
    def startInstall(self):
        self.started.emit()
        pkgList = Sisyphus.pkgList
        redcore_sync()
        generate_sisyphus_local_packages_table_csv_pre()
        portage_call = subprocess.Popen(
            ['emerge', '-q'] + pkgList, stdout=subprocess.PIPE)
        atexit.register(kill_bg_portage, portage_call)
        for portage_output in io.TextIOWrapper(portage_call.stdout, encoding="utf-8"):
            self.strReady.emit(portage_output.rstrip())
        generate_sisyphus_local_packages_table_csv_post()
        sync_sisyphus_local_packages_table_csv()
        self.finished.emit()


class UninstallWorker(QtCore.QObject):
    started = QtCore.pyqtSignal()
    finished = QtCore.pyqtSignal()
    strReady = QtCore.pyqtSignal(str)

    @QtCore.pyqtSlot()
    def startUninstall(self):
        self.started.emit()
        pkgList = Sisyphus.pkgList
        redcore_sync()
        generate_sisyphus_local_packages_table_csv_pre()
        portage_call = subprocess.Popen(
            ['emerge', '--depclean', '-q'] + pkgList, stdout=subprocess.PIPE)
        atexit.register(kill_bg_portage, portage_call)
        for portage_output in io.TextIOWrapper(portage_call.stdout, encoding="utf-8"):
            self.strReady.emit(portage_output.rstrip())
        generate_sisyphus_local_packages_table_csv_post()
        sync_sisyphus_local_packages_table_csv()
        self.finished.emit()


class UpgradeWorker(QtCore.QObject):
    started = QtCore.pyqtSignal()
    finished = QtCore.pyqtSignal()
    strReady = QtCore.pyqtSignal(str)

    @QtCore.pyqtSlot()
    def startUpgrade(self):
        self.started.emit()
        redcore_sync()
        generate_sisyphus_local_packages_table_csv_pre()
        portage_call = subprocess.Popen(
            ['emerge', '-uDNq', '--backtrack=100', '--with-bdeps=y', '@world'], stdout=subprocess.PIPE)
        atexit.register(kill_bg_portage, portage_call)
        for portage_output in io.TextIOWrapper(portage_call.stdout, encoding="utf-8"):
            self.strReady.emit(portage_output.rstrip())
        generate_sisyphus_local_packages_table_csv_post()
        sync_sisyphus_local_packages_table_csv()
        self.finished.emit()


class OrphansWorker(QtCore.QObject):
    started = QtCore.pyqtSignal()
    finished = QtCore.pyqtSignal()
    strReady = QtCore.pyqtSignal(str)

    @QtCore.pyqtSlot()
    def cleanOrphans(self):
        self.started.emit()
        redcore_sync()
        generate_sisyphus_local_packages_table_csv_pre()
        portage_call = subprocess.Popen(
            ['emerge', '--depclean', '-q'], stdout=subprocess.PIPE)
        atexit.register(kill_bg_portage, portage_call)
        for portage_output in io.TextIOWrapper(portage_call.stdout, encoding="utf-8"):
            self.strReady.emit(portage_output.rstrip())
        generate_sisyphus_local_packages_table_csv_post()
        sync_sisyphus_local_packages_table_csv()
        self.finished.emit()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Sisyphus()
    sys.exit(app.exec_())
