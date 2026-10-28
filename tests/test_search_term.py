import sqlite3

import pytest

import sisyphus.getfs
import sisyphus.searchdb


def test_split_term_splits_category_and_name():
    assert sisyphus.searchdb.split_term('x11-wm/openbox') == (
        'x11-wm', 'openbox')


def test_split_term_keeps_category_wildcard():
    assert sisyphus.searchdb.split_term('x11-wm/*') == ('x11-wm', '*')


def test_split_term_leaves_plain_names_alone():
    assert sisyphus.searchdb.split_term('openbox') == ('', 'openbox')


def test_split_term_does_not_crash_on_extra_slash():
    assert sisyphus.searchdb.split_term('a/b/c') == ('a', 'b/c')


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
            "insert into remote_packages values ('x11-wm', 'openbox', '3.6.1-r11', '3')")
        db.execute(
            "insert into remote_packages values ('x11-wm', 'fluxbox', '1.3.7-r5', '0')")
        db.execute(
            "insert into remote_packages values ('x11-themes', 'openbox-themes', '1.0.2', '0')")
    monkeypatch.setattr(sisyphus.getfs, 'local_db', str(path))


def search(terms):
    rows = sisyphus.searchdb.srch_db('all', '', terms, '')
    return sorted(f"{row['cat']}/{row['pn']}" for row in rows)


def test_category_name_term_matches_only_that_category(local_db):
    assert search(['x11-wm/openbox']) == ['x11-wm/openbox']


def test_plain_terms_still_search_every_category(local_db):
    assert search(['openbox', 'fluxbox']) == [
        'x11-themes/openbox-themes', 'x11-wm/fluxbox', 'x11-wm/openbox']


def test_category_name_term_keeps_later_terms(local_db):
    assert search(['x11-wm/openbox', 'fluxbox']) == [
        'x11-wm/fluxbox', 'x11-wm/openbox']
