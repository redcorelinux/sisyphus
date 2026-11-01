import sqlite3

import pytest

import sisyphus.getfs
import sisyphus.querydb
import sisyphus.searchdb

FILTERS = ['all', 'installed', 'alien', 'available', 'upgradable']


@pytest.fixture
def local_db(tmp_path, monkeypatch):
    # A small copy of the tables syncdb builds, in a temporary file.
    path = tmp_path / 'sisyphus.db'
    with sqlite3.connect(path) as db:
        db.execute(
            'create table local_packages (category TEXT,name TEXT,version TEXT,slot TEXT)')
        db.execute(
            'create table remote_packages (category TEXT,name TEXT,version TEXT,slot TEXT)')
        db.execute(
            'create table remote_descriptions (category TEXT,name TEXT,description TEXT)')
        db.execute(
            "insert into local_packages values ('x11-wm', 'openbox', '3.6.1', '3')")
        db.execute(
            "insert into remote_packages values ('x11-wm', 'openbox', '3.6.2', '3')")
        db.execute(
            "insert into remote_packages values ('x11-wm', 'fluxbox', '1.3.7', '0')")
        db.execute(
            "insert into remote_descriptions values ('x11-wm', 'openbox', 'A window manager')")
        db.execute(
            "insert into remote_descriptions values ('x11-wm', 'fluxbox', 'Blackbox''s lighter cousin')")
    monkeypatch.setattr(sisyphus.getfs, 'local_db', str(path))
    return path


@pytest.mark.parametrize('filter', FILTERS)
def test_apostrophe_in_name_does_not_crash(local_db, filter):
    assert sisyphus.searchdb.srch_db(filter, pn="o'box") == []


@pytest.mark.parametrize('filter', FILTERS)
def test_apostrophe_in_description_does_not_crash(local_db, filter):
    sisyphus.searchdb.srch_db(filter, desc="it's")


def test_apostrophe_in_description_finds_the_package(local_db):
    rows = sisyphus.searchdb.srch_db('available', desc="blackbox's")
    assert [row['pn'] for row in rows] == ['fluxbox']


def test_wildcards_still_work(local_db):
    rows = sisyphus.searchdb.srch_db('all', pn='*box')
    assert sorted(row['pn'] for row in rows) == ['fluxbox', 'openbox']


def test_upgradable_still_finds_newer_version(local_db):
    rows = sisyphus.searchdb.srch_db('upgradable', pn='openbox')
    assert [(row['iv'], row['av']) for row in rows] == [('3.6.1', '3.6.2')]


def test_query_text_does_not_contain_the_search_term():
    query, params = sisyphus.querydb.start('all', pn="o'box")
    assert "o'box" not in query
    assert params['pn'] == "o'box"
