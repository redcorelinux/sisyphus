#!/usr/bin/env bash

# export dialog && abort flags
export local sisyphusprogress="yad --title "sisyphus" --progress --pulsate --width 400 --center --no-buttons --on-top --no-escape --sticky --fixed --undecorated --skip-taskbar  --auto-close &"
export local sisyphustextinfo="yad --title "sisyphus" --text-info --width 800 --height 600 --center --no-buttons --on-top --sticky --fixed --skip-taskbar --listen --tail &"

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
			<input file>/usr/share/sisyphus/appsearch.svg</input>
			<action>epkg search $pkgname|$sisyphustextinfo</action>
		</button>
		<button space-expand="true" space-extend="true" tooltip-text="Install package(s)">
			<input file>/usr/share/sisyphus/appinstall.svg</input>
			<action>epkg autoinstall $pkgname|$sisyphusprogress</action>
		</button>
		<button space-expand="true" space-extend="true" tooltip-text="Uninstall package(s)">
			<input file>/usr/share/sisyphus/appremove.svg</input>
			<action>epkg autoremove $pkgname|$sisyphusprogress</action>
		</button>
		<button space-expand="true" space-extend="true" tooltip-text="Upgrade system">
			<input file>/usr/share/sisyphus/appupgrade.svg</input>
			<action>epkg autoupgrade|$sisyphusprogress</action>
		</button>
		<button space-expand="true" space-extend="true" tooltip-text="Remove orphan packages(s) aka no longer needed">
			<input file>/usr/share/sisyphus/appcleanup.svg</input>
			<action>epkg autoclean|$sisyphusprogress</action>
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
			<input file>/usr/share/sisyphus/caccesories.svg</input>
			<action signal="button-press-event">gtkdialog --space-expand=true --space-fill=true --program=accesoriesui &</action>
			<action signal="button-release-event">EXIT:ok</action>
		</button>
		<button tooltip-text="Games">
			<input file>/usr/share/sisyphus/cgames.svg</input>
			<action signal="button-press-event">gtkdialog --space-expand=true --space-fill=true --program=gamesui &</action>
			<action signal="button-release-event">EXIT:ok</action>
		</button>
		<button tooltip-text="Graphics">
			<input file>/usr/share/sisyphus/cgraphics.svg</input>
			<action signal="button-press-event">gtkdialog --space-expand=true --space-fill=true --program=graphicsui &</action>
			<action signal="button-release-event">EXIT:ok</action>
		</button>
		<button tooltip-text="Internet">
			<input file>/usr/share/sisyphus/cinternet.svg</input>
			<action signal="button-press-event">gtkdialog --space-expand=true --space-fill=true --program=internetui &</action>
			<action signal="button-release-event">EXIT:ok</action>
		</button>	
	</hbox>
	<hbox space-expand="true" space-extend="true">
		<button tooltip-text="Sound & Video">
			<input file>/usr/share/sisyphus/cmultimedia.svg</input>
			<action signal="button-press-event">gtkdialog --space-expand=true --space-fill=true --program=multimediaui &</action>
			<action signal="button-release-event">EXIT:ok</action>
		</button>
		<button tooltip-text="Office">
			<input file>/usr/share/sisyphus/coffice.svg</input>
			<action signal="button-press-event">gtkdialog --space-expand=true --space-fill=true --program=officeui &</action>
			<action signal="button-release-event">EXIT:ok</action>
		</button>
		<button tooltip-text="System Tools">
			<input file>/usr/share/sisyphus/csystem.svg</input>
			<action signal="button-press-event">gtkdialog --space-expand=true --space-fill=true --program=systemui &</action>
			<action signal="button-release-event">EXIT:ok</action>
		</button>
	</hbox>
</frame>
</vbox>
</window>
'
