#!/usr/bin/python3
import sys, subprocess, sqlite3
from PyQt5 import QtCore, QtGui, QtWidgets, uic

class Development(QtWidgets.QMainWindow):
    def __init__(self):
        super(Development, self).__init__()
        uic.loadUi('ui/development.ui', self)
        self.centerOnScreen()
        self.show()
        self.load_packages()

        self.package_install.clicked.connect(self.install_package) 
        self.package_uninstall.clicked.connect(self.uninstall_package)
        self.orphans_remove.clicked.connect(self.remove_orphans)
        self.category_exit.clicked.connect(self.exit_category)
    
    def centerOnScreen(self):
        resolution = QtWidgets.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                    (resolution.height() / 2) - (self.frameSize().height() / 2))

    def install_package(self):
        pkgname = self.table_development.item(self.table_development.currentRow(), 1).text()
        subprocess.Popen(['xterm', '-e', 'sisyphus', 'auto-install'] + pkgname.split())
    
    def uninstall_package(self):
        pkgname = self.table_development.item(self.table_development.currentRow(), 1).text()
        subprocess.Popen(['xterm', '-e', 'sisyphus', 'auto-uninstall'] + pkgname.split())

    def remove_orphans(self):
        subprocess.Popen(['xterm', '-e', 'sisyphus', 'auto-uninstall'])

    def exit_category(self):
        self.close()
 
    def load_packages(self):
        with sqlite3.connect('/var/lib/sisyphus/db/sisyphus.db') as db:
            cursor=db.cursor()
            cursor.execute('''SELECT * from remote_packages''')
            rows = cursor.fetchall()
            
            for row in rows:
                inx = rows.index(row)
                self.table_development.insertRow(inx)
                self.table_development.setItem(inx, 0, QtWidgets.QTableWidgetItem(row[0]))
                self.table_development.setItem(inx, 1, QtWidgets.QTableWidgetItem(row[1]))
                self.table_development.setItem(inx, 2, QtWidgets.QTableWidgetItem(row[2]))
                self.table_development.setItem(inx, 3, QtWidgets.QTableWidgetItem(row[3]))
                self.table_development.setItem(inx, 4, QtWidgets.QTableWidgetItem(row[4]))