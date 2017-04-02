#!/usr/bin/python3
import sys, subprocess, sqlite3
from PyQt5 import QtCore, QtGui, QtWidgets, uic

class Everything(QtWidgets.QMainWindow):
    def __init__(self):
        super(Everything, self).__init__()
        uic.loadUi('ui/everything.ui', self)
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
        pkgname = self.table_everything.item(self.table_everything.currentRow(), 1).text()
        subprocess.Popen(['xterm', '-e', 'epkg', 'autoinstall'] + pkgname.split())

    def uninstall_package(self):
        pkgname = self.table_everything.item(self.table_everything.currentRow(), 1).text()
        subprocess.Popen(['xterm', '-e', 'epkg', 'autoremove'] + pkgname.split())

    def remove_orphans(self):
        subprocess.Popen(['xterm', '-e', 'epkg', 'autoclean'])

    def exit_category(self):
        self.close()
 
    def load_packages(self):
        with sqlite3.connect('/var/lib/epkg/db/epkg.db') as db:
            cursor=db.cursor()
            cursor.execute('''
                            SELECT
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
            ''')
            rows = cursor.fetchall()
            
            for row in rows:
                inx = rows.index(row)
                self.table_everything.insertRow(inx)
                self.table_everything.setItem(inx, 0, QtWidgets.QTableWidgetItem(row[0]))
                self.table_everything.setItem(inx, 1, QtWidgets.QTableWidgetItem(row[1]))
                self.table_everything.setItem(inx, 2, QtWidgets.QTableWidgetItem(row[2]))
                self.table_everything.setItem(inx, 3, QtWidgets.QTableWidgetItem(row[3]))
                self.table_everything.setItem(inx, 4, QtWidgets.QTableWidgetItem(row[4]))
