#!/usr/bin/python3

import sisyphus
import typer
from typing import List

sisyphus.check.update()
sisyphus.setjobs.start.__wrapped__() # undecorate

app = typer.Typer()
mirrorSetup = typer.Typer()
app.add_typer(mirrorSetup, name="mirror", help='List/Set the active binary repository mirror.')

@app.callback()
def app_callback():
    """Sisyphus is a simple python wrapper around portage, gentoolkit, and portage-utils
    which provides an apt-get/yum-alike interface to these commands,
    to assist newcomer people transitioning from Debian/RedHat-based systems to Gentoo.

    Use 'sisyphus COMMAND --help' for detailed usage.
    """
    pass

@app.command("search")
def search(pkgname: List[str]):
    """Search for binary and/or ebuild (source) packages."""
    sisyphus.search.start(pkgname)

@app.command("install")
def install(pkgname: List[str], hybrid: bool = typer.Option(False, "--hybrid")):
    """Install binary and/or ebuild(source) packages.
    By default, only binary packages will be installed.
    Use the --hybrid option to install ebuild(source) packages.

    * Examples:

    'sisyphus install pidgin'

    will install pidgin binary package (if available); if there is none, but the ebuild(source) package for pidgin is found, it will stop and suggest the --hybrid option.

    'sisyphus install pidgin --hybrid'

    will compile pidgin from source

    The --hybrid option will preffer to reuse binary packages(if available) to satisfy the dependencies for the ebuild(source) package, speeding up the installation.
    You can use the --hybrid option even if you don't want to install any ebuild(source) packages; It will fall back to binary packages only.
    """
    if not hybrid:
        sisyphus.install.start(pkgname)
    else:
        sisyphus.installhybrid.start(pkgname)

@app.command("uninstall")
def uninstall(pkgname: List[str], force: bool = typer.Option(False, "--force")):
    """Uninstall packages *SAFELY* by checking for reverse dependencies.
    If reverse dependencies exist, the package(s) will NOT be uninstalled to prevent the possible breakage of the system.
    If you really want to uninstall the package, make sure you uninstall all reverse dependencies as well.
    This will not allways be possible, as the reverse dependency chain may be way to long and require you to uninstall critical system packages.

    * Examples:

    'sisyphus uninstall firefox'

    will succeed, nothing depends on it

    'sisyphus uninstall pulseaudio'

    will fail, many packages depend on it

    With --force option, packages are uninstalled *UNSAFELY* by ignoring reverse dependencies.
    This may break your system if you uninstall critical packages.
    It will try the best it can to preserve the libraries required by other packages to prevent such a breakage.
    Upgrading the system may pull the packages back in, to fix the reverse dependency chain.

    * Examples :

    'sisyphus uninstall pulseaudio --force'

    will succeed, but you may no longer have audio

    'sisyphus uninstall openrc --force'

    will succeed, but the system will be broken
    """
    if not force:
        sisyphus.uninstall.start(pkgname)
    else:
        sisyphus.uninstallforce.start(pkgname)

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
    sisyphus.update.start()

@app.command("upgrade")
def upgrade(hybrid: bool = typer.Option(False, "--hybrid")):
    """Upgrade the system using binary and/or ebuild (source) packages.
    By default, only binary packages will be upgraded.
    However, if you installed any ebuild(source) packages with the '--hybrid' option, it would make sense to upgrade them too.
    Use the --hybrid option to upgrade **EVERYTHING**, binary and/or ebuild(source) packages.

    * Examples:

    'sisyphus upgrade'

    will upgrade the system using binary packages; if any ebuild(source) package upgrade is detected, it will stop and suggest the --hybrid option

    'sisyphus upgrade --hybrid'

    will upgrade the system using both binary and/or ebuild(source) packages

    The --hybrid option will preffer to reuse binary packages(if available) to satisfy the dependencies for the ebuild(source) packages, speeding up the upgrade.
    You can use the --hybrid option even if you don't have any ebuild(source) packages installed; It will fall back to binary packages only.
    """
    if not hybrid:
        sisyphus.upgrade.start()
    else:
        sisyphus.upgradehybrid.start()

@app.command("spmsync")
def spmsync():
    """Sync Sisyphus's package database with Portage's package database.
    When you install something with Portage directly (emerge), Sisyphus is not aware of that package, and it doesn't track it in it's database.
    Use this command to synchronize Sisyphus's package database with Portage's package database.
    """
    sisyphus.spmsync.start()

@app.command("rescue")
def rescue():
    """Resurrect Sisyphus's package database if lost or corrupted.
    If for some reason Sisyphus's package database is lost or corrupted, it can be resurrected using Portage's package database.
    If Portage's package database is corrupted (in this case you're screwed anyway :D), only a partial resurrection will be possible.
    If Portage's package database is intact, full resurrection will be possible.
    """
    sisyphus.rescue.start()

@app.command("branch")
def branch(branch: str = typer.Argument(...), remote: str = typer.Option(...)):
    """Pull the branch 'BRANCH' of the Portage tree, Redcore overlay and Portage configs,
    using 'REMOTE' git repositories.

    'BRANCH' can be one of the following : master, next

    'REMOTE' can be one of the following : gitlab, pagure

    * Examples:

    'branch master --remote=gitlab' will pull the branch 'master' from gitlab.com

    'branch next --remote=pagure' will pull the branch 'next' from pagure.io

    !!! WARNING !!!

    Once you changed the branch, you must pair the branch 'BRANCH' with the correct binary repository.

    Branch 'master' must be paired with the stable binary repository (odd numbers in 'sisyphus mirror list').

    * Examples : 'sisyphus mirror set 1' or 'sisyphus mirror set 5'

    Branch 'next' must be paired with the testing binary repository (even numbers in 'sisyphus mirror list').

    * Examples : 'sisyphus mirror set 2' or 'sisyphus mirror set 8'
    """
    sisyphus.branchsetup.start(branch, remote)

@app.command("sysinfo")
def sysinfo():
    """Display information about installed core packages and portage configuration."""
    sisyphus.sysinfo.show()

@mirrorSetup.command("list")
def mirrorlist():
    """List available binary package repository mirrors (the active one is marked with *)."""
    sisyphus.mirror.printList()

@mirrorSetup.command("set")
def mirrorset(index: int):
    """Change the binary package repository to the selected mirror."""
    sisyphus.mirror.setActive(index)

if __name__ == "__main__":
    app()
