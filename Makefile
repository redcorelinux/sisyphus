SUBDIRS =
DESTDIR = 
UBINDIR ?= /usr/bin
SISYPHUSLIBDIR ?= /usr/lib/sisyphus
SISYPHUSSHAREDIR ?= /usr/share/sisyphus
POLKITDIR ?= /usr/share/polkit-1/actions

all:
	for d in $(SUBDIRS); do $(MAKE) -C $$d; done

clean:
	for d in $(SUBDIRS); do $(MAKE) -C $$d clean; done

install:
	for d in $(SUBDIRS); do $(MAKE) -C $$d install; done

	install -d $(DESTDIR)$(UBINDIR)
	install -m 0755 sisyphus $(DESTDIR)$(UBINDIR)/
	install -d $(DESTDIR)$(SISYPHUSLIBDIR)
	install -m 0755 libsisyphus.sh $(DESTDIR)$(SISYPHUSLIBDIR)/
	install -m 0755 ui/accesoriesui.sh $(DESTDIR)$(SISYPHUSLIBDIR)/
	install -m 0755 ui/gamesui.sh $(DESTDIR)$(SISYPHUSLIBDIR)/
	install -m 0755 ui/graphicsui.sh $(DESTDIR)$(SISYPHUSLIBDIR)/
	install -m 0755 ui/internetui.sh $(DESTDIR)$(SISYPHUSLIBDIR)/
	install -m 0755 ui/multimediaui.sh $(DESTDIR)$(SISYPHUSLIBDIR)/
	install -m 0755 ui/officeui.sh $(DESTDIR)$(SISYPHUSLIBDIR)/
	install -m 0755 ui/systemui.sh $(DESTDIR)$(SISYPHUSLIBDIR)/
	install -d $(DESTDIR)$(SISYPHUSSHAREDIR)
	install -m 0755 icon/accesories.svg $(DESTDIR)$(SISYPHUSSHAREDIR)/
	install -m 0755 icon/games.svg $(DESTDIR)$(SISYPHUSSHAREDIR)/
	install -m 0755 icon/graphics.svg $(DESTDIR)$(SISYPHUSSHAREDIR)/
	install -m 0755 icon/install.svg $(DESTDIR)$(SISYPHUSSHAREDIR)/
	install -m 0755 icon/internet.svg $(DESTDIR)$(SISYPHUSSHAREDIR)/
	install -m 0755 icon/multimedia.svg $(DESTDIR)$(SISYPHUSSHAREDIR)/
	install -m 0755 icon/office.svg $(DESTDIR)$(SISYPHUSSHAREDIR)/
	install -m 0755 icon/purge.svg $(DESTDIR)$(SISYPHUSSHAREDIR)/
	install -m 0755 icon/remove.svg $(DESTDIR)$(SISYPHUSSHAREDIR)/
	install -m 0755 icon/search.svg $(DESTDIR)$(SISYPHUSSHAREDIR)/
	install -m 0755 icon/system.svg $(DESTDIR)$(SISYPHUSSHAREDIR)/
	install -m 0755 icon/upgrade.svg $(DESTDIR)$(SISYPHUSSHAREDIR)/
	install -d $(DESTDIR)$(POLKITDIR)
	install -m 0644 org.redcorelinux.sisyphus.policy $(DESTDIR)$(POLKITDIR)/
