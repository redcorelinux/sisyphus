#!/usr/bin/python3

import sisyphus
import typer
from typing import List
from enum import Enum
import sys

app = typer.Typer()
mirrorSetup = typer.Typer()
app.add_typer(mirrorSetup, name="mirror",
              help='List/Set the active binhost (binary repository) mirror.')


@app.callback()
def app_callback(ctx: typer.Context):
    """
    Sisyphus is a simple python wrapper around portage, gentoolkit, and portage-utils\n
    which provides an apt-get/yum-alike interface to these commands, to assist newcomers\n
    transitioning from Debian/RedHat-based systems to Gentoo.\n

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
           desc: str = typer.Option(
               '', '--description', '-d', help='Match description.'),
           filter: Filter = typer.Option(
               Filter.all, '--filter', '-f', show_default=True),
           quiet: bool = typer.Option(
               False, '-q', help='Short (one line) output.'),
           ebuild: bool = typer.Option(False, "--ebuild", "-e", help='Search in ebuilds (slower).')):
    """Search for binary and/or ebuild (source) packages.\n
    By default will search for binary packages, using internal database.\n
    The search term can be provided also in the category/name format.\n
    \n
    * Examples:\n
        sisyphus search openbox\n
        sisyphus search x11-wm/openbox\n
    \n
    Using * and ? wildcards is supported. An empty string will match everything (similar to *).\n
    \n
    * Examples:\n
        sisyphus search x11-wm/     # search all packages in the x11-wm category\n
        sisyphus search x11-wm/*    # search all packages in the x11-wm category\n
    \n
    In addition, search can be performed by package description, using the -d (--description) option:\n
    \n
    * Examples:\n
        sisyphus search x11/open -d 'window manager'    # use single or double quotes when the description contains spaces\n
    \n
    Use the -f (--filter) option to select only packages of interest. Possible values:\n
    \n
        all (default)   - search the entire database\n
        alien           - search for installed packages but not available     # (this filter can match packages installed from ebuilds or packages no longer maintained as binaries)\n
        installed       - search in all installed packages\n
        available       - search for available packages but not installed\n
        upgradable      - search for installed packages where installed version is different from available version\n
    \n
    !!! NOTE !!!\n
    \n
    Bash will expand a single * character as current folder listing.\n
    To search for all matching '--filter' packages you need to escape it, surround it with quotes, or just use an empty string.\n
    \n
    * Examples:\n
        sisyphus search * -f installed          # not valid\n
        sisyphus search \* -f alien             # valid\n
        sisyphus search '*' -f available        # valid\n
        sisyphus search '' -f upgradable        # valid\n
    \n
    To search for all (including source) packages, use the --ebuild option.\n
    This is slower since will perform an 'emerge --search' actually.\n
    With this option, more than one package can be provided as search term.\n
    '-d', '-f' and '-q' (quiet) options are ignored in this mode.\n
    """
    if not ebuild:
        if '/' in package[0]:
            cat, pn = package[0].split('/')
        else:
            cat, pn = '', package[0]
        sisyphus.searchdb.start(filter.value, cat, pn, desc, quiet)
    else:
        if not package:
            raise typer.Exit(
                'No search term provided, try: sisyphus search --help')
        else:
            sisyphus.searchdb.estart(package)


@app.command("install")
def install(pkgname: List[str],
            ebuild: bool = typer.Option(
                False, "--ebuild", "-e", help='Install ebuild(source) package if binary package is not found (slower).'),
            oneshot: bool = typer.Option(
                False, "--oneshot", "-1", help='Install the package without marking it as explicitly installed.'),
            nodeps: bool = typer.Option(False, "--nodeps", help='Install the package without retrieving its dependencies.')):
    """
    Install binary and/or ebuild(source) packages.\n
    Binary packages are default, however the --ebuild option can be used to install ebuild(source) packages.\n
    The --ebuild option will be recommended automatically if a binary package is not found but a corresponding ebuild (source) package is available.\n
    The --ebuild option will revert to binary packages when installation from an ebuild (source) package is unnecessary. This option can be safely used at all times.\n
    The --ebuild option will prioritize the use of binary packages (when available) to fulfill dependencies for the ebuild (source) package, thereby accelerating the installation process.\n
    The --oneshot option adheres to the aforementioned rules but does not designate the package as explicitly installed. In Gentoo Linux terminology, this means it is not added to the world set.\n
    The --nodeps option adheres to the aforementioned rules but does not retrieve the package dependecies. In conjunction with the --oneshot option, it can be used to quickly reinstall any already installed *BINARY* package.\n
    The options --ebuild, --oneshot, and --nodeps can be utilized independently or in conjunction with one another, in either their short or long forms.\n
    The sequence of utilizing the --ebuild, --oneshot, and --nodeps options is flexible; they can be applied before or after specifying the package name.\n
    \n
    !!! NOTE !!!\n
    \n
    To minimize the risk of inadvertent input or typographical errors, the --nodeps option is intentionally without a shortened form.\n
    \n
    !!! WARNING !!!\n
    \n
    Unless all required dependencies are already installed, attempting to install an ebuild (source) package using the --ebuild option in conjunction with the --nodeps option is likely to result in failure.\n
    \n
    * Examples:\n
        sisyphus install firefox\n
        sisyphus install pidgin --ebuild\n
        sisyphus install -e xonotic\n
        sisyphus install filezilla --oneshot\n
        sisyphus install -1 thunderbird\n
        sisyphus install falkon -e -1\n
        sisyphus install --nodeps --oneshot opera\n
        sisyphus install -e --nodeps vivaldi\n
    """
    if ebuild:
        sisyphus.pkgadd.start(
            pkgname, ebuild=True, gfx_ui=False, oneshot=oneshot, nodeps=nodeps)
    else:
        sisyphus.pkgadd.start(
            pkgname, ebuild=False, gfx_ui=False, oneshot=oneshot, nodeps=nodeps)


@app.command("uninstall")
def uninstall(pkgname: List[str], force: bool = typer.Option(False, "--force", "-f", help='Ignore the reverse dependencies and force uninstall the package (DANGEROUS)')):
    """
    Uninstall packages *SAFELY* by checking for reverse dependencies.\n
    To maintain system integrity, if there are any reverse dependencies, the package or packages will not be uninstalled to prevent system instability.\n
    If you're set on uninstalling the package or packages, consider removing all of its reverse dependencies first.\n
    However, this may not always be feasible due to the extensive nature of the reverse dependency tree, which could involve critical system packages.\n
    \n
    !!! DANGEROUS !!!\n
    \n
    The --force option will ignore the reverse dependencies and uninstall the package *UNSAFELY*, without safeguards.\n
    \n
    !!! WARNING !!!\n
    \n
    The --force option will break your system if you uninstall important system packages (bootloader, kernel, init).\n
    \n
    * Examples:\n
        sisyphus uninstall firefox              # this will succeed, no package depends on firefox\n
        sisyphus uninstall pulseaudio           # this will fail, many packages depend on pulseaudio\n
        sisyphus uninstall pulseaudio --force   # this will succeed, but the sound may no longer work\n
        sisyphus uninstall openrc -f            # this will succeed, but the system will no longer boot\n
    """
    if force:
        sisyphus.pkgremove.start(
            pkgname, depclean=False, gfx_ui=False, unmerge=True)
    else:
        sisyphus.pkgremove.start(
            pkgname, depclean=True, gfx_ui=False, unmerge=False)


@app.command("autoremove")
def autoremove():
    """
    Uninstall packages which become orphans and which are no longer needed.\n
    Uninstalling a package will usually leave its dependencies behind.\n
    Those dependencies become orphans if no other package requires them.\n
    A package may also gain extra dependencies or lose some dependencies.\n
    The lost dependencies become orphans if no other package requires them.\n
    In either case, the orphan packages are no longer needed and can be safely removed.\n
    Use this option to check the whole dependency tree for orphan packages, and remove them.\n
    \n
    * Examples:\n
        sisyphus autoremove\n
    """
    sisyphus.sysclean.start(gfx_ui=False)


@app.command("autoclean")
def autoclean():
    """
    Clean the binary package cache and the source tarball cache.\n
    \n
    * Examples:\n
        sisyphus autoclean\n
    """
    if sisyphus.checkenv.root():
        sisyphus.purgeenv.cache()
    else:
        sys.exit("\nYou need root permissions to do this, exiting!\n")


@app.command("update")
def update():
    """
    Update the source trees, package configs (USE flags, keywords, masks, etc) and the binary package database.\n
    \n
    * Examples:\n
        sisyphus update\n
    """
    if sisyphus.checkenv.root():
        sisyphus.syncall.start(gfx_ui=False)
    else:
        sys.exit("\nYou need root permissions to do this, exiting!\n")


@app.command("upgrade")
def upgrade(
        ebuild: bool = typer.Option(False, "--ebuild", "-e", help='Upgrade all packages, including ebuild(source) packages (slower)')):
    """
    Upgrade the system using binary and/or ebuild(source) packages.\n
    Binary packages are default, however the --ebuild option can be used to upgrade the ebuild(source) packages as well, alongside the binary packages.\n
    The --ebuild option will be automatically recommended if upgrades are necessary for the ebuild (source) packages, in addition to the binary packages.\n
    The --ebuild option will default to binary packages if upgrades are unnecessary for the ebuild (source) packages. This option is safe to use at all times.\n
    The --ebuild option will prioritize the use of binary packages (when available) to fulfill dependencies for the ebuild (source) packages, thereby accelerating the upgrade process.\n
    \n
    * Examples:\n
        sisyphus upgrade\n
        sisyphus upgrade --ebuild\n
        sisyphus upgrade -e\n
    """
    if ebuild:
        sisyphus.sysupgrade.start(ebuild=True, gfx_ui=False)
    else:
        sisyphus.sysupgrade.start(ebuild=False, gfx_ui=False)


@app.command("spmsync")
def spmsync():
    """
    Sync Sisyphus's package database with Portage's package database.\n
    Sisyphus doesn't monitor packages installed directly via Portage in its package database.\n
    Use this command to align Sisyphus's package database with Portage's package database.\n
    \n
    * Examples:\n
        sisyphus spmsync\n
    """
    sisyphus.syncspm.start()


@app.command("rescue")
def rescue():
    """
    Resurrect Sisyphus's package database if it becomes lost or corrupted.\n
    If, for any reason, Sisyphus's package database becomes lost or corrupted, it can be resurrected using Portage's package database.\n
    In the event of corruption in Portage's package database (in which case, you're in trouble anyway :D), only partial resurrection will be feasible.\n
    With Portage's package database intact, complete resurrection will be achievable.\n
    \n
    * Examples:\n
        sisyphus rescue\n
    """
    sisyphus.recoverdb.start()


class Branch(str, Enum):
    master = 'master'
    next = 'next'


class Remote(str, Enum):
    github = 'github'
    gitlab = 'gitlab'
    pagure = 'pagure'


@app.command("branch")
def branch(branch: Branch = typer.Argument(...), remote: Remote = typer.Option(Remote.gitlab, "--remote", "-r")):
    """
    Switch between the branches of Redcore Linux : 'master' (stable) or 'next' (testing), default branch is 'master' (stable)\n
    Reconfigure the source trees, package configs (USE flags, keywords, masks, etc) and the binhost (binary repository)\n
    Selection of a remote is optional (default is gitlab), but it can be accomplished by using the --remote option.\n
    'BRANCH' can be one of the following : master, next\n
    'REMOTE' can be one of the following : github, gitlab, pagure (default is gitlab)\n
    \n
    * Examples:\n
        sisyphus branch master                  # switch to branch 'master', use default remote (gitlab)\n
        sisyphus branch next                    # switch to branch 'next', use default remote (gitlab)\n
        sisyphus branch master --remote=github  # switch to branch 'master', use github remote\n
        sisyphus branch next --remote=pagure    # switch to branch 'next', use pagure remote\n
    \n
    Sisyphus will automatically pair the selected branch with the correct binhost (binary repository).\n
    However, since no geolocation is ever used, it may select one which is geographically far from you.\n
    If that is inconvenient, you can manually select a binhost (binary repository) closer to your location,\n
    \n
    !!! WARNING !!!\n
    \n
    Branch 'master' must be paired with the stable binhost (binary repository) (odd numbers in 'sisyphus mirror list').\n
    * Examples:\n
        sisyphus mirror set 1\n
        sisyphus mirror set 5\n
    \n
    Branch 'next' must be paired with the testing binhost (binary repository) (even numbers in 'sisyphus mirror list').\n
    * Examples:\n
        sisyphus mirror set 2\n
        sisyphus mirror set 8\n
    """
    sisyphus.setbranch.start(branch.value, remote.value)


@app.command("sysinfo")
def sysinfo():
    """
    Display information about installed core packages and portage configuration.\n
    \n
    * Examples:\n
        sisyphus sysinfo\n
    """
    sisyphus.sysinfo.show()


@mirrorSetup.command("list")
def mirrorlist():
    """
    List available binary package repository mirrors (the active one is marked with *).\n
    \n
    * Examples:\n
        sisyphus mirror list\n
    """
    sisyphus.setmirror.printList()


@mirrorSetup.command("set")
def mirrorset(index: int):
    """
    Change the binary package repository to the selected mirror.\n
    \n
    * Examples:\n
        sisyphus mirror set 2\n
        sisyphus mirror set 5\n
    """
    sisyphus.setmirror.setActive(index)


if __name__ == "__main__":
    if len(sys.argv) > 1 and not '--help' in sys.argv:
        sisyphus.setjobs.start()
    app()
