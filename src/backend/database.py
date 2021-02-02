#!/usr/bin/python3

import csv
import shutil
import urllib3
import sqlite3
import subprocess
import sisyphus.csvfiles
import sisyphus.filesystem

def getRemote():
    isPackageCsv,isDescriptionCsv = sisyphus.csvfiles.start()
    http = urllib3.PoolManager()

    with http.request('GET', isPackageCsv, preload_content=False) as tmp_buffer, open(sisyphus.filesystem.remotePackagesCsv, 'wb') as output_file:
        shutil.copyfileobj(tmp_buffer, output_file)

    with http.request('GET', isDescriptionCsv, preload_content=False) as tmp_buffer, open(sisyphus.filesystem.remoteDescriptionsCsv, 'wb') as output_file:
        shutil.copyfileobj(tmp_buffer, output_file)

def makeLocal():
    subprocess.call(['/usr/share/sisyphus/helpers/make_local_csv'])

def syncRemote():
    getRemote()

    sisyphusdb = sqlite3.connect(sisyphus.filesystem.localDatabase)
    sisyphusdb.cursor().execute('''drop table if exists remote_packages''')
    sisyphusdb.cursor().execute('''drop table if exists remote_descriptions''')
    sisyphusdb.cursor().execute('''create table remote_packages (category TEXT,name TEXT,version TEXT,slot TEXT)''')
    sisyphusdb.cursor().execute('''create table remote_descriptions (category TEXT,name TEXT,description TEXT)''')

    with open(sisyphus.filesystem.remotePackagesCsv) as input_file:
        for row in csv.reader(input_file):
            sisyphusdb.cursor().execute("insert into remote_packages (category, name, version, slot) values (?, ?, ?, ?);", row)

    with open(sisyphus.filesystem.remoteDescriptionsCsv) as input_file:
        for row in csv.reader(input_file):
            sisyphusdb.cursor().execute("insert into remote_descriptions (category, name, description) values (?, ?, ?);", row)

    sisyphusdb.commit()
    sisyphusdb.close()

def syncLocal():
    makeLocal()

    sisyphusdb = sqlite3.connect(sisyphus.filesystem.localDatabase)
    sisyphusdb.cursor().execute('''drop table if exists local_packages''')
    sisyphusdb.cursor().execute('''create table local_packages (category TEXT,name TEXT,version TEXT,slot TEXT)''')

    with open(sisyphus.filesystem.localPackagesCsv) as input_file:
        for row in csv.reader(input_file):
            sisyphusdb.cursor().execute("insert into local_packages (category, name, version, slot) values (?, ?, ?, ?);", row)

    sisyphusdb.commit()
    sisyphusdb.close()

