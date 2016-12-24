#!/usr/bin/env bash

# export yad worker variable
export local showdialog="yad --title "sisyphus" --text-info --width 800 --height 600 --center --no-buttons --on-top --sticky --fixed --skip-taskbar --listen --tail &"

# import user interfaces
source /usr/lib64/sisyphus/accesoriesui.sh
source /usr/lib64/sisyphus/gamesui.sh
source /usr/lib64/sisyphus/graphicsui.sh
source /usr/lib64/sisyphus/internetui.sh
source /usr/lib64/sisyphus/multimediaui.sh
source /usr/lib64/sisyphus/officeui.sh
source /usr/lib64/sisyphus/systemui.sh

# create main user interface
export local mainui='
<window title="Sisyphus - A simple Epkg GUI" window-position="1" icon-name="gtk-search" modal="true" resizable="false" width-request="800" height-request="600">
<vbox>
<frame Manage packages by name>
	<hbox>
		<text>
			<label>Enter package(s)</label>
		</text>
		<entry>
			<variable>pkgname</variable>
		</entry>
	</hbox>
	<hbox>
		<button tooltip-text="Search for package(s)">
			<label>Search package(s)</label>
			<action>epkg search $pkgname | $showdialog</action>
		</button>
		<button tooltip-text="Install new package(s) (no confirmation)">
			<label>Install package(s)</label>
			<action>epkg autoinstall $pkgname | $showdialog</action>
		</button>
		<button tooltip-text="Uninstall package(s) safely (no confirmation)">
			<label>Remove package(s)</label>
			<action>epkg autoremove $pkgname | $showdialog</action>
		</button>
		<button tooltip-text="Upgrade system (no confirmation)">
			<label>Upgrade System</label>
			<action>epkg autoupgrade | $showdialog</action>
		</button>
		<button tooltip-text="Remove orphan packages(s) aka no longer needed (no confirmation)">
			<label>Remove orphan package(s)</label>
			<action>epkg autoclean | $showdialog</action>
		</button>
	</hbox>
</frame>
<frame Browse packages by category>
	<hbox>
		<button tooltip-text="Accesories">
			<label>Accesories</label>
			<action signal="button-press-event">gtkdialog --space-expand=true --space-fill=true --program=accesoriesui &</action>
			<action signal="button-release-event">EXIT:ok</action>
		</button>
		<button tooltip-text="Games">
			<label>Games</label>
			<action signal="button-press-event">gtkdialog --space-expand=true --space-fill=true --program=gamesui &</action>
			<action signal="button-release-event">EXIT:ok</action>
		</button>
		<button tooltip-text="Graphics">
			<label>Graphics</label>
		</button>
		<button tooltip-text="Internet">
			<label>Internet</label>
		</button>	
	</hbox>
	<hbox>
		<button tooltip-text="Sound & Video">
			<label>Sound & Video</label>
			<action signal="button-press-event">gtkdialog --space-expand=true --space-fill=true --program=multimediaui &</action>
			<action signal="button-release-event">EXIT:ok</action>
		</button>
		<button tooltip-text="Office">
			<label>Office</label>
			<action signal="button-press-event">gtkdialog --space-expand=true --space-fill=true --program=officeui &</action>
			<action signal="button-release-event">EXIT:ok</action>
		</button>
		<button tooltip-text="System Tools">
			<label>System Tools</label>
		</button>
	</hbox>
</frame>
<frame Terminal Emulator>
	<hbox>
		<terminal argv0="/bin/bash">
			<variable>vte1</variable>
			<input>echo epkg</input>
		</terminal>
	</hbox>
</frame>
</vbox>
</window>
'
