# `sisyphus`

Sisyphus is a simple python wrapper around portage, gentoolkit, and portage-utils
which provides an apt-get/yum-alike interface to these commands,
to assist newcomer people transitioning from Debian/RedHat-based systems to Gentoo.

Use 'sisyphus COMMAND --help' for detailed usage.

**Usage**:

```console
$ sisyphus [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `autoremove`: Uninstall packages that are no longer needed.
* `autoclean` : Clean the binary package cache...
* `branch`: Pull the selected branch of the Portage tree,...
* `install`: Install binary and/or ebuild(source)...
* `mirror`: List/Set the active binhost (binary repository) mirror.
* `rescue`: Resurrect Sisyphus's package database if lost...
* `search`: Search for binary and/or ebuild (source)...
* `spmsync`: Sync Sisyphus's package database with...
* `sysinfo`: Display information about installed core...
* `uninstall`: Uninstall packages *SAFELY* by checking for...
* `update`: Update the Portage tree, the Redcore...
* `upgrade`: Upgrade the system using binary and/or ebuild...

## `sisyphus autoremove`

Uninstall packages that are no longer needed.
When you uninstall a package without it's reverse dependencies, those dependencies will become orphans if nothing else requires them.
In addition, a package may no longer depend on another one, so that other package becomes orphan as well if nothing else requires it.
Use this option to check the whole dependency chain for such packages, and uninstall them.

**Usage**:

```console
$ sisyphus autoremove [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.


## `sisyphus autoclean`

Clean the binary package cache and the source tarball cache

**Usage**:

```console
$ sisyphus autoclean [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `sisyphus branch`

Pull the selected branch of the Portage tree, Redcore overlay and Portage configs.
The remote can be selected by using the --remote option.

'BRANCH' can be one of the following : master, next

'REMOTE' can be one of the following : gitlab, pagure (default is pagure)

* Examples:


`    branch master --remote=gitlab   # pull the branch 'master' from gitlab.com
`

`    branch next --remote=pagure     # pull the branch 'next' from pagure.io
`


!!! WARNING !!!

Once you changed the branch, you must pair it with the correct binhost (binary repository).

Branch 'master' must be paired with the stable binhost (binary repository) (odd numbers in 'sisyphus mirror list').

* Examples:

`    sisyphus mirror set 1
`

`    sisyphus mirror set 5
`

Branch 'next' must be paired with the testing binhost (binary repository) (even numbers in 'sisyphus mirror list').

* Examples:

`    sisyphus mirror set 2
`

`    sisyphus mirror set 8
`


**Usage**:

```console
$ sisyphus branch [OPTIONS] [master|next]
```

**Options**:

* `-r, --remote [gitlab|pagure]`
* `--help`: Show this message and exit.

## `sisyphus install`

Install binary and/or ebuild(source) packages.
By default, only binary packages will be installed.
Use the --ebuild option to install ebuild(source) packages.

* Examples:

`    sisyphus install pidgin`

will install pidgin binary package (if available); if there is none, but the ebuild(source) package for pidgin is found, it will stop and suggest the --ebuild option.

`    sisyphus install pidgin --ebuild`

will compile pidgin from source

The --ebuild option will preffer to reuse binary packages(if available) to satisfy the dependencies for the ebuild(source) package, speeding up the installation.
You can use the --ebuild option even if you don't want to install any ebuild(source) packages; It will fall back to binary packages only.

**Usage**:

```console
$ sisyphus install [OPTIONS] PKGNAME...
```

**Options**:

* `-e, --ebuild`
* `--help`: Show this message and exit.

## `sisyphus mirror`

List/Set the active binhost (binary repository) mirror.

**Usage**:

```console
$ sisyphus mirror [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `list`: List available binary package repository...
* `set`: Change the binary package repository to the...

### `sisyphus mirror list`

List available binary package repository mirrors (the active one is marked with *).

**Usage**:

```console
$ sisyphus mirror list [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `sisyphus mirror set`

Change the binary package repository to the selected mirror.

**Usage**:

```console
$ sisyphus mirror set [OPTIONS] INDEX
```

**Options**:

* `--help`: Show this message and exit.

## `sisyphus rescue`

Resurrect Sisyphus's package database if lost or corrupted.
If for some reason Sisyphus's package database is lost or corrupted, it can be resurrected using Portage's package database.
If Portage's package database is corrupted (in this case you're screwed anyway :D), only a partial resurrection will be possible.
If Portage's package database is intact, full resurrection will be possible.

**Usage**:

```console
$ sisyphus rescue [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `sisyphus search`

Search for binary and/or ebuild (source) packages.

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

**Usage**:

```console
$ sisyphus search [OPTIONS] PACKAGE...
```

**Options**:

* `-d, --description TEXT`: Match description.
* `-f, --filter [all|alien|installed|available|upgradable]`: [default: all]
* `-q`: Short (one line) output.
* `-e, --ebuild`: Search in ebuilds (slower).
* `--help`: Show this message and exit.

## `sisyphus spmsync`

Sync Sisyphus's package database with Portage's package database.
When you install something with Portage directly (emerge), Sisyphus is not aware of that package, and it doesn't track it in it's database.
Use this command to synchronize Sisyphus's package database with Portage's package database.

**Usage**:

```console
$ sisyphus spmsync [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `sisyphus sysinfo`

Display information about installed core packages and portage configuration.

**Usage**:

```console
$ sisyphus sysinfo [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `sisyphus uninstall`

Uninstall packages *SAFELY* by checking for reverse dependencies.
If reverse dependencies exist, the package(s) will NOT be uninstalled to prevent the possible breakage of the system.
If you really want to uninstall the package, make sure you uninstall all reverse dependencies as well.
This will not allways be possible, as the reverse dependency chain may be way to long and require you to uninstall critical system packages.

* Examples:

`   sisyphus uninstall firefox`
will succeed, nothing depends on it 

`    sisyphus uninstall pulseaudio`
will fail, many packages depend on it

With --force option, packages are uninstalled *UNSAFELY* by ignoring reverse dependencies.
This may break your system if you uninstall critical packages.
It will try the best it can to preserve the libraries required by other packages to prevent such a breakage.
Upgrading the system may pull the packages back in, to fix the reverse dependency chain.

* Examples :

`    sisyphus uninstall pulseaudio --force`
will succeed, but you may no longer have audio

`    sisyphus uninstall openrc --force`
will succeed, but the system will be broken

**Usage**:

```console
$ sisyphus uninstall [OPTIONS] PKGNAME...
```

**Options**:

* `-f, --force`
* `--help`: Show this message and exit.

## `sisyphus update`

Update the Portage tree, the Redcore Overlay(s), Portage configs and Sisyphus's package database.

**Usage**:

```console
$ sisyphus update [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `sisyphus upgrade`

Upgrade the system using binary and/or ebuild (source) packages.
By default, only binary packages will be upgraded.
However, if you installed any ebuild(source) packages with the '--ebuild' option, it would make sense to upgrade them too.
Use the --ebuild option to upgrade **EVERYTHING**, binary and/or ebuild(source) packages.

* Examples:

`    sisyphus upgrade`

will upgrade the system using binary packages; if any ebuild(source) package upgrade is detected, it will stop and suggest the --ebuild option

`    sisyphus upgrade --ebuild`

will upgrade the system using both binary and/or ebuild(source) packages

The --ebuild option will preffer to reuse binary packages(if available) to satisfy the dependencies for the ebuild(source) packages, speeding up the upgrade.
You can use the --ebuild option even if you don't have any ebuild(source) packages installed; It will fall back to binary packages only.

**Usage**:

```console
$ sisyphus upgrade [OPTIONS]
```

**Options**:

* `-e, --ebuild`
* `--help`: Show this message and exit.
