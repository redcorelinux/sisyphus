#!/usr/bin/env bash

# create accesories user interface
export local accesoriesui='
<window title="Sisyphus - A simple Epkg GUI" window-position="1" icon-name="gtk-search" modal="true" resizable="false" width-request="800" height-request="600">
<vbox>
<frame Accesories>
	<hbox space-expand="true" space-extend="true">
		<tree hscrollbar-policy="1" vscrollbar-policy="1" exported-column="1" selection-mode="3">
			<variable>accesories</variable>
			<label>Application Category|Application Name|Application Description</label>
			<item>app-admin|keepassx|Qt password manager compatible with its Win32 and Pocket PC versions</item>
		</tree>
	</hbox>
	<hbox space-expand="false" space-extend="false">
		<button space-expand="true" space-extend="true" label-text="install">
			<label>Install package</label>
			<action>epkg autoinstall $accesories|$sisyphusprogress &</action>
		</button>
		<button space-expand="true" space-extend="true" label-text="uninstall">
			<label>Uninstall package</label>
			<action>epkg autoremove $accesories|$sisyphusprogress &</action>
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
