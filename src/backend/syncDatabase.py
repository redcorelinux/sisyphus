#!/usr/bin/python3

import csv
import shutil
import urllib3
import sqlite3
import subprocess
import sisyphus.getEnvironment
import sisyphus.getFilesystem

def remoteCSV():
    packagesCsvURL,descriptionsCsvURL = sisyphus.getEnvironment.csvURL()
    http = urllib3.PoolManager()

    with http.request('GET', packagesCsvURL, preload_content=False) as tmp_buffer, open(sisyphus.getFilesystem.remotePackagesCsv, 'wb') as output_file:
        shutil.copyfileobj(tmp_buffer, output_file)

    with http.request('GET', descriptionsCsvURL, preload_content=False) as tmp_buffer, open(sisyphus.getFilesystem.remoteDescriptionsCsv, 'wb') as output_file:
        shutil.copyfileobj(tmp_buffer, output_file)

def localCSV():
    subprocess.call(['/usr/share/sisyphus/helpers/make_local_csv'])

def remoteTable():
    remoteCSV()

    sisyphusdb = sqlite3.connect(sisyphus.getFilesystem.localDatabase)
    sisyphusdb.cursor().execute('''drop table if exists remote_packages''')
    sisyphusdb.cursor().execute('''drop table if exists remote_descriptions''')
    sisyphusdb.cursor().execute('''create table remote_packages (category TEXT,name TEXT,version TEXT,slot TEXT)''')
    sisyphusdb.cursor().execute('''create table remote_descriptions (category TEXT,name TEXT,description TEXT)''')

    with open(sisyphus.getFilesystem.remotePackagesCsv) as input_file:
        for row in csv.reader(input_file):
            sisyphusdb.cursor().execute("insert into remote_packages (category, name, version, slot) values (?, ?, ?, ?);", row)

    with open(sisyphus.getFilesystem.remoteDescriptionsCsv) as input_file:
        for row in csv.reader(input_file):
            sisyphusdb.cursor().execute("insert into remote_descriptions (category, name, description) values (?, ?, ?);", row)

    sisyphusdb.commit()
    sisyphusdb.close()

def localTable():
    localCSV()

    sisyphusdb = sqlite3.connect(sisyphus.getFilesystem.localDatabase)
    sisyphusdb.cursor().execute('''drop table if exists local_packages''')
    sisyphusdb.cursor().execute('''create table local_packages (category TEXT,name TEXT,version TEXT,slot TEXT)''')

    with open(sisyphus.getFilesystem.localPackagesCsv) as input_file:
        for row in csv.reader(input_file):
            sisyphusdb.cursor().execute("insert into local_packages (category, name, version, slot) values (?, ?, ?, ?);", row)

    sisyphusdb.commit()
    sisyphusdb.close()

