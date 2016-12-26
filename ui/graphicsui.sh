#!/usr/bin/env bash

# create graphics user interface
export local graphicsui='
<window title="Sisyphus - A simple Epkg GUI" window-position="1" icon-name="gtk-search" modal="true" resizable="false" width-request="800" height-request="600">
<vbox>
<frame Graphics>
	<hbox space-expand="true" space-extend="true">
		<tree hscrollbar-policy="1" vscrollbar-policy="1" exported-column="1" selection-mode="3">
			<variable>graphics</variable>
			<label>Application Category|Application Name|Application Description</label>
			<item>media-fonts|cantarell|Default fontset for GNOME Shell</item>
			<item>media-fonts|corefonts|Microsofts TrueType core fonts</item>
			<item>media-fonts|dejavu|DejaVu fonts, bitstream vera with ISO-8859-2 characters</item>
			<item>media-fonts|inconsolata|A beautiful sans-serif monotype font designed for code listings</item>
			<item>media-fonts|liberation-fonts|A Helvetica/Times/Courier replacement TrueType font set, courtesy of Red Hat</item>
			<item>media-fonts|libertine|Fonts from the Linux Libertine Open Fonts Project</item>
			<item>media-fonts|noto|Googles font family that aims to support all the worlds languages</item>
			<item>media-fonts|ttf-bitstream-vera|Bitstream Vera font family</item>
			<item>media-fonts|urw-fonts|free good quality fonts gpl-ed by URW++</item>
			<item>media-gfx|blender|3D Creation/Animation/Publishing System</item>
			<item>media-gfx|darktable|A virtual lighttable and darkroom for photographers</item>
			<item>media-gfx|eom|The MATE image viewer</item>
			<item>media-gfx|gimp|GNU Image Manipulation Program</item>
			<item>media-gfx|gpicview|A Simple and Fast Image Viewer for X</item>
			<item>media-gfx|inkscape|A SVG based generic vector-drawing program</item>
			<item>media-gfx|lximage-qt|LXImage Image Viewer - GPicView replacement</item>
			<item>media-gfx|rawtherapee|A powerful cross-platform raw image processing program</item>
			<item>media-gfx|simple-scan|Simple document scanning utility</item>
			<item>media-gfx|xsane|graphical scanning frontend</item>
		</tree>
	</hbox>
	<hbox space-expand="false" space-extend="false">
		<button space-expand="true" space-extend="true" tooltip-text="Install package(s)">
			<label>Install package(s)</label>
			<action>epkg autoinstall $graphics|$sisyphusprogress &</action>
		</button>
		<button space-expand="true" space-extend="true" tooltip-text="Uninstall package(s)">
			<label>Uninstall package(s)</label>
			<action>epkg autoremove $graphics|$sisyphusprogress &</action>
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
