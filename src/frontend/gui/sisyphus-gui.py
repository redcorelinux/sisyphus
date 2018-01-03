#!/usr/bin/python3
import sys, subprocess, sqlite3, io, atexit
from collections import OrderedDict
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from libsisyphus import *

class Sisyphus(QtWidgets.QMainWindow):
    def __init__(self):
        super(Sisyphus, self).__init__()
        uic.loadUi('ui/sisyphus-gui.ui', self)
        self.centerOnScreen()
        self.show()
        
        self.SEARCHFIELDS = OrderedDict ([
            ('Search by Name', 'pn'),
            ('Search by Category', 'cat'),
            ('Search by Description', 'descr')
            ])
        self.selectfield.addItems(self.SEARCHFIELDS.keys())
        self.selectfield.setCurrentText('Search by Name')
        Sisyphus.SEARCHFIELD = self.SEARCHFIELDS['Search by Name']
        self.selectfield.currentIndexChanged.connect(self.setSearchField)
        
        self.SEARCHFILTERS = OrderedDict ([
            ('All Packages', 'all'),
            ('Installed Packages', 'instaled'),
            ('Installable Packages', 'installable'),
            ('Safely Removable Packages', 'removable'),
            ('Upgradable/Rebuilt Packages', 'upgradable')
            ])
        Sisyphus.SEARCHFILTER = self.SEARCHFILTERS['All Packages']
        self.selectfilter.addItems(self.SEARCHFILTERS.keys())
        self.selectfilter.setCurrentText('All Packages')
        self.selectfilter.currentIndexChanged.connect(self.setSearchFilter)
        
        Sisyphus.SEARCHTERM = "'%%'"

        self.database.clicked.connect(self.rowClicked)
        
        self.input.textEdited.connect(self.filterDatabase)

        self.updateWorker = UpdateWorker()
        self.updateThread = QtCore.QThread()
        self.updateWorker.moveToThread(self.updateThread)
        self.updateWorker.started.connect(self.showProgressBar)
        self.updateWorker.finished.connect(self.updateThread.quit)
        self.updateThread.started.connect(self.updateWorker.startUpdate)
        self.updateThread.finished.connect(self.jobDone)

        self.install.clicked.connect(self.packageInstall)
        self.installWorker = InstallWorker()
        self.installThread = QtCore.QThread()
        self.installWorker.moveToThread(self.installThread)
        self.installWorker.started.connect(self.showProgressBar)
        self.installWorker.strReady.connect(self.updateStatusBar)
        self.installWorker.finished.connect(self.installThread.quit)
        self.installThread.started.connect(self.installWorker.startInstall)
        self.installThread.finished.connect(self.jobDone)

        self.uninstall.clicked.connect(self.packageUninstall)
        self.uninstallWorker = UninstallWorker()
        self.uninstallThread = QtCore.QThread()
        self.uninstallWorker.moveToThread(self.uninstallThread)
        self.uninstallWorker.started.connect(self.showProgressBar)
        self.uninstallWorker.strReady.connect(self.updateStatusBar)
        self.uninstallWorker.finished.connect(self.uninstallThread.quit)
        self.uninstallThread.started.connect(self.uninstallWorker.startUninstall)
        self.uninstallThread.finished.connect(self.jobDone)

        self.upgrade.clicked.connect(self.systemUpgrade)
        self.upgradeWorker = UpgradeWorker()
        self.upgradeThread = QtCore.QThread()
        self.upgradeWorker.moveToThread(self.upgradeThread)
        self.upgradeWorker.started.connect(self.showProgressBar)
        self.upgradeWorker.strReady.connect(self.updateStatusBar)
        self.upgradeWorker.finished.connect(self.upgradeThread.quit)
        self.upgradeThread.started.connect(self.upgradeWorker.startUpgrade)
        self.upgradeThread.finished.connect(self.jobDone)

        self.orphans.clicked.connect(self.orphansRemove)
        self.orphansWorker = OrphansWorker()
        self.orphansThread = QtCore.QThread()
        self.orphansWorker.moveToThread(self.orphansThread)
        self.orphansWorker.started.connect(self.showProgressBar)
        self.orphansWorker.strReady.connect(self.updateStatusBar)
        self.orphansWorker.finished.connect(self.orphansThread.quit)
        self.orphansThread.started.connect(self.orphansWorker.cleanOrphans)
        self.orphansThread.finished.connect(self.jobDone)

        self.updateSystem()
        self.progress.hide()

        self.abort.clicked.connect(self.sisyphusExit)
        
    def centerOnScreen(self):
        resolution = QtWidgets.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                    (resolution.height() / 2) - (self.frameSize().height() / 2))
        
    def rowClicked(self):
        Sisyphus.PKGSELECTED = len(self.database.selectionModel().selectedRows())
        self.showPackageCount()

    def showPackageCount(self):
        self.statusBar().showMessage("Found: %d, Selected: %d packages" %(Sisyphus.PKGCOUNT, Sisyphus.PKGSELECTED))

    def setSearchField(self):
        Sisyphus.SEARCHFIELD = self.SEARCHFIELDS[self.selectfield.currentText()]
        self.loadDatabase()
        
    def setSearchFilter(self):
        Sisyphus.SEARCHFILTER = self.SEARCHFILTERS[self.selectfilter.currentText()]
        Sisyphus.SELECT = self.selectfilter.currentText()
        self.loadDatabase()

    def loadDatabase(self):
        FILTEROUT = "AND cat NOT LIKE 'virtual'"
        self.SELECTS = OrderedDict ([
            ('all','''SELECT
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
            ''' % (Sisyphus.SEARCHFIELD, Sisyphus.SEARCHTERM, FILTEROUT, Sisyphus.SEARCHFIELD, Sisyphus.SEARCHTERM, FILTEROUT)),
            ('instaled','''SELECT
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
            ''' % (Sisyphus.SEARCHFIELD, Sisyphus.SEARCHTERM, FILTEROUT)),
            ('installable','''SELECT
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
            ''' % (Sisyphus.SEARCHFIELD, Sisyphus.SEARCHTERM, FILTEROUT)),
            ('removable','''SELECT
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
            ''' % (Sisyphus.SEARCHFIELD, Sisyphus.SEARCHTERM, FILTEROUT)),
            ('upgradable','''SELECT
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
            ''' % (Sisyphus.SEARCHFIELD, Sisyphus.SEARCHTERM, FILTEROUT)),
            ])
        with sqlite3.connect(sisyphus_database_path) as db:
            cursor=db.cursor()
            cursor.execute('%s' % (self.SELECTS[Sisyphus.SEARCHFILTER]))
            rows = cursor.fetchall()
            Sisyphus.PKGCOUNT = len(rows)
            Sisyphus.PKGSELECTED = 0
            model = QtGui.QStandardItemModel(len(rows), 5)
            model.setHorizontalHeaderLabels(['Category', 'Name', 'Available Version', 'Installed Version', 'Description'])
            for row in rows:
                indx = rows.index(row)
                for column in range(0, 5):
                    item = QtGui.QStandardItem("%s"%(row[column]))
                    model.setItem(indx, column, item)
            self.database.setModel(model)
            self.showPackageCount()

    def filterDatabase(self):
        search = self.input.text()
        Sisyphus.SEARCHTERM = "'%" + search + "%'"
        self.loadDatabase()

    def updateSystem(self):
        self.loadDatabase()
        self.statusBar().showMessage("I am syncing myself, hope to finish soon ...")
        self.updateThread.start()

    def packageInstall(self):
        indexes = self.database.selectionModel().selectedRows(1)
        if len(indexes) == 0:
            self.statusBar().showMessage("No package selected, please pick at least one!")
        else:
            Sisyphus.PKGLIST = []
            for index in sorted(indexes):
                Sisyphus.PKGLIST.append(index.data())
            self.statusBar().showMessage("I am installing requested package(s), please wait ...")
            self.installThread.start()

    def packageUninstall(self):
        indexes = self.database.selectionModel().selectedRows(1)
        if len(indexes) == 0:
            self.statusBar().showMessage("No package selected, please pick at least one!")
        else:
            Sisyphus.PKGLIST = []
            for index in sorted(indexes):
                Sisyphus.PKGLIST.append(index.data())
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
        self.progress.setRange(0,0)
        self.progress.show()

    def hideProgressBar(self):
        self.progress.setRange(0,1)
        self.progress.setValue(1)
        self.progress.hide()
        self.showButtons()

    def hideButtons(self):
        self.install.hide()
        self.uninstall.hide()
        self.orphans.hide()
        self.upgrade.hide()
        self.abort.hide()

    def showButtons(self):
        self.install.show()
        self.uninstall.show()
        self.orphans.show()
        self.upgrade.show()
        self.abort.show()

    def updateStatusBar(self, workerMessage):
        self.statusBar().showMessage(workerMessage)

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
        PKGLIST = Sisyphus.PKGLIST
        redcore_sync()
        generate_sisyphus_local_packages_table_csv_pre()
        portage_call = subprocess.Popen(['emerge', '-q'] + PKGLIST, stdout=subprocess.PIPE)
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
        PKGLIST = Sisyphus.PKGLIST
        redcore_sync()
        generate_sisyphus_local_packages_table_csv_pre()
        portage_call = subprocess.Popen(['emerge', '--depclean', '-q'] + PKGLIST, stdout=subprocess.PIPE)
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
        portage_call = subprocess.Popen(['emerge', '-uDNq', '--backtrack=100', '--with-bdeps=y', '@world'], stdout=subprocess.PIPE)
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
        portage_call = subprocess.Popen(['emerge', '--depclean', '-q'], stdout=subprocess.PIPE)
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
