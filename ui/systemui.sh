#!/usr/bin/env bash

# create system user interface
export local systemui='
<window title="Sisyphus - A simple Epkg GUI" window-position="1" icon-name="gtk-search" modal="true" resizable="false" width-request="800" height-request="600">
<vbox>
<frame System>
	<hbox space-expand="true" space-extend="true">
		<tree hscrollbar-policy="1" vscrollbar-policy="1" exported-column="1" selection-mode="3">
			<variable>system</variable>
			<label>Application Category|Application Name|Application Description</label>
			<item>sys-boot|unetbootin-static|Universal Netboot Installer creates Live USB systems for various OS distributions</item>
		</tree>
	</hbox>
	<hbox space-expand="false" space-extend="false">
		<button space-expand="true" space-extend="true" tooltip-text="Install package(s)">
			<label>Install package(s)</label>
			<action>epkg autoinstall $system|$sisyphusprogress &</action>
		</button>
		<button space-expand="true" space-extend="true" label-text="Uninstall package(s)">
			<label>Uninstall package(s)</label>
			<action>epkg autoremove $system|$sisyphusprogress &</action>
		</button>
		<button space-expand="true" space-extend="true" tooltip-text="Clean orphan package(s)">
			<label>Clean orphan package(s)</label>
			<action>epkg autoclean|$sisyphusprogress &</action>
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
