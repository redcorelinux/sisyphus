#!/usr/bin/env bash

# create internet user interface
export local internetui='
<window title="Sisyphus - A simple Epkg GUI" window-position="1" icon-name="gtk-search" modal="true" resizable="false" width-request="800" height-request="600">
<vbox>
<frame Internet>
	<hbox space-expand="true" space-extend="true">
		<table hscrollbar-policy="1" vscrollbar-policy="1" exported-column="1">
			<variable>internet</variable>
			<label>Application Category|Application Name|Application Description</label>
			<item>net-analyzer|netcat6|netcat clone with better IPv6 support, improved code, etc...</item>
			<item>net-analyzer|nmap|A utility for network discovery and security auditing</item>
			<item>net-dns|avahi|System which facilitates service discovery on a local network</item>
			<item>net-firewall|firewalld|A firewall daemon with D-BUS interface providing a dynamic firewall</item>
			<item>net-firewall|ufw|A program used to manage a netfilter firewall</item>
			<item>net-firewall|ufw-frontends|Provides graphical frontend to ufw</item>
			<item>net-fs|samba|Samba Suite Version 4</item>
			<item>net-fs|sshfs|Fuse-filesystem utilizing the sftp service</item>
			<item>net-ftp|filezilla|FTP client with lots of useful features and an intuitive interface</item>
			<item>net-im|pidgin|GTK Instant Messenger client</item>
			<item>net-im|skypeforlinux|P2P Internet Telephony (VoiceIP) client</item>
			<item>net-im|telegram|Unofficial telegram protocol client</item>
			<item>net-im|viber|Free calls, text and picture sharing with anyone, anywhere!</item>
			<item>net-irc|hexchat|Graphical IRC client based on XChat</item>
			<item>net-irc|konversation|A user friendly IRC Client</item>
			<item>net-irc|quassel|Qt/KDE IRC client supporting a remote daemon for 24/7 connectivity</item>
			<item>net-misc|cmst|Qt GUI for Connman with system tray icon</item>
			<item>net-misc|dropbox|Dropbox daemon (pretends to be GUI-less)</item>
			<item>net-misc|lxqt-connman-applet|LXQt system-tray applet for ConnMan</item>
			<item>net-misc|modem-manager-gui|Frontend for ModemManager daemon able to control specific modem functions</item>
			<item>net-misc|teamviewer|All-In-One Solution for Remote Access and Support over the Internet</item>
			<item>net-misc|tigervnc|Remote desktop viewer display system</item>
			<item>net-misc|youtube-dl|Download videos from YouTube.com (and more sites...)</item>
			<item>net-news|liferea|News Aggregator for RDF/RSS/CDF/Atom/Echo feeds</item>
			<item>net-p2p|deluge|BitTorrent client with a client/server model</item>
			<item>net-p2p|qbittorrent|BitTorrent client in C++ and Qt</item>
			<item>net-p2p|transmission|A Fast, Easy and Free BitTorrent client</item>
			<item>net-print|cnijfilter|Canon InkJet Printer Driver for Linux (Pixus/Pixma-Series)</item>
			<item>net-print|cnijfilter-drivers|Canon InkJet Printer Driver for Linux (Pixus/Pixma-Series)</item>
			<item>net-print|cups|The Common Unix Printing System</item>
			<item>net-print|cups-filters|Cups PDF filters</item>
			<item>net-print|hplip|HP Linux Imaging and Printing - Print, scan, fax drivers and service tools</item>
			<item>net-wireless|aircrack-ng|WLAN tools for breaking 802.11 WEP/WPA keys</item>
			<item>net-wireless|b43-fwcutter|Firmware Tool for Broadcom 43xx based wireless network devices using the mac80211 wireless stack</item>
			<item>net-wireless|bluez|Bluetooth Tools and System Daemons for Linux</item>
			<item>net-wireless|broadcom-sta|Broadcoms IEEE 802.11a/b/g/n hybrid Linux device driver</item>
			<item>net-wireless|wavemon|Ncurses based monitor for IEEE 802.11 wireless LAN cards</item>
			<item>www-client|firefox|Firefox Web Browser</item>
			<item>www-client|google-chrome|The web browser from Google</item>
			<item>www-client|opera|A fast and secure web browser</item>
			<item>www-client|qupzilla|A cross-platform web browser using QtWebEngine</item>
			<item>www-client|vivaldi|A new browser for our friends</item>
			<item>www-misc|profile-sync-daemon|Symlinks and syncs browser profile dirs to RAM</item>
			<item>www-plugins|adobe-flash|Adobe Flash Player</item>
			<item>www-plugins|chrome-binary-plugins|Binary plugins from Google Chrome for use in Chromium</item>
			<item>www-plugins|freshplayerplugin|PPAPI-host NPAPI-plugin adapter for flashplayer in npapi based browsers</item>
			<item>www-plugins|google-talkplugin|Video chat browser plug-in for Google Talk</item>
		</table>
	</hbox>
	<hbox space-expand="false" space-extend="false">
		<button space-expand="true" space-extend="true" label-text="install">
			<label>Install package</label>
			<action>epkg autoinstall $internet|$sisyphusprogress</action>
		</button>
		<button space-expand="true" space-extend="true" label-text="uninstall">
			<label>Uninstall package</label>
			<action>epkg autoremove $internet|$sisyphusprogress</action>
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
