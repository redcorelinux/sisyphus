SUBDIRS =
DESTDIR = 
UBINDIR ?= /usr/bin
DESKTOPDIR ?= /usr/share/applications
PIXMAPDIR ?= /usr/share/pixmaps
SISYPHUSLIBDIR ?= /usr/lib/sisyphus
SISYPHUSDATADIR ?= /usr/share/sisyphus
POLKITDIR ?= /usr/share/polkit-1/actions

all:
	for d in $(SUBDIRS); do $(MAKE) -C $$d; done

clean:
	for d in $(SUBDIRS); do $(MAKE) -C $$d clean; done

install:
	for d in $(SUBDIRS); do $(MAKE) -C $$d install; done

	install -d $(DESTDIR)$(UBINDIR)
	install -m 0755 sisyphus $(DESTDIR)$(UBINDIR)/
	install -m 0755 sisyphus-pkexec $(DESTDIR)$(UBINDIR)/
	install -d $(DESTDIR)$(SISYPHUSLIBDIR)
	install -m 0755 libsisyphus.sh $(DESTDIR)$(SISYPHUSLIBDIR)/
	install -m 0755 ui/accesoriesui.sh $(DESTDIR)$(SISYPHUSLIBDIR)/
	install -m 0755 ui/gamesui.sh $(DESTDIR)$(SISYPHUSLIBDIR)/
	install -m 0755 ui/graphicsui.sh $(DESTDIR)$(SISYPHUSLIBDIR)/
	install -m 0755 ui/internetui.sh $(DESTDIR)$(SISYPHUSLIBDIR)/
	install -m 0755 ui/multimediaui.sh $(DESTDIR)$(SISYPHUSLIBDIR)/
	install -m 0755 ui/officeui.sh $(DESTDIR)$(SISYPHUSLIBDIR)/
	install -m 0755 ui/systemui.sh $(DESTDIR)$(SISYPHUSLIBDIR)/
	install -d $(DESTDIR)$(SISYPHUSDATADIR)
	install -m 0755 icon/appcleanup.svg $(DESTDIR)$(SISYPHUSDATADIR)/
	install -m 0755 icon/appinstall.svg $(DESTDIR)$(SISYPHUSDATADIR)/
	install -m 0755 icon/appremove.svg $(DESTDIR)$(SISYPHUSDATADIR)/
	install -m 0755 icon/appsearch.svg $(DESTDIR)$(SISYPHUSDATADIR)/
	install -m 0755 icon/appupgrade.svg $(DESTDIR)$(SISYPHUSDATADIR)/
	install -m 0755 icon/caccesories.svg $(DESTDIR)$(SISYPHUSDATADIR)/
	install -m 0755 icon/cgames.svg $(DESTDIR)$(SISYPHUSDATADIR)/
	install -m 0755 icon/cgraphics.svg $(DESTDIR)$(SISYPHUSDATADIR)/
	install -m 0755 icon/cinternet.svg $(DESTDIR)$(SISYPHUSDATADIR)/
	install -m 0755 icon/cmultimedia.svg $(DESTDIR)$(SISYPHUSDATADIR)/
	install -m 0755 icon/coffice.svg $(DESTDIR)$(SISYPHUSDATADIR)/
	install -m 0755 icon/csystem.svg $(DESTDIR)$(SISYPHUSDATADIR)/
	install -d $(DESTDIR)$(DESKTOPDIR)
	install -m 0755 desktop/sisyphus.desktop $(DESTDIR)$(DESKTOPDIR)/
	install -d $(DESTDIR)$(PIXMAPDIR)
	install -m 0644 desktop/sisyphus.png $(DESTDIR)$(PIXMAPDIR)
	install -d $(DESTDIR)$(POLKITDIR)
	install -m 0644 org.redcorelinux.sisyphus.policy $(DESTDIR)$(POLKITDIR)/
