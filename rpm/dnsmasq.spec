%define testrelease 0
%define releasecandidate 0
%if 0%{testrelease}
  %define extrapath test-releases/
  %define extraversion test30
%endif
%if 0%{releasecandidate}
  %define extrapath release-candidates/
  %define extraversion rc1
%endif

Name:           dnsmasq
Version:        2.72_calico0.24
Release:        1%{?extraversion}%{?dist}
Summary:        A lightweight DHCP/caching DNS server

Group:          System Environment/Daemons
License:        GPLv2 or GPLv3
URL:            http://www.thekelleys.org.uk/dnsmasq/
Source0:        dnsmasq-%{version}.tar.gz
Patch0:         %{name}-2.33-initscript.patch
Patch1:         %{name}-configuration.patch
Patch2:         %{name}-2.48-tftp-server-vulnerabilities.patch
Patch3:         %{name}-2.48-no-address-warning.patch
Patch4:         %{name}-2.48-initscript-fixes.patch
Patch5:         %{name}-2.48-wrt-man-fix.patch
Patch6:         %{name}-fix-lease-change-script.patch
Patch7:         %{name}-check-tftp-root-exists-and-is-accessible-at-startup.patch
Patch8:         %{name}-2.48-Set-SO_BINDTODEVICE-when-creating-sockets.patch
Patch9:         %{name}-2.48-Fixing-initscript-restart-stop-functions.patch
Patch10:        %{name}-2.48-Fix-DHCP-release-problem.patch
Patch11:        %{name}-2.48-fix_initscript_status.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  dbus-devel
BuildRequires:  pkgconfig

Requires(post):  /sbin/chkconfig
Requires(post):  /sbin/service
Requires(post):  /bin/sed /bin/grep
Requires(preun): /sbin/chkconfig
Requires(preun): /sbin/service

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
%patch0 -p1
%patch4 -p0
%patch9 -p1
%patch11 -p1

%build
# Note the main Makefile handles RPM_OPT_FLAGS internally,
# while we need to explicitly set it for the contrib Makefile
# We need to add "-fno-strict-aliasing" to solve strict-aliasing rules warnings
RPM_OPT_FLAGS="$RPM_OPT_FLAGS -fno-strict-aliasing" make %{?_smp_mflags}
CFLAGS="$RPM_OPT_FLAGS" make -C contrib/wrt %{?_smp_mflags}


%install
rm -rf $RPM_BUILD_ROOT
# normally i'd do 'make install'...it's a bit messy, though
mkdir -p $RPM_BUILD_ROOT%{_sbindir} $RPM_BUILD_ROOT%{_initrddir} \
        $RPM_BUILD_ROOT%{_mandir}/man8 \
        $RPM_BUILD_ROOT%{_var}/lib/dnsmasq \
        $RPM_BUILD_ROOT%{_sysconfdir}/dnsmasq.d \
        $RPM_BUILD_ROOT%{_sysconfdir}/dbus-1/system.d
install src/dnsmasq $RPM_BUILD_ROOT%{_sbindir}/dnsmasq
install dnsmasq.conf.example $RPM_BUILD_ROOT%{_sysconfdir}/dnsmasq.conf
install dbus/dnsmasq.conf $RPM_BUILD_ROOT%{_sysconfdir}/dbus-1/system.d/
install rpm/dnsmasq.init $RPM_BUILD_ROOT%{_initrddir}/dnsmasq
install -m 644 man/dnsmasq.8 $RPM_BUILD_ROOT%{_mandir}/man8/

# utils sub package
mkdir -p $RPM_BUILD_ROOT%{_bindir} \
         $RPM_BUILD_ROOT%{_mandir}/man1
install -m 755 contrib/wrt/dhcp_release $RPM_BUILD_ROOT%{_bindir}/dhcp_release
install -m 644 contrib/wrt/dhcp_release.1 $RPM_BUILD_ROOT%{_mandir}/man1/dhcp_release.1
install -m 755 contrib/wrt/dhcp_lease_time $RPM_BUILD_ROOT%{_bindir}/dhcp_lease_time
install -m 644 contrib/wrt/dhcp_lease_time.1 $RPM_BUILD_ROOT%{_mandir}/man1/dhcp_lease_time.1

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ "$1" = "2" ]; then # if we're being upgraded
    # if using the old leases location, move the file to the new one
    # but only if we're not clobbering another file
    #
    if [ -f /var/lib/misc/dnsmasq.leases -a ! -f /var/lib/dnsmasq/dnsmasq.leases ]; then
        # causes rpmlint to report dangerous-command-in-post,
        # but that's the price of selinux compliance :-(
        mv -f /var/lib/misc/dnsmasq.leases /var/lib/dnsmasq/dnsmasq.leases || :
    fi
    # ugly, but kind of necessary
    if [ ! `grep -q dhcp-leasefile=/var/lib/misc/dnsmasq.leases %{_sysconfdir}/dnsmasq.conf` ]; then
        cp %{_sysconfdir}/dnsmasq.conf %{_sysconfdir}/dnsmasq.conf.tmp || :
        sed -e 's/var\/lib\/misc/var\/lib\/dnsmasq/' < %{_sysconfdir}/dnsmasq.conf.tmp > %{_sysconfdir}/dnsmasq.conf || :
        rm -f %{_sysconfdir}/dnsmasq.conf.tmp || :
    fi
    /sbin/service dnsmasq condrestart >/dev/null 2>&1 || :
else # if we're being installed
    /sbin/chkconfig --add dnsmasq
fi

%preun
if [ "$1" = "0" ]; then     # execute this only if we are NOT doing an upgrade
    /sbin/service dnsmasq stop >/dev/null 2>&1 || :
    /sbin/chkconfig --del dnsmasq
fi


%files
%defattr(-,root,root,-)
%doc CHANGELOG COPYING-v3 FAQ doc.html setup.html dbus/DBus-interface
%config(noreplace) %attr(644,root,root) %{_sysconfdir}/dnsmasq.conf
%dir /etc/dnsmasq.d
%dir %{_var}/lib/dnsmasq
%config(noreplace) %attr(644,root,root) %{_sysconfdir}/dbus-1/system.d/dnsmasq.conf
%{_initrddir}/dnsmasq
%{_sbindir}/dnsmasq
%{_mandir}/man8/dnsmasq*

%files utils
%{_bindir}/dhcp_*
%{_mandir}/man1/dhcp_*

%changelog
* Mon Jun 15 2015 Matt Dupre <matt@projectcalico.org> - 2.72_calico0.24
- Sync IPv6 enhancement code with what we've submitted to upstream dnsmasq project

* Fri Mar 06 2015 Matt Dupre <matt@projectcalico.org> - 2.72_calico0.13
- Cope with multiple interfaces with the same LL address

* Fri Sep 26 2014 Neil Jerram <nj@metaswitch.com> - 2.72_calico0.4.1
- Fix for an intermittent Calico/IPv6 connectivity loss; please see
  https://github.com/Metaswitch/calico/issues/14 for details:
  - Set RA link-local addr correctly when sending on alias interface

* Tue Sep 16 2014 Neil Jerram <nj@metaswitch.com> - 2.72_calico0.4
- Updates for Calico/IPv6 connectivity:
  - Implement aliasing idea (per --bridge-interfaces) for DHCPv6 as well as for v4
  - Allow configuration of on-link (L) bit in Router Advertisement prefix option
  - Implement aliasing idea (per --bridge-interfaces) for solicited Router Advertisements
  - Implement aliasing for unsolicited router advertisements
  - Documentation for IPv6 enhancements

* Fri Jul 04 2014 Neil Jerram <nj@metaswitch.com> - 2.72_calico0.1
- Packaging for Project Calico, based on latest upstream source

* Fri Apr 04 2014 Tomas Hozza <thozza@redhat.com> - 2.48-14
- Fix initscript status command to check only the system instance (#991473)

* Fri Jan 04 2013 Tomas Hozza <thozza@redhat.com> - 2.48-13
- Fix the DHCP RELEASE problem when two or more dnsmasq instances are running (rhbz#887156)

* Wed Dec 19 2012 Tomas Hozza <thozza@redhat.com> - 2.48-12
- Fixing initscript restart stop functions (rhbz#850944)

* Mon Dec 17 2012 Tomas Hozza <thozza@redhat.com> - 2.48-11
- Revert previous changes because of many problems with --bind-dynamic option backport.
- Dropping dnsmasq-2.48-add-bind-dynamic-option.patch
- Set SO_BINDTODEVICE socket option when using --bind-interfaces (rhbz#884957)

* Tue Dec 04 2012 Tomas Hozza <thozza@redhat.com> - 2.48-10
- Fixed dnsmasq-2.48-add-bind-dynamic-option.patch
 - the option --bind-dynamic was not set correctly when used

* Sun Dec 02 2012 Tomas Hozza <thozza@redhat.com> - 2.48-9
- Added cc flag -fno-strict-aliasing to solve Testsuite regressions

* Fri Nov 30 2012 Tomas Hozza <thozza@redhat.com> - 2.48-8
- Fix CVE-2012-3411 (rhbz#882251)

* Fri Oct 12 2012 Jiri Denemark <jdenemar@redhat.com> - 2.48-7
- Fix lease-change script (rhbz#815819)
- Check tftp-root exists and is accessible at startup (rhbz#824214)

* Tue Feb 21 2012 Daniel Veillard <veillard@redhat.com> - 2.48-6
- Add DHCP lease management utils and man page in an utils subpackage (rhbz#794792)

* Wed Aug 17 2011 Daniel Veillard <veillard@redhat.com> - 2.48-5
- suppress the no address DHCP warning from logs (rhbz#704073)
- fixes various small problems in the initscript (rhbz#584009)

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
