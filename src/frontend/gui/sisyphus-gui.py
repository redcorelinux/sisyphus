#!/usr/bin/python3

import sys
import sqlite3
import sisyphus
from collections import OrderedDict
from PyQt5 import QtCore, QtGui, QtWidgets, uic


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
        self.applicationFilter.currentIndexChanged.connect(self.setApplicationFilter)
        Sisyphus.applicationView = self.filterApplications['Package Name']

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
        Sisyphus.databaseView = self.filterDatabases['All Packages']

        Sisyphus.searchTerm = "'%%'"

        self.databaseTable.clicked.connect(self.rowClicked)

        self.inputBox.textEdited.connect(self.searchDatabase)

        self.settingsButton.clicked.connect(self.showMirrorWindow)
        self.licenseButton.clicked.connect(self.showLicenseWindow)

        sys.stdout = MainWorker(workerOutput=self.updateProgressBox) # capture stdout

        self.updateWorker = MainWorker()
        self.updateThread = QtCore.QThread()
        self.updateWorker.moveToThread(self.updateThread)
        self.updateWorker.started.connect(self.showProgressBar)
        self.updateThread.started.connect(self.updateWorker.startUpdate)
        self.updateThread.finished.connect(self.hideProgressBar)
        self.updateWorker.finished.connect(self.updateThread.quit)

        self.installButton.clicked.connect(self.packageInstall)
        self.installWorker = MainWorker()
        self.installThread = QtCore.QThread()
        self.installWorker.moveToThread(self.installThread)
        self.installWorker.started.connect(self.showProgressBar)
        self.installThread.started.connect(self.installWorker.startInstall)
        self.installWorker.workerOutput.connect(self.updateProgressBox)
        self.installThread.finished.connect(self.hideProgressBar)
        self.installWorker.finished.connect(self.installThread.quit)

        self.uninstallButton.clicked.connect(self.packageUninstall)
        self.uninstallWorker = MainWorker()
        self.uninstallThread = QtCore.QThread()
        self.uninstallWorker.moveToThread(self.uninstallThread)
        self.uninstallWorker.started.connect(self.showProgressBar)
        self.uninstallThread.started.connect(self.uninstallWorker.startUninstall)
        self.uninstallWorker.workerOutput.connect(self.updateProgressBox)
        self.uninstallThread.finished.connect(self.hideProgressBar)
        self.uninstallWorker.finished.connect(self.uninstallThread.quit)

        self.upgradeButton.clicked.connect(self.systemUpgrade)
        self.upgradeWorker = MainWorker()
        self.upgradeThread = QtCore.QThread()
        self.upgradeWorker.moveToThread(self.upgradeThread)
        self.upgradeWorker.started.connect(self.showProgressBar)
        self.upgradeThread.started.connect(self.upgradeWorker.startUpgrade)
        self.upgradeWorker.workerOutput.connect(self.updateProgressBox)
        self.upgradeThread.finished.connect(self.hideProgressBar)
        self.upgradeWorker.finished.connect(self.upgradeThread.quit)

        self.autoremoveButton.clicked.connect(self.autoRemove)
        self.autoremoveWorker = MainWorker()
        self.autoremoveThread = QtCore.QThread()
        self.autoremoveWorker.moveToThread(self.autoremoveThread)
        self.autoremoveWorker.started.connect(self.showProgressBar)
        self.autoremoveThread.started.connect(self.autoremoveWorker.startAutoremove)
        self.autoremoveWorker.workerOutput.connect(self.updateProgressBox)
        self.autoremoveThread.finished.connect(self.hideProgressBar)
        self.autoremoveWorker.finished.connect(self.autoremoveThread.quit)

        self.updateSystem()
        self.progressBar.hide()

        self.exitButton.clicked.connect(self.sisyphusExit)

    def centerOnScreen(self):
        screenGeometry = QtWidgets.QDesktopWidget().screenGeometry()
        windowGeometry = self.geometry()
        horizontalPosition = int(( screenGeometry.width() - windowGeometry.width() ) / 2)
        verticalPosition = int(( screenGeometry.height() - windowGeometry.height() ) / 2)
        self.move(horizontalPosition, verticalPosition)

    def rowClicked(self):
        Sisyphus.pkgSelect = len(self.databaseTable.selectionModel().selectedRows())
        self.showPackageCount()

    def showPackageCount(self):
        self.statusBar().showMessage("Found: %d, Selected: %d packages" % (Sisyphus.pkgCount, Sisyphus.pkgSelect))

    def setApplicationFilter(self):
        Sisyphus.applicationView = self.filterApplications[self.applicationFilter.currentText()]
        self.loadDatabase()

    def setDatabaseFilter(self):
        Sisyphus.databaseView = self.filterDatabases[self.databaseFilter.currentText()]
        Sisyphus.SELECT = self.databaseFilter.currentText()
        self.loadDatabase()

    def loadDatabase(self):
        noVirtual = "AND cat NOT LIKE 'virtual'"
        self.SELECTS = OrderedDict([
            ('all', '''SELECT
                i.category AS cat,
                i.name as pn,
                i.version as iv,
                IFNULL(a.version, 'alien') AS av,
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
            ('alien', '''SELECT
                i.category AS cat,
                i.name AS pn,
                i.version as iv,
                IFNULL(a.version, 'alien') AS av,
                d.description AS desc
                FROM local_packages AS i
                LEFT JOIN remote_packages AS a
                ON a.category = i.category
                AND a.name = i.name
                AND a.slot = i.slot
                LEFT JOIN remote_descriptions AS d ON i.name = d.name AND i.category = d.category
                WHERE %s LIKE %s %s
                AND av IS 'alien'
            ''' % (Sisyphus.applicationView, Sisyphus.searchTerm, noVirtual)),
            ('available', '''SELECT
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
        with sqlite3.connect(sisyphus.getfs.lcl_db) as db:
            cursor = db.cursor()
            cursor.execute('%s' % (self.SELECTS[Sisyphus.databaseView]))
            rows = cursor.fetchall()
            Sisyphus.pkgCount = len(rows)
            Sisyphus.pkgSelect = 0
            model = QtGui.QStandardItemModel(len(rows), 5)
            model.setHorizontalHeaderLabels(['Category', 'Name', 'Installed Version', 'Available Version', 'Description'])
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

    def getSelectedPackages(self):
        def byRow(e):
            return e['row']

        pkg_categs = [{'row': pkg.row(), 'cat': pkg.data()} for pkg in self.databaseTable.selectionModel().selectedRows(0)]
        pkg_names = [{'row': pkg.row(), 'name': pkg.data()} for pkg in self.databaseTable.selectionModel().selectedRows(1)]
        pkg_categs = sorted(pkg_categs, key=byRow)
        pkg_names = sorted(pkg_names, key=byRow)
        selected_pkgs = [pkg_categs[i]['cat'] + '/' + pkg_names[i]['name'] for i in range(len(pkg_categs))]
        return(selected_pkgs)

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

    def showProgressBar(self):
        self.installButton.hide()
        self.uninstallButton.hide()
        self.autoremoveButton.hide()
        self.upgradeButton.hide()
        self.exitButton.hide()
        self.progressBar.setRange(0, 0)
        self.progressBar.show()
        self.inputBox.setFocus()
        self.progressBox.clear()

    def hideProgressBar(self):
        self.installButton.show()
        self.uninstallButton.show()
        self.autoremoveButton.show()
        self.upgradeButton.show()
        self.exitButton.show()
        self.progressBar.setRange(0, 1)
        self.progressBar.setValue(1)
        self.progressBar.hide()
        self.inputBox.setFocus()
        self.loadDatabase()

    def updateProgressBox(self, workerMessage):
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
        sys.stdout = sys.__stdout__ # restore stdout

# mirror configuration window
class MirrorConfiguration(QtWidgets.QMainWindow):
    def __init__(self):
        super(MirrorConfiguration, self).__init__()
        uic.loadUi('/usr/share/sisyphus/ui/mirrorcfg.ui', self)
        self.centerOnScreen()
        self.MIRRORLIST = sisyphus.mirrors.getList()
        self.updateMirrorList()
        self.applyButton.pressed.connect(self.mirrorCfgApply)
        self.applyButton.released.connect(self.mirrorCfgExit)
        self.mirrorCombo.activated.connect(self.setMirrorList)

    def centerOnScreen(self):
        screenGeometry = QtWidgets.QDesktopWidget().screenGeometry()
        windowGeometry = self.geometry()
        horizontalPosition = int(( screenGeometry.width() - windowGeometry.width() ) / 2)
        verticalPosition = int(( screenGeometry.height() - windowGeometry.height() ) / 2)
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
        sisyphus.mirrors.writeList(self.MIRRORLIST)

    def mirrorCfgExit(self):
        self.close()


# license information window
class LicenseInformation(QtWidgets.QMainWindow):
    def __init__(self):
        super(LicenseInformation, self).__init__()
        uic.loadUi('/usr/share/sisyphus/ui/license.ui', self)
        self.centerOnScreen()

    def centerOnScreen(self):
        screenGeometry = QtWidgets.QDesktopWidget().screenGeometry()
        windowGeometry = self.geometry()
        horizontalPosition = int(( screenGeometry.width() - windowGeometry.width() ) / 2)
        verticalPosition = int(( screenGeometry.height() - windowGeometry.height() ) / 2)
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
        sisyphus.update.start.__wrapped__(gfx_ui=True) # undecorate
        self.finished.emit()

    @QtCore.pyqtSlot()
    def startInstall(self):
        self.started.emit()
        pkgname = Sisyphus.pkgname
        sisyphus.install.start(pkgname, ebuild=False, gfx_ui=True, oneshot=False)
        self.finished.emit()

    @QtCore.pyqtSlot()
    def startUninstall(self):
        self.started.emit()
        pkgname = Sisyphus.pkgname
        sisyphus.uninstall.start(pkgname, depclean=True, gfx_ui=True, unmerge=False)
        self.finished.emit()

    @QtCore.pyqtSlot()
    def startUpgrade(self):
        self.started.emit()
        sisyphus.upgrade.start(ebuild=False, gfx_ui=True)
        self.finished.emit()

    @QtCore.pyqtSlot()
    def startAutoremove(self):
        self.started.emit()
        sisyphus.autoremove.start(gfx_ui=True)
        self.finished.emit()


# launch application
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Breeze')
    window = Sisyphus()
    window.inputBox.setFocus()
    sys.exit(app.exec_())
