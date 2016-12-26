#!/usr/bin/env bash

# create multimedia user interface
export local multimediaui='
<window title="Sisyphus - A simple Epkg GUI" window-position="1" icon-name="gtk-search" modal="true" resizable="false" width-request="800" height-request="600">
<vbox>
<frame Multimedia>
	<hbox space-expand="true" space-extend="true">
		<table hscrollbar-policy="1" vscrollbar-policy="1" exported-column="1">
			<variable>multimedia</variable>
			<label>Application Category|Application Name|Application Description</label>
			<item>app-cdr|bashburn|A shell script for burning optical media</item>
			<item>app-cdr|bchunk|Converts bin/cue CD-images to iso+wav/cdr</item>
			<item>app-cdr|bin2iso|converts RAW format (.bin|.cue) files to ISO/WAV format</item>
			<item>app-cdr|brasero|CD/DVD burning application for the GNOME desktop</item>
			<item>app-cdr|cdrdao|Burn CDs in disk-at-once mode -- with optional GUI frontend</item>
			<item>app-cdr|cdrtools|A set of tools for CD|DVD reading and recording, including cdrecord</item>
			<item>app-cdr|dvd+rw-tools|A set of tools for DVD+RW|-RW drives</item>
			<item>app-cdr|nrg2iso|Converts Nero nrg CD-images to iso</item>
			<item>media-plugins|qmmp-plugin-pack|A set of extra plugins for Qmmp</item>
			<item>media-sound|audacity|Free crossplatform audio editor</item>
			<item>media-sound|deadbeef|foobar2k-like music player</item>
			<item>media-sound|pavucontrol|Pulseaudio Volume Control, GTK based mixer for Pulseaudio</item>
			<item>media-sound|pavucontrol-qt|Qt port of pavucontrol</item>
			<item>media-sound|qmmp|Qt5-based audio player with winamp/xmms skins support</item>
			<item>media-sound|spotify|Spotify is a social music platform</item>
			<item>media-sound|volumeicon|A lightweight volume control that sits in your systray</item>
			<item>media-tv|sopcast|SopCast free P2P Internet TV binary</item>
			<item>media-tv|tv-maxe|Program to view free channels</item>
			<item>media-tv|v4l-utils|Separate utilities ebuild from upstream v4l-utils package</item>
			<item>media-video|baka-mplayer|Cross-platform libmpv-based multimedia player with uncluttered design</item>
			<item>media-video|ffmulticonverter|FF Multi Converter is a simple graphical converter application for audio, video, image and document</item>
			<item>media-video|gtk-recordmydesktop|GTK+ interface for RecordMyDesktop</item>
			<item>media-video|guvcview|GTK+ UVC Webcam Viewer</item>
			<item>media-video|handbrake|Open-source, GPL-licensed, multiplatform, multithreaded video transcoder</item>
			<item>media-video|mpv|Media player based on MPlayer and mplayer2</item>
			<item>media-video|obs-studio|Software for Recording and Streaming Live Video Content</item>
			<item>media-video|simplescreenrecorder|A Simple Screen Recorder</item>
			<item>media-video|smplayer|Great Qt GUI front-end for mplayer/mpv</item>
			<item>media-video|smtube|YouTube Browser for SMPlayer</item>
			<item>media-video|vlc|VLC media player - Video player and streamer</item>
		</table>
	</hbox>
	<hbox space-expand="false" space-extend="false">
		<button space-expand="true" space-extend="true" label-text="install">
			<label>Install package</label>
			<action>epkg autoinstall $multimedia|$sisyphusprogress</action>
		</button>
		<button space-expand="true" space-extend="true" label-text="uninstall">
			<label>Uninstall package</label>
			<action>epkg autoremove $multimedia|$sisyphusprogress</action>
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
