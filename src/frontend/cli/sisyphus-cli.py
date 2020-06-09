#!/usr/bin/python3

import sisyphus
import typer
from typing import List

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

@app.command("update")
def update():
    """Update the Portage tree, the Redcore Overlay(s), Portage configs and Sisyphus's package database."""
    typer.echo("Updating system ...")

@app.command("upgrade")
def upgrade():
    """Upgrade the system using binary and/or ebuild (source) packages."""
    typer.echo("Upgrading all packages ...")

@app.command("install")
def install(pkglist: List[str]):
    """Install binary and/or ebuild (source) packages."""
    [typer.echo(f"Installing {pkg}") for pkg in pkglist]

@app.command("uninstall")
def uninstall(pkglist: List[str], force: bool = False):
    """Uninstall packages *SAFELY* by checking for reverse dependencies.
    If reverse dependencies exist, the package(s) will NOT be uninstalled to prevent the possible breakage of the system.
    If you really want to uninstall the package, make sure you uninstall all reverse dependencies as well.
    This will not allways be possible, as the reverse dependency chain may be way to long and require you to uninstall critical system packages.

    Using the --force option, packages are uninstalled *UNSAFELY* by ignoring reverse dependencies.
    This may break your system if you uninstall critical system packages.
    It will try the best it can to preserve the libraries required by other packages to prevent such a breakage.
    Upgrading the system may pull the packages back in, to fix the reverse dependency chain.
    """
    if not force:
        [typer.echo(f"Safely removing {pkg}") for pkg in pkglist]
    else:
        [typer.echo(f"Force removing {pkg}") for pkg in pkglist]

@app.command("autoremove")
def autoremove():
    """Uninstall packages that are no longer needed.
    When you uninstall a package without it's reverse dependencies, those dependencies will become orphans if nothing else requires them.
    In addition, a package may no longer depend on another one, so that other package becomes orphan as well if nothing else requires it.
    Use this option to check the whole dependency chain for such packages, and uninstall them.
    """
    typer.echo("Performing cleanup ... ")

@app.command("search")
def install(pkglist: List[str]):
    """Search for binary and/or ebuild (source) packages."""
    [typer.echo(f"Searching for {pkg}") for pkg in pkglist]

@app.command("spmsync")
def spmsync():
    """Sync Sisyphus's package database with Portage's package database.
    When you install something with Portage directly (emerge), Sisyphus is not aware of that package, and it doesn't track it in it's database.
    Use this command to synchronize Sisyphus's package database with Portage's package database.
    """
    typer.echo("Syncing sisyphus database ...")

@app.command("rescue")
def rescue():
    """Resurrect Sisyphus's package database if lost or corrupted.
    If for some reason Sisyphus's package database is lost or corrupted, it can be resurrected using Portage's package database.
    If Portage's package database is corrupted (in this case you're screwed anyway :D), only a partial resurrection will be possible.
    If Portage's package database is intact, full resurrection will be possible.
    """
    typer.echo("Syncing sisyphus database ...")

@app.command("branch")
def branch(branch: str = typer.Argument('master'), remote: str = typer.Option('pagure')):
    """Pull the branch 'BRANCH' of the Portage tree, Redcore overlay and Portage configs,
    using 'REMOTE' git repositories.

    'BRANCH' can be one of the following : master, next (default is master)

    'REMOTE' can be one of the following : gitlab, pagure (default is pagure)

    * Examples:

    'branch master --remote gitlab' will pull the branch 'master' from gitlab.com

    'branch next --remote pagure' will pull the branch 'next' from pagure.io

    !!! WARNING !!!

    Once you changed the branch, you must pair the branch 'BRANCH' with the correct binary repository.

    Branch 'master' must be paired with the stable binary repository (odd numbers in 'sisyphus mirror list').

    * Examples : 'sisyphus mirror set 1' or 'sisyphus mirror set 5'

    Branch 'next' must be paired with the testing binary repository (even numbers in 'sisyphus mirror list').

    * Examples : 'sisyphus mirror set 2' or 'sisyphus mirror set 8'
    """
    typer.echo(f"Injecting {branch} branch from {remote} repository")

@app.command("sysinfo")
def sysinfo():
    """Display information about installed core packages and portage configuration."""
    typer.echo("Syncing sisyphus database ...")

@mirrorSetup.command("list")
def mirrorlist():
    """List available binary package repository mirrors (* means active)."""
    sisyphus.mirror.printList()

@mirrorSetup.command("set")
def mirrorset(index: int):
    """Change the binary package repository to the selected mirror."""
    sisyphus.mirror.setActive(index)

if __name__ == "__main__":
    app()
