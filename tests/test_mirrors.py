import pytest
import sisyphus.getenv
import sisyphus.getfs
import sisyphus.setmirror

# Cut-down copies of the real files in redcore-desktop (app-portage/sisyphus/files).
BINREPOS = """\
#    Uncomment only one mirror from the list bellow   #

# [redcore-princeton-stable]
# sync-uri = http://mirror.math.princeton.edu/pub/redcorelinux/amd64/packages/
# location = /var/cache/packages

# [redcore-princeton-testing]
# sync-uri = http://mirror.math.princeton.edu/pub/redcorelinux/amd64/packages-next/
# location = /var/cache/packages

[redcore-alpix-stable]
sync-uri = http://mirror.alpix.eu/redcorelinux/amd64/packages/
location = /var/cache/packages
"""

BINHOST = """\
# Princeton University (USA) mirror - stable
PORTAGE_BINHOST="http://mirror.math.princeton.edu/pub/redcorelinux/amd64/packages/"

# Princeton University (USA) mirror - testing
# PORTAGE_BINHOST="http://mirror.math.princeton.edu/pub/redcorelinux/amd64/packages-next/"
"""

PRINCETON = 'http://mirror.math.princeton.edu/pub/redcorelinux/amd64/'
ALPIX = 'http://mirror.alpix.eu/redcorelinux/amd64/'


@pytest.fixture
def cfg(tmp_path, monkeypatch):
    binrepos = tmp_path / 'binrepos.conf'
    binhost = tmp_path / 'binhost.conf'
    binrepos.write_text(BINREPOS)
    binhost.write_text(BINHOST)
    # getfs only sets these on x86_64 and aarch64, hence raising=False.
    monkeypatch.setattr(sisyphus.getfs, 'binreposcfg', str(binrepos), raising=False)
    monkeypatch.setattr(sisyphus.getfs, 'binhostcfg', str(binhost), raising=False)
    return binrepos, binhost


def test_getlist_reads_both_files(cfg):
    mirrors = sisyphus.setmirror.getList()

    assert [(m['Type'], m['Branch'], m['isActive'], m['Url']) for m in mirrors] == [
        ('BINHOST (DEPRECATED)', 'stable', True, PRINCETON + 'packages/'),
        ('BINHOST (DEPRECATED)', 'testing', False, PRINCETON + 'packages-next/'),
        ('BINREPOS (CURRENT)', 'stable', False, PRINCETON + 'packages/'),
        ('BINREPOS (CURRENT)', 'testing', False, PRINCETON + 'packages-next/'),
        ('BINREPOS (CURRENT)', 'stable', True, ALPIX + 'packages/'),
    ]


def test_getlist_skips_missing_files(tmp_path, monkeypatch):
    monkeypatch.setattr(sisyphus.getfs, 'binreposcfg', str(tmp_path / 'none'), raising=False)
    monkeypatch.setattr(sisyphus.getfs, 'binhostcfg', str(tmp_path / 'none'), raising=False)

    assert sisyphus.setmirror.getList() == []


def test_writelist_activates_a_binrepos_section(cfg):
    binrepos, _ = cfg

    sisyphus.setmirror.writeList(str(binrepos), PRINCETON + 'packages/', True, False)

    text = binrepos.read_text()
    assert ('\n[redcore-princeton-stable]\n'
            'sync-uri = ' + PRINCETON + 'packages/\n'
            'location = /var/cache/packages\n') in text
    # The testing section for the same mirror is left commented out.
    assert '# [redcore-princeton-testing]\n' in text
    assert '# sync-uri = ' + PRINCETON + 'packages-next/\n' in text


def test_writelist_deactivates_a_binrepos_section(cfg):
    binrepos, _ = cfg

    sisyphus.setmirror.writeList(str(binrepos), ALPIX + 'packages/', False, False)

    assert ('# [redcore-alpix-stable]\n'
            '# sync-uri = ' + ALPIX + 'packages/\n'
            '# location = /var/cache/packages\n') in binrepos.read_text()
    assert all(not m['isActive'] for m in sisyphus.setmirror.getList()
               if m['Type'] == 'BINREPOS (CURRENT)')


def test_writelist_switches_binhost_line(cfg):
    _, binhost = cfg

    sisyphus.setmirror.writeList(str(binhost), PRINCETON + 'packages/', False, True)
    sisyphus.setmirror.writeList(str(binhost), PRINCETON + 'packages-next/', True, True)

    text = binhost.read_text()
    assert '# PORTAGE_BINHOST="' + PRINCETON + 'packages/"\n' in text
    assert '\nPORTAGE_BINHOST="' + PRINCETON + 'packages-next/"\n' in text


def test_writelist_ignores_a_missing_file(tmp_path):
    missing = tmp_path / 'none'

    sisyphus.setmirror.writeList(str(missing), ALPIX + 'packages/', True, False)

    assert not missing.exists()


def test_binpkg_addr_returns_first_active_mirror(cfg):
    # BINHOST is read first, so its active line wins.
    assert sisyphus.getenv.binpkg_addr() == PRINCETON + 'packages/'


def test_csv_addr_stable(cfg):
    _, binhost = cfg
    binhost.write_text('')

    assert sisyphus.getenv.csv_addr() == (
        ALPIX + 'csv/remotePackagesPre.csv',
        ALPIX + 'csv/remoteDescriptionsPre.csv')


def test_csv_addr_testing(cfg):
    _, binhost = cfg
    binhost.write_text('PORTAGE_BINHOST="' + PRINCETON + 'packages-next/"\n')

    assert sisyphus.getenv.csv_addr() == (
        PRINCETON + 'csv-next/remotePackagesPre.csv',
        PRINCETON + 'csv-next/remoteDescriptionsPre.csv')


def test_csv_addr_without_an_active_mirror(cfg):
    binrepos, binhost = cfg
    binrepos.write_text('')
    binhost.write_text('')

    assert sisyphus.getenv.csv_addr() == (None, None)
