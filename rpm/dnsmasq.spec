%define testrelease 0
%define releasecandidate 0
%if 0%{testrelease}
  %define extrapath test-releases/
  %define extraversion test30
%endif
%if 0%{releasecandidate}
  %define extrapath release-candidates/
  %define extraversion rc5
%endif

%define _hardened_build 1

Name:           dnsmasq
Version:        2.79_test1_calico1
Release:        2%{?extraversion}%{?dist}.2
Summary:        A lightweight DHCP/caching DNS server

Group:          System Environment/Daemons
License:        GPLv2 or GPLv3
URL:            http://www.thekelleys.org.uk/dnsmasq/
Source0:        http://www.thekelleys.org.uk/dnsmasq/%{?extrapath}%{name}-%{version}%{?extraversion}.tar.gz
Source1:        %{name}.service
# upstream git: git://thekelleys.org.uk/dnsmasq.git

Patch8:		dnsmasq-2.76-coverity.patch
Patch9:		dnsmasq-2.76-CVE-2017-14491.patch
Patch10:	dnsmasq-2.76-CVE-2017-14492.patch
Patch11:	dnsmasq-2.76-CVE-2017-14493.patch
Patch12:	dnsmasq-2.76-CVE-2017-14494.patch
Patch13:	dnsmasq-2.76-CVE-2017-14496.patch
Patch14:	dnsmasq-2.76-CVE-2017-14495.patch
# commit a3303e196e5d304ec955c4d63afb923ade66c6e8
Patch15:	dnsmasq-2.76-gita3303e196.patch
Patch16:	dnsmasq-2.76-underflow.patch
Patch17:	dnsmasq-2.76-misc-cleanups.patch
Patch18:	dnsmasq-2.76-CVE-2017-14491-2.patch

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  dbus-devel
BuildRequires:  pkgconfig
BuildRequires:  libidn-devel

BuildRequires:  systemd
Requires(post): systemd systemd-sysv chkconfig
Requires(preun): systemd
Requires(postun): systemd


%description
Dnsmasq is lightweight, easy to configure DNS forwarder and DHCP server.
It is designed to provide DNS and, optionally, DHCP, to a small network.
It can serve the names of local machines which are not in the global
DNS. The DHCP server integrates with the DNS server and allows machines
with DHCP-allocated addresses to appear in the DNS with names configured
either in each host or in a central configuration file. Dnsmasq supports
static and dynamic DHCP leases and BOOTP for network booting of diskless
machines.

%package        utils
Summary:        Utilities for manipulating DHCP server leases
Group:          System Environment/Daemons

%description    utils
Utilities that use the standard DHCP protocol to
query/remove a DHCP server's leases.


%prep
%setup -q -n %{name}-%{version}%{?extraversion}

%patch8 -p1 -b .coverity
%patch9 -p1 -b .CVE-2017-14491
%patch10 -p1 -b .CVE-2017-14492
%patch11 -p1 -b .CVE-2017-14493
%patch12 -p1 -b .CVE-2017-14494
%patch13 -p1 -b .CVE-2017-14496
%patch14 -p1 -b .CVE-2017-14495
%patch15 -p1 -b .gita3303e196
%patch16 -p1 -b .underflow
%patch17 -p1 -b .misc
%patch18 -p1 -b .CVE-2017-14491-2

# use /var/lib/dnsmasq instead of /var/lib/misc
for file in dnsmasq.conf.example man/dnsmasq.8 man/es/dnsmasq.8 src/config.h; do
    sed -i 's|/var/lib/misc/dnsmasq.leases|/var/lib/dnsmasq/dnsmasq.leases|g' "$file"
done

#enable dbus
sed -i 's|/\* #define HAVE_DBUS \*/|#define HAVE_DBUS|g' src/config.h

#enable IDN support
sed -i 's|/\* #define HAVE_IDN \*/|#define HAVE_IDN|g' src/config.h

#enable /etc/dnsmasq.d fix bz 526703, ignore RPM backup files
cat << EOF >> dnsmasq.conf.example

# Include all files in /etc/dnsmasq.d except RPM backup files
conf-dir=/etc/dnsmasq.d,.rpmnew,.rpmsave,.rpmorig
EOF


%build
make %{?_smp_mflags} CFLAGS="$RPM_OPT_FLAGS" LDFLAGS="$RPM_LD_FLAGS"
make -C contrib/lease-tools %{?_smp_mflags} CFLAGS="$RPM_OPT_FLAGS" LDFLAGS="$RPM_LD_FLAGS"


%install
rm -rf $RPM_BUILD_ROOT
# normally i'd do 'make install'...it's a bit messy, though
mkdir -p $RPM_BUILD_ROOT%{_sbindir} \
        $RPM_BUILD_ROOT%{_mandir}/man8 \
        $RPM_BUILD_ROOT%{_var}/lib/dnsmasq \
        $RPM_BUILD_ROOT%{_sysconfdir}/dnsmasq.d \
        $RPM_BUILD_ROOT%{_sysconfdir}/dbus-1/system.d
install src/dnsmasq $RPM_BUILD_ROOT%{_sbindir}/dnsmasq
install dnsmasq.conf.example $RPM_BUILD_ROOT%{_sysconfdir}/dnsmasq.conf
install dbus/dnsmasq.conf $RPM_BUILD_ROOT%{_sysconfdir}/dbus-1/system.d/
install -m 644 man/dnsmasq.8 $RPM_BUILD_ROOT%{_mandir}/man8/

# utils sub package
mkdir -p $RPM_BUILD_ROOT%{_bindir} \
         $RPM_BUILD_ROOT%{_mandir}/man1
install -m 755 contrib/lease-tools/dhcp_release $RPM_BUILD_ROOT%{_bindir}/dhcp_release
install -m 644 contrib/lease-tools/dhcp_release.1 $RPM_BUILD_ROOT%{_mandir}/man1/dhcp_release.1
install -m 755 contrib/lease-tools/dhcp_release6 $RPM_BUILD_ROOT%{_bindir}/dhcp_release6
install -m 644 contrib/lease-tools/dhcp_release6.1 $RPM_BUILD_ROOT%{_mandir}/man1/dhcp_release6.1
install -m 755 contrib/lease-tools/dhcp_lease_time $RPM_BUILD_ROOT%{_bindir}/dhcp_lease_time
install -m 644 contrib/lease-tools/dhcp_lease_time.1 $RPM_BUILD_ROOT%{_mandir}/man1/dhcp_lease_time.1

# Systemd
mkdir -p %{buildroot}%{_unitdir}
install -m644 %{SOURCE1} %{buildroot}%{_unitdir}
rm -rf %{buildroot}%{_initrddir}

%clean
rm -rf $RPM_BUILD_ROOT

%post
%systemd_post dnsmasq.service

%preun
%systemd_preun dnsmasq.service

%postun
%systemd_postun_with_restart dnsmasq.service

%triggerun -- dnsmasq < 2.52-3
%{_bindir}/systemd-sysv-convert --save dnsmasq >/dev/null 2>&1 ||:
/sbin/chkconfig --del dnsmasq >/dev/null 2>&1 || :
/bin/systemctl try-restart dnsmasq.service >/dev/null 2>&1 || :

%files
%defattr(-,root,root,-)
%doc CHANGELOG COPYING COPYING-v3 FAQ doc.html setup.html dbus/DBus-interface
%config(noreplace) %attr(644,root,root) %{_sysconfdir}/dnsmasq.conf
%dir /etc/dnsmasq.d
%dir %{_var}/lib/dnsmasq
%config(noreplace) %attr(644,root,root) %{_sysconfdir}/dbus-1/system.d/dnsmasq.conf
%{_unitdir}/%{name}.service
%{_sbindir}/dnsmasq
%{_mandir}/man8/dnsmasq*

%files utils
%{_bindir}/dhcp_*
%{_mandir}/man1/dhcp_*

%changelog
* Wed Jan 17 2018 Neil Jerram <neil@tigera.io> - 2.79_test1_calico1-2.2
- Test package for arbitrarily long options

* Wed Sep 27 2017 Petr Menšík <pemensik@redhat.com> - 2.76-2.2
- Small correction of CVE-2017-14491

* Tue Sep 26 2017 Petr Menšík <pemensik@redhat.com> - 2.76-2.1
- Fix CVE-2017-14491
- Fix CVE-2017-14492
- Fix CVE-2017-14493
- Fix CVE-2017-14494
- Fix CVE-2017-14496
- Fix CVE-2017-14495
- extra fixes

* Wed Mar 15 2017 Petr Menšík <pemensik@redhat.com> - 2.76-2
- Fix a few coverity warnings
- package is dual-licensed GPL v2 or v3
- don't include /etc/dnsmasq.d in triplicate, ignore RPM backup files instead

* Tue Feb 21 2017 Petr Menšík <pemensik@redhat.com> - 2.76-1
- Rebase to 2.76 (#1375527)
- Include also dhcp_release6 (#1375569)
- Fix compilation warnings
- Correct manual about interface aliases, warn if used without --bind*

* Tue Sep 13 2016 Pavel Šimerda <psimerda@redhat.com> - 2.66-21
- Related: #1367772 - fix dns server update

* Thu Sep 08 2016 Pavel Šimerda <psimerda@redhat.com> - 2.66-20
- Related: #1367772 - additional upstream patch

* Tue Sep 06 2016 Pavel Šimerda <psimerda@redhat.com> - 2.66-19
- Resolves: #1367772 - dns not updated after sleep and resume laptop

* Fri Aug 26 2016 root - 2.66-18
- Resolves: #1358427 - dhcp errors with hostnames beginning with numbers

* Tue May 31 2016 Pavel Šimerda <psimerda@redhat.com> - 2.66-17
- Resolves: #1275626 - modify the patch using new information

* Mon May 30 2016 Pavel Šimerda <psimerda@redhat.com> - 2.66-16
- Resolves: #1275626 - use the patch

* Wed May 25 2016 Pavel Šimerda <psimerda@redhat.com> - 2.66-15
- Resolves: #1275626 - dnsmasq crash with coredump on infiniband network with
  OpenStack

* Thu Jun 25 2015 Pavel Šimerda <psimerda@redhat.com> - 2.66-14
- Resolves: #1232677 - handle IPv4 and IPv6 host entries properly

* Wed Feb 25 2015 Pavel Šimerda <psimerda@redhat.com> - 2.66-13
- Resolves: #1179756 - dnsmasq does not support MAC address based matching for
  IPv6

* Fri Jan 24 2014 Daniel Mach <dmach@redhat.com> - 2.66-12
- Mass rebuild 2014-01-24

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 2.66-11
- Mass rebuild 2013-12-27

* Thu Aug 15 2013 Tomas Hozza <thozza@redhat.com> - 2.66-10
- Use SO_REUSEPORT and SO_REUSEADDR if possible for DHCPv4/6 (#981973)

* Mon Aug 12 2013 Tomas Hozza <thozza@redhat.com> - 2.66-9
- Don't use SO_REUSEPORT on DHCPv4 socket to prevent conflicts with ISC DHCP (#981973)

* Tue Jul 23 2013 Tomas Hozza <thozza@redhat.com> - 2.66-8
- Fix crash when specified empty DHCP option

* Tue Jun 11 2013 Tomas Hozza <thozza@redhat.com> - 2.66-7
- use _hardened_build macro instead of hardcoded flags
- include several fixies from upstream repo:
  - Allow constructed ranges from interface address at end of range
  - Dont BINDTODEVICE DHCP socket if more interfaces may come
  - Fix option parsing for dhcp host
  - Log forwarding table overflows
  - Remove limit in prefix length in auth zone

* Fri May 17 2013 Tomas Hozza <thozza@redhat.com> - 2.66-6
- include several fixies from upstream repo:
  - Tighten hostname checks in legal hostname() function
  - Replace inet_addr() with inet_pton() in src/option.c
  - Use dnsmasq as default DNS server for RA only if it's doing DNS
  - Handle IPv4 interface address labels (aliases) in Linux (#962246)
  - Fix failure to start with ENOTSOCK (#962874)

* Tue Apr 30 2013 Tomas Hozza <thozza@redhat.com> - 2.66-5
- dnsmasq unit file cleanup
  - drop forking Type and PIDfile and rather start dnsmasq with "-k" option
  - drop After syslog.target as this is by default

* Thu Apr 25 2013 Tomas Hozza <thozza@redhat.com> - 2.66-4
- include several fixes from upstream repo:
  - Send TCP DNS messages in one packet
  - Fix crash on SERVFAIL when using --conntrack option
  - Fix regression in dhcp_lease_time utility
  - Man page typos fixes
  - Note that dhcp_lease_time and dhcp_release work only for IPv4
  - Fix for --dhcp-match option to work also with BOOTP protocol

* Sat Apr 20 2013 Tomas Hozza <thozza@redhat.com> - 2.66-3
- Use Full RELRO when linking the daemon
- compile the daemon with PIE
- include two fixes from upstream git repo

* Thu Apr 18 2013 Tomas Hozza <thozza@redhat.com> - 2.66-2
- New stable version dnsmasq-2.66
- Drop of merged patch

* Fri Apr 12 2013 Tomas Hozza <thozza@redhat.com> - 2.66-1.rc5
- Update to latest dnsmasq-2.66rc5
- Include fix for segfault when lease limit is reached

* Fri Mar 22 2013 Tomas Hozza <thozza@redhat.com> - 2.66-1.rc1
- Update to latest dnsmasq-2.66rc1
- Dropping unneeded patches
- Enable IDN support

* Fri Mar 15 2013 Tomas Hozza <thozza@redhat.com> - 2.65-5
- Allocate dhcp_buff-ers also if daemon->ra_contexts to prevent SIGSEGV (#920300)

* Thu Jan 31 2013 Tomas Hozza <thozza@redhat.com> - 2.65-4
- Handle locally-routed DNS Queries (#904940)

* Thu Jan 24 2013 Tomas Hozza <thozza@redhat.com> - 2.65-3
- build dnsmasq with $RPM_OPT_FLAGS, $RPM_LD_FLAGS explicitly (#903362)

* Tue Jan 22 2013 Tomas Hozza <thozza@redhat.com> - 2.65-2
- Fix for CVE-2013-0198 (checking of TCP connection interfaces) (#901555)

* Sat Dec 15 2012 Tomas Hozza <thozza@redhat.com> - 2.65-1
- new version 2.65

* Wed Dec 05 2012 Tomas Hozza <thozza@redhat.com> - 2.64-1
- New version 2.64
- Merged patches dropped

* Tue Nov 20 2012 Tomas Hozza <thozza@redhat.com> - 2.63-4
- Remove EnvironmentFile from service file (#878343)

* Mon Nov 19 2012 Tomas Hozza <thozza@redhat.com> - 2.63-3
- dhcp6 support fixes (#867054)
- removed "-s $HOSTNAME" from .service file (#753656, #822797)

* Tue Oct 23 2012 Tomas Hozza <thozza@redhat.com> - 2.63-2
- Introduce new systemd-rpm macros in dnsmasq spec file (#850096)

* Thu Aug 23 2012 Douglas Schilling Landgraf <dougsland@redhat.com> - 2.63-1
- Use .tar.gz compression, in upstream site there is no .lzma anymore
- New version 2.63

* Sat Feb 11 2012 Pádraig Brady <P@draigBrady.com> - 2.59-5
- Compile DHCP lease management utils with RPM_OPT_FLAGS

* Thu Feb  9 2012 Pádraig Brady <P@draigBrady.com> - 2.59-4
- Include DHCP lease management utils in a subpackage

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.59-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Fri Aug 26 2011 Douglas Schilling Landgraf <dougsland@redhat.com> - 2.59-2
- do not enable service by default

* Fri Aug 26 2011 Douglas Schilling Landgraf <dougsland@redhat.com> - 2.59-1
- New version 2.59
- Fix regression in 2.58 (IPv6 issue) - bz 744814

* Fri Aug 26 2011 Douglas Schilling Landgraf <dougsland@redhat.com> - 2.58-1
- Fixed License
- New version 2.58

* Mon Aug 08 2011 Patrick "Jima" Laughton <jima@fedoraproject.org> - 2.52-5
- Include systemd unit file

* Mon Aug 08 2011 Patrick "Jima" Laughton <jima@fedoraproject.org> - 2.52-3
- Applied Jóhann's patch, minor cleanup

* Tue Jul 26 2011 Jóhann B. Guðmundsson <johannbg@gmail.com> - 2.52-3
- Introduce systemd unit file, drop SysV support

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.52-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Tue Jan 26 2010 Itamar Reis Peixoto <itamar@ispbrasil.com.br> - 2.52-1
- New Version 2.52
- fix condrestart() in initscript bz 547605
- fix sed to enable DBUS(the '*' need some escaping) bz 553161

* Sun Nov 22 2009 Itamar Reis Peixoto <itamar@ispbrasil.com.br> - 2.51-2
- fix bz 512664

* Sat Oct 17 2009 Itamar Reis Peixoto <itamar@ispbrasil.com.br> - 2.51-1
- move initscript from patch to a plain text file
- drop (dnsmasq-configuration.patch) and use sed instead
- enable /etc/dnsmasq.d fix bz 526703
- change requires to package name instead of file
- new version 2.51

* Mon Oct  5 2009 Mark McLoughlin <markmc@redhat.com> - 2.48-4
- Fix multiple TFTP server vulnerabilities (CVE-2009-2957, CVE-2009-2958)

* Wed Aug 12 2009 Ville Skyttä <ville.skytta@iki.fi> - 2.48-3
- Use lzma compressed upstream tarball.

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.48-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Jun 10 2009 Patrick "Jima" Laughton <jima@beer.tclug.org> 2.48-1
- Bugfix/feature enhancement update
- Fixing BZ#494094

* Fri May 29 2009 Patrick "Jima" Laughton <jima@beer.tclug.org> 2.47-1
- Bugfix/feature enhancement update

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.46-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Mon Dec 29 2008 Matěj Cepl <mcepl@redhat.com> - 2.45-2
- rebuilt

* Mon Jul 21 2008 Patrick "Jima" Laughton <jima@beer.tclug.org> 2.45-1
- Upstream release (bugfixes)

* Wed Jul 16 2008 Patrick "Jima" Laughton <jima@beer.tclug.org> 2.43-2
- New upstream release, contains fixes for CVE-2008-1447/CERT VU#800113
- Dropped patch for newer glibc (merged upstream)

* Wed Feb 13 2008 Patrick "Jima" Laughton <jima@beer.tclug.org> 2.41-0.8
- Added upstream-authored patch for newer glibc (thanks Simon!)

* Wed Feb 13 2008 Patrick "Jima" Laughton <jima@beer.tclug.org> 2.41-0.7
- New upstream release

* Wed Jan 30 2008 Patrick "Jima" Laughton <jima@beer.tclug.org> 2.41-0.6.rc1
- Release candidate
- Happy Birthday Isaac!

* Wed Jan 23 2008 Patrick "Jima" Laughton <jima@beer.tclug.org> 2.41-0.5.test30
- Bugfix update

* Mon Dec 31 2007 Patrick "Jima" Laughton <jima@beer.tclug.org> 2.41-0.4.test26
- Bugfix/feature enhancement update

* Thu Dec 13 2007 Patrick "Jima" Laughton <jima@beer.tclug.org> 2.41-0.3.test24
- Upstream fix for fairly serious regression

* Tue Dec 04 2007 Patrick "Jima" Laughton <jima@beer.tclug.org> 2.41-0.2.test20
- New upstream test release
- Moving dnsmasq.leases to /var/lib/dnsmasq/ as per BZ#407901
- Ignoring dangerous-command-in-%%post rpmlint warning (as per above fix)
- Patch consolidation/cleanup
- Removed conditionals for Fedora <= 3 and Aurora 2.0

* Tue Sep 18 2007 Patrick "Jima" Laughton <jima@beer.tclug.org> 2.40-1
- Finalized upstream release
- Removing URLs from patch lines (CVS is the authoritative source)
- Added more magic to make spinning rc/test packages more seamless

* Sun Aug 26 2007 Patrick "Jima" Laughton <jima@beer.tclug.org> 2.40-0.1.rc2
- New upstream release candidate (feature-frozen), thanks Simon!
- License clarification

* Tue May 29 2007 Patrick "Jima" Laughton <jima@beer.tclug.org> 2.39-1
- New upstream version (bugfixes, enhancements)

* Mon Feb 12 2007 Patrick "Jima" Laughton <jima@beer.tclug.org> 2.38-1
- New upstream version with bugfix for potential hang

* Tue Feb 06 2007 Patrick "Jima" Laughton <jima@beer.tclug.org> 2.37-1
- New upstream version

* Wed Jan 24 2007 Patrick "Jima" Laughton <jima@beer.tclug.org> 2.36-1
- New upstream version

* Mon Nov 06 2006 Patrick "Jima" Laughton <jima@beer.tclug.org> 2.35-2
- Stop creating /etc/sysconfig on %%install
- Create /etc/dnsmasq.d on %%install

* Mon Nov 06 2006 Patrick "Jima" Laughton <jima@beer.tclug.org> 2.35-1
- Update to 2.35
- Removed UPGRADING_to_2.0 from %%doc as per upstream change
- Enabled conf-dir in default config as per RFE BZ#214220 (thanks Chris!)
- Added %%dir /etc/dnsmasq.d to %%files as per above RFE

* Tue Oct 24 2006 Patrick "Jima" Laughton <jima@beer.tclug.org> 2.34-2
- Fixed BZ#212005
- Moved %%postun scriptlet to %%post, where it made more sense
- Render scriptlets safer
- Minor cleanup for consistency

* Thu Oct 19 2006 Patrick "Jima" Laughton <jima@beer.tclug.org> 2.34-1
- Hardcoded version in patches, as I'm getting tired of updating them
- Update to 2.34

* Mon Aug 28 2006 Patrick "Jima" Laughton <jima@beer.tclug.org> 2.33-2
- Rebuild for FC6

* Tue Aug 15 2006 Patrick "Jima" Laughton <jima@beer.tclug.org> 2.33-1
- Update

* Sat Jul 22 2006 Patrick "Jima" Laughton <jima@beer.tclug.org> 2.32-3
- Added pkgconfig BuildReq due to reduced buildroot

* Thu Jul 20 2006 Patrick "Jima" Laughton <jima@beer.tclug.org> 2.32-2
- Forced update due to dbus version bump

* Mon Jun 12 2006 Patrick "Jima" Laughton <jima@beer.tclug.org> 2.32-1
- Update from upstream
- Patch from Dennis Gilmore fixed the conditionals to detect Aurora Linux

* Mon May  8 2006 Patrick "Jima" Laughton <jima@auroralinux.org> 2.31-1
- Removed dbus config patch (now provided upstream)
- Patched in init script (no longer provided upstream)
- Added DBus-interface to docs

* Tue May  2 2006 Patrick "Jima" Laughton <jima@auroralinux.org> 2.30-4.2
- More upstream-recommended cleanups :)
- Killed sysconfig file (provides unneeded functionality)
- Tweaked init script a little more

* Tue May  2 2006 Patrick "Jima" Laughton <jima@auroralinux.org> 2.30-4
- Moved options out of init script and into /etc/sysconfig/dnsmasq
- Disabled DHCP_LEASE in sysconfig file, fixing bug #190379
- Simon Kelley provided dbus/dnsmasq.conf, soon to be part of the tarball

* Thu Apr 27 2006 Patrick "Jima" Laughton <jima@auroralinux.org> 2.30-3
- Un-enabled HAVE_ISC_READER, a hack to enable a deprecated feature (request)
- Split initscript & enable-dbus patches, conditionalized dbus for FC3
- Tweaked name field in changelog entries (trying to be consistent)

* Mon Apr 24 2006 Patrick "Jima" Laughton <jima@auroralinux.org> 2.30-2
- Disabled stripping of binary while installing (oops)
- Enabled HAVE_ISC_READER/HAVE_DBUS via patch
- Added BuildReq for dbus-devel

* Mon Apr 24 2006 Patrick "Jima" Laughton <jima@auroralinux.org> 2.30-1
- Initial Fedora Extras RPM
