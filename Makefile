SUBDIRS =
DESTDIR = 
UBINDIR ?= /usr/bin
DESKTOPDIR ?= /usr/share/applications
PIXMAPDIR ?= /usr/share/pixmaps
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
	install -d $(DESTDIR)$(SISYPHUSDATADIR)
	install -d $(DESTDIR)$(SISYPHUSDATADIR)/icon
	install -d $(DESTDIR)$(SISYPHUSDATADIR)/ui
	install -m 0755 *.py $(DESTDIR)$(SISYPHUSDATADIR)/
	install -m 0755 icon/* $(DESTDIR)$(SISYPHUSDATADIR)/icon/
	install -m 0755 ui/* $(DESTDIR)$(SISYPHUSDATADIR)/ui/
	install -d $(DESTDIR)$(DESKTOPDIR)
	install -m 0755 desktop/sisyphus.desktop $(DESTDIR)$(DESKTOPDIR)/
	install -d $(DESTDIR)$(PIXMAPDIR)
	install -m 0644 desktop/sisyphus.png $(DESTDIR)$(PIXMAPDIR)
	install -d $(DESTDIR)$(POLKITDIR)
	install -m 0644 org.redcorelinux.sisyphus.policy $(DESTDIR)$(POLKITDIR)/

uninstall:
	rm -rf $(DESTDIR)$(UBINDIR)/sisyphus
	rm -rf $(DESTDIR)$(UBINDIR)/sisyphus-pkexec
	rm -rf $(DESTDIR)$(DESKTOPDIR)/sisyphus.desktop
	rm -rf $(DESTDIR)$(PIXMAPDIR)/sisyphus.png
	rm -rf $(DESTDIR)$(POLKITDIR)/org.redcorelinux.sisyphus.policy
	rm -rf $(DESTDIR)$(SISYPHUSDATADIR)
