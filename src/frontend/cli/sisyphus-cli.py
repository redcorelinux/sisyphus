#!/usr/bin/python3

import sisyphus
import typer
from typing import List
from enum import Enum
import sys

app = typer.Typer()
mirrorSetup = typer.Typer()
app.add_typer(mirrorSetup, name="mirror", help='List/Set the active binhost (binary repository) mirror.')

@app.callback()
def app_callback(ctx: typer.Context):
    """Sisyphus is a simple python wrapper around portage, gentoolkit, and portage-utils
    which provides an apt-get/yum-alike interface to these commands,
    to assist newcomer people transitioning from Debian/RedHat-based systems to Gentoo.

    Use 'sisyphus COMMAND --help' for detailed usage.
    """
    ctx.info_name = 'sisyphus'

class Filter(str, Enum):
    all = 'all'
    alien = 'alien'
    installed = 'installed'
    available = 'available'
    upgradable = 'upgradable'

@app.command("search")
def search(package: List[str] = typer.Argument(...),
           desc: str = typer.Option('', '--description', '-d', help = 'Match description.'),
           filter: Filter = typer.Option(Filter.all, '--filter', '-f', show_default=True),
           quiet: bool = typer.Option(False, '-q', help='Short (one line) output.'),
           ebuild: bool = typer.Option(False, "--ebuild", "-e", help = 'Search in ebuilds (slower).')):
    """Search for binary and/or ebuild (source) packages.

    By default will search for binary packages, using internal database.
    The search term can be provided also in the category/name format, e.g:

        sisyphus search openbox

            OR

        sisyphus search x11-wm/openbox

    Using * and ? wildcards is supported. An empty string will match everything (similar to *).

    * Examples:

    to search for all packages belonging to a category, use '*' or leave the name empty:

        sisyphus search x11-wm/

        sisyphus search x11-wm/*

    In addition, search can be performed by package description, using the -d (--description) option:

        sisyphus search x11/open -d 'window manager'

    (use single or double quotes when the description contains spaces)

    Use the -f (--filter) option to select only packages of interest. Possible values:

        all (default) - search the entire database

        alien - search for installed packages but not available
        (this filter can match packages installed from e-builds or packages no longer maintained as binaries)

        installed - search in all installed packages

        available - search for available packages but not installed

        upgradable - search for installed packages where installed version is different from available version

    !!! NOTE !!!:

    bash will expand a single * character as current folder listing.
    To search for all matching '--filter' packages escape it, or surround it with quotes, or use an empty string:

        sisyphus search * -f installed          # this is not valid!

        sisyphus search \* -f alien             # OK

        sisyphus search '*' -f available        # OK

        sisyphus search '' -f upgradable       # OK


    To search for all (including source) packages, use the --ebuild option.
    This is slower since will perform an emerge --search actually.
    With this option, more than one package can be provided as search term.
    '-d', '-f' and '-q' (quiet) options are ignored in this mode.
    """
    if not ebuild:
        if '/' in package[0]:
            cat, pn = package[0].split('/')
        else:
            cat, pn = '', package[0]
        sisyphus.search.start(filter.value, cat, pn, desc, quiet)
    else:
        if not package:
            raise typer.Exit('No search term provided, try: sisyphus search --help')
        else:
            sisyphus.search.estart(package)

@app.command("install")
def install(pkgname: List[str], ebuild: bool = typer.Option(False, "--ebuild", "-e")):
    """Install binary and/or ebuild(source) packages.
    By default, only binary packages will be installed.
    Use the --ebuild option to install ebuild(source) packages.

    * Examples:

        sisyphus install pidgin

    will install pidgin binary package (if available); if there is none, but the ebuild(source) package for pidgin is found, it will stop and suggest the --ebuild option.

        sisyphus install pidgin --ebuild

    will compile pidgin from source

    The --ebuild option will preffer to reuse binary packages(if available) to satisfy the dependencies for the ebuild(source) package, speeding up the installation.
    You can use the --ebuild option even if you don't want to install any ebuild(source) packages; It will fall back to binary packages only.
    """
    if not ebuild:
        sisyphus.install.start(pkgname)
    else:
        sisyphus.install.estart(pkgname)

@app.command("uninstall")
def uninstall(pkgname: List[str], force: bool = typer.Option(False, "--force", "-f")):
    """Uninstall packages *SAFELY* by checking for reverse dependencies.
    If reverse dependencies exist, the package(s) will NOT be uninstalled to prevent the possible breakage of the system.
    If you really want to uninstall the package, make sure you uninstall all reverse dependencies as well.
    This will not allways be possible, as the reverse dependency chain may be way to long and require you to uninstall critical system packages.

    * Examples:

        sisyphus uninstall firefox

    will succeed, nothing depends on it

        sisyphus uninstall pulseaudio

    will fail, many packages depend on it

    With --force option, packages are uninstalled *UNSAFELY* by ignoring reverse dependencies.
    This may break your system if you uninstall critical packages.
    It will try the best it can to preserve the libraries required by other packages to prevent such a breakage.
    Upgrading the system may pull the packages back in, to fix the reverse dependency chain.

    * Examples :

        sisyphus uninstall pulseaudio --force

    will succeed, but you may no longer have audio

        sisyphus uninstall openrc --force

    will succeed, but the system will be broken
    """
    if not force:
        sisyphus.uninstall.start(pkgname)
    else:
        sisyphus.uninstall.fstart(pkgname)

@app.command("autoremove")
def autoremove():
    """Uninstall packages that are no longer needed.
    When you uninstall a package without it's reverse dependencies, those dependencies will become orphans if nothing else requires them.
    In addition, a package may no longer depend on another one, so that other package becomes orphan as well if nothing else requires it.
    Use this option to check the whole dependency chain for such packages, and uninstall them.
    """
    sisyphus.autoremove.start()

@app.command("update")
def update():
    """Update the Portage tree, the Redcore Overlay(s), Portage configs and Sisyphus's package database."""
    if sisyphus.checkenv.root():
        sisyphus.update.start()
    else:
        sys.exit("\nYou need root permissions to do this, exiting!\n")

@app.command("upgrade")
def upgrade(ebuild: bool = typer.Option(False, "--ebuild", "-e")):
    """Upgrade the system using binary and/or ebuild (source) packages.
    By default, only binary packages will be upgraded.
    However, if you installed any ebuild(source) packages with the '--ebuild' option, it would make sense to upgrade them too.
    Use the --ebuild option to upgrade **EVERYTHING**, binary and/or ebuild(source) packages.

    * Examples:

        sisyphus upgrade

    will upgrade the system using binary packages; if any ebuild(source) package upgrade is detected, it will stop and suggest the --ebuild option

        sisyphus upgrade --ebuild

    will upgrade the system using both binary and/or ebuild(source) packages

    The --ebuild option will preffer to reuse binary packages(if available) to satisfy the dependencies for the ebuild(source) packages, speeding up the upgrade.
    You can use the --ebuild option even if you don't have any ebuild(source) packages installed; It will fall back to binary packages only.
    """
    if not ebuild:
        sisyphus.upgrade.start()
    else:
        sisyphus.upgrade.estart()

@app.command("spmsync")
def spmsync():
    """Sync Sisyphus's package database with Portage's package database.
    When you install something with Portage directly (emerge), Sisyphus is not aware of that package, and it doesn't track it in it's database.
    Use this command to synchronize Sisyphus's package database with Portage's package database.
    """
    sisyphus.syncspm.start()

@app.command("rescue")
def rescue():
    """Resurrect Sisyphus's package database if lost or corrupted.
    If for some reason Sisyphus's package database is lost or corrupted, it can be resurrected using Portage's package database.
    If Portage's package database is corrupted (in this case you're screwed anyway :D), only a partial resurrection will be possible.
    If Portage's package database is intact, full resurrection will be possible.
    """
    sisyphus.recoverdb.start()

class Branch(str, Enum):
    master = 'master'
    next = 'next'

class Remote(str, Enum):
    gitlab = 'gitlab'
    pagure = 'pagure'

@app.command("branch")
def branch(branch: Branch = typer.Argument(...), remote: Remote = typer.Option(Remote.pagure, "--remote", "-r")):
    """Pull the selected branch of the Portage tree, Redcore overlay and Portage configs.
    The remote can be selected by using the --remote option.

    'BRANCH' can be one of the following : master, next

    'REMOTE' can be one of the following : gitlab, pagure (default is pagure)

    * Examples:

        branch master --remote=gitlab   # pull the branch 'master' from gitlab.com

        branch next --remote=pagure     # pull the branch 'next' from pagure.io

    !!! WARNING !!!

    Once you changed the branch, you must pair it with the correct binhost (binary repository).

    Branch 'master' must be paired with the stable binhost (binary repository) (odd numbers in 'sisyphus mirror list').

    * Examples:

        sisyphus mirror set 1

        sisyphus mirror set 5

    Branch 'next' must be paired with the testing binhost (binary repository) (even numbers in 'sisyphus mirror list').

    * Examples:

        sisyphus mirror set 2

        sisyphus mirror set 8
    """
    sisyphus.setbranch.start(branch.value, remote.value)

@app.command("sysinfo")
def sysinfo():
    """Display information about installed core packages and portage configuration."""
    sisyphus.sysinfo.show()

@mirrorSetup.command("list")
def mirrorlist():
    """List available binary package repository mirrors (the active one is marked with *)."""
    sisyphus.mirrors.printList()

@mirrorSetup.command("set")
def mirrorset(index: int):
    """Change the binary package repository to the selected mirror."""
    sisyphus.mirrors.setActive(index)

if __name__ == "__main__":
    if len(sys.argv) > 1 and not '--help' in sys.argv:
        sisyphus.setjobs.start()
    app()
