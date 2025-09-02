#!/usr/bin/python3

import sys
import click
import typer
import sisyphus
from typing import List
from enum import Enum

app = typer.Typer()
first_run = typer.Typer()
news = typer.Typer()
mirror = typer.Typer()

app.add_typer(news, name="news", help="News management commands.")
app.add_typer(mirror, name="mirror", help="Mirror management commands.")


class Filter(str, Enum):
    all = "all"
    alien = "alien"
    installed = "installed"
    available = "available"
    upgradable = "upgradable"


class Branch(str, Enum):
    master = "master"
    next = "next"
    purge = "purge"


class Remote(str, Enum):
    github = "github"
    gitlab = "gitlab"
    pagure = "pagure"


def branch_setup(branch: Branch = typer.Argument(...),
                 remote: Remote = typer.Option(Remote.gitlab, "--remote", "-r")):
    if not sisyphus.checkenv.root():
        raise typer.Exit("\nYou need root permissions.\n")

    if branch.value == "purge":
        if any(arg.startswith("--remote") or arg.startswith("-r") for arg in sys.argv):
            raise typer.Exit(
                "\nThe 'purge' argument does not accept '--remote'.\n")
        sisyphus.purgeenv.branch()
        sisyphus.purgeenv.metadata()
    else:
        sisyphus.setbranch.start(branch.value, remote.value, gfx_ui=False)


@first_run.callback(invoke_without_command=True)
def interactive_first_run(ctx: typer.Context):
    if ctx.invoked_subcommand:
        return

    typer.secho(
        "Welcome to Sisyphus!\n\n"
        "This is your first time running the application.\n"
        "Please configure your settings to continue.\n",
        fg=typer.colors.GREEN,
    )

    branch_choice = typer.prompt(
        "Select branch to initialize",
        type=click.Choice(["master", "next"], case_sensitive=False),
        default="master",
    )
    remote_choice = typer.prompt(
        "Select remote to use",
        type=click.Choice(["github", "gitlab", "pagure"],
                          case_sensitive=False),
        default="gitlab",
    )

    branch_setup(branch=Branch(branch_choice.lower()),
                 remote=Remote(remote_choice.lower()))

    typer.secho("\nFirst-run setup complete!", fg=typer.colors.GREEN)
    raise typer.Exit(0)


@app.command("search", help=sisyphus.helptexts.SEARCH)
def search(package: List[str] = typer.Argument(...),
           desc: str = typer.Option("", "--description", "-d"),
           filter: Filter = typer.Option(
               Filter.all, "--filter", "-f", show_default=True),
           quiet: bool = typer.Option(False, "-q"),
           ebuild: bool = typer.Option(False, "--ebuild", "-e")):
    if not package:
        raise typer.Exit(
            "No search term provided, try: sisyphus search --help")

    if ebuild:
        sisyphus.searchdb.start("ebuild", "", package, "", quiet)
    else:
        cat, pn = package[0].split("/") if "/" in package else ("", package)
        sisyphus.searchdb.start(filter.value, cat, pn, desc, quiet)


@app.command("install", help=sisyphus.helptexts.INSTALL)
def install(pkgname: List[str],
            ebuild: bool = typer.Option(False, "--ebuild", "-e"),
            oneshot: bool = typer.Option(False, "--oneshot", "-1"),
            nodeps: bool = typer.Option(False, "--nodeps"),
            onlydeps: bool = typer.Option(False, "--onlydeps")):
    if nodeps and onlydeps:
        typer.secho(
            "Error: --nodeps and --onlydeps are mutually exclusive.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    sisyphus.pkgadd.start(
        pkgname, ebuild=ebuild, gfx_ui=False,
        oneshot=oneshot, nodeps=nodeps, onlydeps=onlydeps
    )


@app.command("uninstall", help=sisyphus.helptexts.UNINSTALL)
def uninstall(pkgname: List[str],
              force: bool = typer.Option(False, "--force", "-f")):
    depclean = True if not force else False
    unmerge = True if force else False
    sisyphus.pkgremove.start(
        pkgname,
        depclean=depclean,
        gfx_ui=False,
        unmerge=unmerge,
    )


@app.command("autoremove", help=sisyphus.helptexts.AUTOREMOVE)
def autoremove():
    sisyphus.sysclean.start(depclean=True, gfx_ui=False)


@app.command("autoclean", help=sisyphus.helptexts.AUTOCLEAN)
def autoclean():
    if not sisyphus.checkenv.root():
        raise typer.Exit("\nYou need root permissions.\n")
    sisyphus.purgeenv.cache()


@app.command("update", help=sisyphus.helptexts.UPDATE)
def update():
    if not sisyphus.checkenv.root():
        raise typer.Exit("\nYou need root permissions.\n")
    sisyphus.syncall.start(gfx_ui=False)


@app.command("upgrade", help=sisyphus.helptexts.UPGRADE)
def upgrade(ebuild: bool = typer.Option(False, "--ebuild", "-e")):
    sisyphus.sysupgrade.start(ebuild=ebuild, gfx_ui=False)


@app.command("spmsync", help=sisyphus.helptexts.SPMSYNC)
def spmsync():
    if not sisyphus.checkenv.root():
        raise typer.Exit("\nYou need root permissions.\n")
    sisyphus.syncspm.start()


@app.command("rescue", help=sisyphus.helptexts.RESCUE)
def rescue():
    if not sisyphus.checkenv.root():
        raise typer.Exit("\nYou need root permissions.\n")
    sisyphus.recoverdb.start()


@app.command("sysinfo", help=sisyphus.helptexts.SYSINFO)
def sysinfo():
    sisyphus.sysinfo.show()


@mirror.command("list", help=sisyphus.helptexts.MIRROR_LIST)
def list_mirrors():
    sisyphus.setmirror.printList()


@mirror.command("set", help=sisyphus.helptexts.MIRROR_SET)
def set_mirror(index: int):
    if not sisyphus.checkenv.root():
        raise typer.Exit("\nYou need root permissions.\n")
    sisyphus.setmirror.setActive(index)


@news.command("list", help=sisyphus.helptexts.NEWS_LIST)
def list_news():
    sisyphus.getnews.start(list=True)


@news.command("read", help=sisyphus.helptexts.NEWS_READ)
def read_news(index: int):
    if not sisyphus.checkenv.root():
        raise typer.Exit("\nYou need root permissions.\n")
    sisyphus.getnews.start(read=True, article_nr=index)


@news.command("unread", help=sisyphus.helptexts.NEWS_UNREAD)
def unread_news(index: int):
    if not sisyphus.checkenv.root():
        raise typer.Exit("\nYou need root permissions.\n")
    sisyphus.getnews.start(unread=True, article_nr=index)


app.command("branch", help=sisyphus.helptexts.BRANCH)(branch_setup)
first_run.command("branch", help=sisyphus.helptexts.BRANCH)(branch_setup)


@app.callback()
def app_callback(ctx: typer.Context):
    """
    Sisyphus is a simple python wrapper around portage, gentoolkit, and portage-utils\n
    which provides an apt-get/yum-alike interface to these commands, to assist newcomers\n
    transitioning from Debian/RedHat-based systems to Gentoo.\n

    Use 'sisyphus COMMAND --help' for detailed usage.
    """

    ctx.info_name = "sisyphus"


if __name__ == "__main__":
    if "--help" in sys.argv or "-h" in sys.argv:
        app()
        sys.exit(0)

    if not sisyphus.getmarkers.markers_exist():
        if len(sys.argv) > 1:
            typer.secho(
                "\nSisyphus is not initialized!\n\n"
                "First-time setup required before using commands.\n"
                "Run this program with no arguments to start setup wizard.\n",
                fg=typer.colors.RED,
            )
            sys.exit(1)

        first_run()
        sys.exit(0)

    if len(sys.argv) > 1:
        sisyphus.setjobs.start()

    app()
