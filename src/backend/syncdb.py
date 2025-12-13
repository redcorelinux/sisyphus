#!/usr/bin/python3

import csv
import shutil
import urllib3
import sqlite3
import os
import re
import subprocess
import sisyphus.getenv
import sisyphus.getfs


def remote_csv():
    pkg_csv_addr, desc_csv_addr = sisyphus.getenv.csv_addr()
    http = urllib3.PoolManager()

    with http.request('GET', pkg_csv_addr, preload_content=False) as tmp_buffer, open(sisyphus.getfs.remote_pkg_csv, 'wb') as output_file:
        shutil.copyfileobj(tmp_buffer, output_file)

    with http.request('GET', desc_csv_addr, preload_content=False) as tmp_buffer, open(sisyphus.getfs.remote_desc_csv, 'wb') as output_file:
        shutil.copyfileobj(tmp_buffer, output_file)


def local_table():
    base_dir = '/var/db/pkg'
    pattern = re.compile(r'^(.+)-([0-9][^,-]*?)(-r[0-9]+)?$')

    sisyphusdb = sqlite3.connect(sisyphus.getfs.local_db)
    cursor = sisyphusdb.cursor()

    cursor.execute('''drop table if exists local_packages''')
    cursor.execute(
        '''create table local_packages (category TEXT,name TEXT,version TEXT,slot TEXT)''')

    packages = []
    if os.path.exists(base_dir):
        for category_name in os.listdir(base_dir):
            category_dir = os.path.join(base_dir, category_name)
            if not os.path.isdir(category_dir):
                continue

            for pkg_dir_name in os.listdir(category_dir):
                pkg_dir = os.path.join(category_dir, pkg_dir_name)
                if not os.path.isdir(pkg_dir):
                    continue

                category_file = os.path.join(pkg_dir, 'CATEGORY')
                pf_file = os.path.join(pkg_dir, 'PF')
                slot_file = os.path.join(pkg_dir, 'SLOT')

                if not all(os.path.exists(f) for f in [category_file, pf_file, slot_file]):
                    continue

                with open(category_file, 'r', encoding='utf-8') as f:
                    category = f.read().strip()
                with open(pf_file, 'r', encoding='utf-8') as f:
                    pf = f.read().strip()
                with open(slot_file, 'r', encoding='utf-8') as f:
                    slot = f.read().strip()

                m = pattern.match(pf)
                if not m:
                    continue

                pn = m.group(1)
                pv = m.group(2)
                pr = m.group(3) or ''
                pvr = pv + pr

                packages.append((category, pn, pvr, slot))

    cursor.executemany(
        "insert into local_packages (category, name, version, slot) values (?, ?, ?, ?)",
        packages
    )

    sisyphusdb.commit()
    sisyphusdb.close()


def remote_table():
    remote_csv()

    sisyphusdb = sqlite3.connect(sisyphus.getfs.local_db)
    sisyphusdb.cursor().execute('''drop table if exists remote_packages''')
    sisyphusdb.cursor().execute('''drop table if exists remote_descriptions''')
    sisyphusdb.cursor().execute(
        '''create table remote_packages (category TEXT,name TEXT,version TEXT,slot TEXT)''')
    sisyphusdb.cursor().execute(
        '''create table remote_descriptions (category TEXT,name TEXT,description TEXT)''')

    with open(sisyphus.getfs.remote_pkg_csv) as input_file:
        for row in csv.reader(input_file):
            sisyphusdb.cursor().execute(
                "insert into remote_packages (category, name, version, slot) values (?, ?, ?, ?);", row)

    with open(sisyphus.getfs.remote_desc_csv) as input_file:
        for row in csv.reader(input_file):
            sisyphusdb.cursor().execute(
                "insert into remote_descriptions (category, name, description) values (?, ?, ?);", row)

    sisyphusdb.commit()
    sisyphusdb.close()
