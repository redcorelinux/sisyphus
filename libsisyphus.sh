#!/usr/bin/env bash

# export xterm flags
export local showprogress="xterm -maximized -e"
export local showresults="xterm -maximized -hold -e"

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
<frame>
	<hbox space-expand="false" space-extend="false">
		<text space-expand="true" space-extend="true">
			<label>MANAGE PACKAGES</label>
		</text>
	</hbox>
	<hbox space-expand="false" space-extend="false">
		<entry space-expand="true" space-extend="true">
			<default>Enter package(s)</default>
			<variable>pkgname</variable>
		</entry>
	</hbox>
	<hbox space-expand="false" space-extend="false">
		<button space-expand="true" space-extend="true" tooltip-text="Search package(s)">
			<input file>/usr/share/sisyphus/search.svg</input>
			<action>$showresults epkg search $pkgname</action>
		</button>
		<button space-expand="true" space-extend="true" tooltip-text="Install package(s)">
			<input file>/usr/share/sisyphus/install.svg</input>
			<action>$showprogress epkg autoinstall $pkgname</action>
		</button>
		<button space-expand="true" space-extend="true" tooltip-text="Uninstall package(s)">
			<input file>/usr/share/sisyphus/remove.svg</input>
			<action>$showprogress epkg autoremove $pkgname</action>
		</button>
		<button space-expand="true" space-extend="true" tooltip-text="Upgrade system">
			<input file>/usr/share/sisyphus/upgrade.svg</input>
			<action>$showprogress epkg autoupgrade</action>
		</button>
		<button space-expand="true" space-extend="true" tooltip-text="Remove orphan packages(s) aka no longer needed">
			<input file>/usr/share/sisyphus/purge.svg</input>
			<action>$showprogress epkg autoclean</action>
		</button>
	</hbox>
	<hseparator space-expand="true" space-extend="true"></hseparator>
	<hbox space-expand="false" space-extend="false">
		<text space-expand="true" space-extend="true">
			<label>BROWSE PACKAGES</label>
		</text>
	</hbox>
	<hbox space-expand="true" space-extend="true">
		<button tooltip-text="Accesories">
			<input file>/usr/share/sisyphus/accesories.svg</input>
			<action signal="button-press-event">gtkdialog --space-expand=true --space-fill=true --program=accesoriesui &</action>
			<action signal="button-release-event">EXIT:ok</action>
		</button>
		<button tooltip-text="Games">
			<input file>/usr/share/sisyphus/games.svg</input>
			<action signal="button-press-event">gtkdialog --space-expand=true --space-fill=true --program=gamesui &</action>
			<action signal="button-release-event">EXIT:ok</action>
		</button>
		<button tooltip-text="Graphics">
			<input file>/usr/share/sisyphus/graphics.svg</input>
			<action signal="button-press-event">gtkdialog --space-expand=true --space-fill=true --program=graphicsui &</action>
			<action signal="button-release-event">EXIT:ok</action>
		</button>
		<button tooltip-text="Internet">
			<input file>/usr/share/sisyphus/internet.svg</input>
			<action signal="button-press-event">gtkdialog --space-expand=true --space-fill=true --program=internetui &</action>
			<action signal="button-release-event">EXIT:ok</action>
		</button>	
	</hbox>
	<hbox space-expand="true" space-extend="true">
		<button tooltip-text="Sound & Video">
			<input file>/usr/share/sisyphus/multimedia.svg</input>
			<action signal="button-press-event">gtkdialog --space-expand=true --space-fill=true --program=multimediaui &</action>
			<action signal="button-release-event">EXIT:ok</action>
		</button>
		<button tooltip-text="Office">
			<input file>/usr/share/sisyphus/office.svg</input>
			<action signal="button-press-event">gtkdialog --space-expand=true --space-fill=true --program=officeui &</action>
			<action signal="button-release-event">EXIT:ok</action>
		</button>
		<button tooltip-text="System Tools">
			<input file>/usr/share/sisyphus/system.svg</input>
			<action signal="button-press-event">gtkdialog --space-expand=true --space-fill=true --program=systemui &</action>
			<action signal="button-release-event">EXIT:ok</action>
		</button>
	</hbox>
</frame>
</vbox>
</window>
'
