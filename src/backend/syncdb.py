#!/usr/bin/python3

import csv
import shutil
import urllib3
import sqlite3
import subprocess
import sisyphus.getenv
import sisyphus.getfs


def rmt_csv():
    pcsv_addr, dcsv_addr = sisyphus.getenv.csv_addr()
    http = urllib3.PoolManager()

    with http.request('GET', pcsv_addr, preload_content=False) as tmp_buffer, open(sisyphus.getfs.rmt_pcsv, 'wb') as output_file:
        shutil.copyfileobj(tmp_buffer, output_file)

    with http.request('GET', dcsv_addr, preload_content=False) as tmp_buffer, open(sisyphus.getfs.rmt_dcsv, 'wb') as output_file:
        shutil.copyfileobj(tmp_buffer, output_file)


def lcl_csv():
    subprocess.call(['/usr/share/sisyphus/helpers/make_local_csv'])


def rmt_tbl():
    rmt_csv()

    sisyphusdb = sqlite3.connect(sisyphus.getfs.lcl_db)
    sisyphusdb.cursor().execute('''drop table if exists remote_packages''')
    sisyphusdb.cursor().execute('''drop table if exists remote_descriptions''')
    sisyphusdb.cursor().execute(
        '''create table remote_packages (category TEXT,name TEXT,version TEXT,slot TEXT)''')
    sisyphusdb.cursor().execute(
        '''create table remote_descriptions (category TEXT,name TEXT,description TEXT)''')

    with open(sisyphus.getfs.rmt_pcsv) as input_file:
        for row in csv.reader(input_file):
            sisyphusdb.cursor().execute(
                "insert into remote_packages (category, name, version, slot) values (?, ?, ?, ?);", row)

    with open(sisyphus.getfs.rmt_dcsv) as input_file:
        for row in csv.reader(input_file):
            sisyphusdb.cursor().execute(
                "insert into remote_descriptions (category, name, description) values (?, ?, ?);", row)

    sisyphusdb.commit()
    sisyphusdb.close()


def lcl_tbl():
    lcl_csv()

    sisyphusdb = sqlite3.connect(sisyphus.getfs.lcl_db)
    sisyphusdb.cursor().execute('''drop table if exists local_packages''')
    sisyphusdb.cursor().execute(
        '''create table local_packages (category TEXT,name TEXT,version TEXT,slot TEXT)''')

    with open(sisyphus.getfs.lcl_pcsv) as input_file:
        for row in csv.reader(input_file):
            sisyphusdb.cursor().execute(
                "insert into local_packages (category, name, version, slot) values (?, ?, ?, ?);", row)

    sisyphusdb.commit()
    sisyphusdb.close()
