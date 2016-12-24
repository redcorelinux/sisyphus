SUBDIRS =
DESTDIR = 
UBINDIR ?= /usr/bin
LIBSISYPHUSDIR ?= /usr/lib/sisyphus
POLKITDIR ?= /usr/share/polkit-1/actions

all:
	for d in $(SUBDIRS); do $(MAKE) -C $$d; done

clean:
	for d in $(SUBDIRS); do $(MAKE) -C $$d clean; done

install:
	for d in $(SUBDIRS); do $(MAKE) -C $$d install; done

	install -d $(DESTDIR)$(UBINDIR)
	install -m 0755 sisyphus $(DESTDIR)$(UBINDIR)/
	install -d $(DESTDIR)$(LIBSISYPHUSDIR)
	install -m 0755 libsisyphus.sh $(DESTDIR)$(LIBSISYPHUSDIR)/
	install -m 0755 accesoriesui.sh $(DESTDIR)$(LIBSISYPHUSDIR)/
	install -m 0755 gamesui.sh $(DESTDIR)$(LIBSISYPHUSDIR)/
	install -m 0755 graphicsui.sh $(DESTDIR)$(LIBSISYPHUSDIR)/
	install -m 0755 internetui.sh $(DESTDIR)$(LIBSISYPHUSDIR)/
	install -m 0755 multimediaui.sh $(DESTDIR)$(LIBSISYPHUSDIR)/
	install -m 0755 officeui.sh $(DESTDIR)$(LIBSISYPHUSDIR)/
	install -m 0755 systemui.sh $(DESTDIR)$(LIBSISYPHUSDIR)/
	install -d $(DESTDIR)$(POLKITDIR)
	install -m 0644 org.redcorelinux.sisyphus.policy $(DESTDIR)$(POLKITDIR)/
