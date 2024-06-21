##  Makefile.am -- an automake template for Makefile.in file



bin_PROGRAMS = scanimage

if COMPILE_SANED
sbin_PROGRAMS = saned
else
EXTRA_PROGRAMS += saned
endif

AM_CPPFLAGS = -I. -I$(srcdir) -I$(top_builddir)/include -I$(top_srcdir)/include

scanimage_SOURCES = scanimage.c stiff.c stiff.h
scanimage_LDADD = ../backend/libsane.la ../sanei/libsanei.la ../lib/liblib.la \
             ../lib/libfelib.la

saned_SOURCES = saned.c
saned_LDADD = ../backend/libsane.la ../sanei/libsanei.la ../lib/liblib.la \
             ../lib/libfelib.la @SYSLOG_LIBS@ @SYSTEMD_LIBS@


