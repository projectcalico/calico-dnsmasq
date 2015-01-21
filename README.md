This repository is Project Calico's fork of the Dnsmasq project.

Branches containing Calico-related work are generally named
calico\_`TAG` or `DISTRIBUTION`\_`TAG`, where

- `TAG` is the upstream (Simon Kelley) version number, such as 2.72

- `DISTRIBUTION` names the distribution that the branch's code aims to
  be installed on, such as "ubuntu" or "rhel7".

calico\_`TAG` branches contain Calico-specific changes to the upstream
code.  `DISTRIBUTION`\_`TAG` branches incorporate those code changes
and also contain packaging and metadata as appropriate for the target
distribution.  In some cases (such as Ubuntu) the packaging branches
represent the code changes in a quite different form from the Git
commits that you can see in the related calico\_`TAG` branch; e.g. as
patch files under `debian/patches`.  Therefore, if you're interested
in Calico's changes to the upstream code, best to look at the
calico\_`TAG` branch; if you're interested in the packaging for a
particular distribution, look at `DISTRIBUTION`\_`TAG`.

The following branches are currently our **active** ones - i.e. the ones
that we actively maintain for installing Calico on the relevant target
distribution:

- calico\_2.72 and ubuntu\_2.72, for installation on Ubuntu 14.04
  (Trusty).

- calico\_2.72 and ubuntu\_2.72\_no\_dnssec, for installing Calico
  using Mirantis Fuel 5.1.

- master, for installation on Red Hat Enterprise Linux 7.  (This
  branch is an exception to the general scheme described above, as it
  combines code changes and RPM packaging work in the same branch.)

Please do contact us via http://www.projectcalico.org/community/, for
help with rebasing or applying Calico patches to other upstream
releases, or with targeting other distributions.
