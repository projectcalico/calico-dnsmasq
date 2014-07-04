This directory contains RPM packaging for the Calico distribution of
Dnsmasq.  The RPM spec and patches were first copied from the source
for RHEL6.5 (available at
http://ftp.redhat.com/pub/redhat/linux/enterprise/6Server/en/os/SRPMS/),
then adjusted for Calico using more up to date Dnsmasq source (as can
be seen at https://github.com/Metaswitch/calico-dnsmasq).

Specifically, as Calico is using up to date Dnsmasq source, we assume
that we do not require any of the _code_ patches that the RHEL6.5
packaging applies.
