#!/usr/bin/env bash

# create games user interface
export local gamesui='
<window title="Sisyphus - A simple Epkg GUI" window-position="1" icon-name="gtk-search" modal="true" resizable="false" width-request="800" height-request="600">
<vbox>
<frame Games>
	<hbox space-expand="true" space-extend="true">
		<table hscrollbar-policy="1" vscrollbar-policy="1" exported-column="1">
			<variable>game</variable>
			<label>Application Category|Application Name|Application Description</label>
			<item>app-emulation|playonlinux|Set of scripts to easily install and use Windows games and software</item>
			<item>app-emulation|steam|Digital distribution client bootstrap package</item>
			<item>games-action|armagetronad|Fast-paced 3D lightcycle game based on Tron</item>
			<item>games-action|chromium-bsu|Chromium B.S.U. - an arcade game</item>
			<item>games-action|supertuxkart|A kart racing game starring Tux, the linux penguin (TuxKart fork)</item>
			<item>games-action|teeworlds|Online multi-player platform 2D shooter</item>
			<item>games-board|aisleriot|A collection of solitaire card games for GNOME</item>
			<item>games-emulation|dosbox|DOS Emulator</item>
			<item>games-emulation|zsnes|SNES (Super Nintendo) emulator that uses x86 assembly</item>
			<item>games-fps|urbanterror|Hollywood tactical shooter based on the ioquake3 engine</item>
			<item>games-fps|xonotic|Fork of Nexuiz, Deathmatch FPS based on DarkPlaces, an advanced Quake 1 engine</item>
			<item>games-simulation|openttd|OpenTTD is a clone of Transport Tycoon Deluxe</item>
			<item>games-strategy|0ad|Cross-platform, 3D and historically-based real-time strategy game</item>
		</table>
	</hbox>
	<hbox space-expand="false" space-extend="false">
		<button space-expand="true" space-extend="true" label-text="install">
			<label>Install package</label>
			<action signal="button-press-event">epkg autoinstall $game|$showdialog</action>
			<action signal="button-release-event">$abortnow</action>
		</button>
		<button space-expand="true" space-extend="true" label-text="uninstall">
			<label>Uninstall package</label>
			<action signal="button-press-event">epkg autoremove $game|$showdialog</action>
			<action signal="button-release-event">$abortnow</action>
		</button>
		<button space-expand="true" space-extend="true" label-text="home">
			<label>Back home</label>
			<action signal="button-press-event">gtkdialog --space-expand=true --space-fill=true --program=mainui &</action>
			<action signal="button-release-event">EXIT:ok</action>
		</button>
		<button space-expand="true" space-extend="true" label-text="exit">
			<label>Exit</label>
			<action>EXIT:ok</action>
		</button>
	</hbox>
</frame>
</vbox>
</window>'
