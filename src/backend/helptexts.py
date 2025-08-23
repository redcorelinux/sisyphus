#!/usr/bin/python3

SEARCH = """Search for binary and/or ebuild (source) packages.
Default: binary packages. Use --ebuild to search source packages.
Supports wildcards (* and ?).

Options:\n
  --ebuild / -e   Search source packages.\n

Examples:\n
  sisyphus search openbox\n
  sisyphus search x11-wm/openbox\n
  sisyphus search x11-wm/*\n
  sisyphus search '' -f upgradable\n
  sisyphus search x11/open -d 'window manager'\n
  sisyphus search -e firefox thunderbird\n
"""

INSTALL = """Install binary and/or ebuild (source) packages.
Default: binary packages. Use --ebuild to install source packages.

Options:\n
  --ebuild / -e   Install source packages.\n
  --oneshot / -1  Do not mark package as explicitly installed.\n
  --nodeps        Do not install dependencies.\n
  --onlydeps      Install only dependencies.\n

Examples:\n
  sisyphus install firefox\n
  sisyphus install pidgin --ebuild\n
  sisyphus install filezilla --oneshot\n
  sisyphus install -e --onlydeps vivaldi\n
"""

UNINSTALL = """Uninstall packages safely (or forcefully if --force is used).
Default: uninstall safely. Use --force to force uninstall (DANGEROUS).

Options:\n
  --force / -f   Force uninstall ignoring reverse deps (DANGEROUS).\n

Examples:\n
  sisyphus uninstall firefox\n
  sisyphus uninstall pulseaudio\n
  sisyphus uninstall pulseaudio --force\n
"""

AUTOREMOVE = """Uninstall orphaned packages no longer required by the system.

Example:\n
  sisyphus autoremove\n
"""

AUTOCLEAN = """Clean binary & source caches.

Example:\n
  sisyphus autoclean\n
"""

UPDATE = """Update source trees, configs, and binary DB.

Example:\n
  sisyphus update\n
"""

UPGRADE = """Upgrade the system.
Default: binary packages. Use --ebuild to upgrade source packages.

Options:\n
  --ebuild / -e   Upgrade source packages.\n
Examples:\n
  sisyphus upgrade\n
  sisyphus upgrade --ebuild\n
"""

SPMSYNC = """Sync Sisyphus DB with Portage DB.

Example:\n
  sisyphus spmsync\n
"""

RESCUE = """Resurrect Sisyphus DB if lost or corrupted.

Example:\n
  sisyphus rescue\n
"""

SYSINFO = """Show information about installed core packages and Portage config.

Example:\n
  sisyphus sysinfo\n
"""

MIRROR_LIST = """List binary package repository mirrors.
The active one is marked with *.

Example:\n
  sisyphus mirror list\n
"""

MIRROR_SET = """Switch to a different binary package mirror.

Examples:\n
  sisyphus mirror set 2\n
  sisyphus mirror set 5\n
"""

NEWS_LIST = """List all news articles.

Example:\n
  sisyphus news list\n
"""

NEWS_READ = """Mark a news article as read.

Example:\n
  sisyphus news read 1\n
"""

NEWS_UNREAD = """Mark a news article as unread.

Example:\n
  sisyphus news unread 2\n
"""

BRANCH = """Switch or purge Redcore Linux branches.

Branches:\n
  master = stable (use odd-number mirrors)\n
  next   = testing (use even-number mirrors)\n
  purge  = purge all configs and source trees\n

Remotes:\n
  github, gitlab (default), pagure\n

Examples:\n
  sisyphus branch master\n
  sisyphus branch master --remote=github\n
  sisyphus branch purge\n
"""
