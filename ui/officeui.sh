#!/usr/bin/env bash

# create office user interface
export local officeui='
<window title="Sisyphus - A simple Epkg GUI" window-position="1" icon-name="gtk-search" modal="true" resizable="false" width-request="800" height-request="600">
<vbox>
<frame Office>
	<hbox space-expand="true" space-extend="true">
		<table hscrollbar-policy="1" vscrollbar-policy="1" exported-column="1">
			<variable>office</variable>
			<label>Application Category|Application Name|Application Description</label>
			<item>app-office|abiword|Fully featured yet light and fast cross platform word processor documentation</item>
			<item>app-office|fet|Opensource school/high-school/university timetable scheduling software</item>
			<item>app-office|gnucash|A personal finance manager</item>
			<item>app-office|libreoffice|A full office productivity suite</item>
			<item>app-office|wps-office|WPS Office is an office productivity suite</item>
			<item>app-text|qpdfview|A tabbed document viewer</item>
		</table>
	</hbox>
	<hbox space-expand="false" space-extend="false">
		<button space-expand="true" space-extend="true" label-text="install">
			<label>Install package</label>
			<action signal="button-press-event">epkg autoinstall $office|$showdialog</action>
			<action signal="button-release-event">$abortnow</action>
		</button>
		<button space-expand="true" space-extend="true" label-text="uninstall">
			<label>Uninstall package</label>
			<action signal="button-press-event">epkg autoremove $office|$showdialog</action>
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
