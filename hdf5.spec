Name: hdf5
Version: 1.8.20
Release: 8
Summary: A data model, library, and file format for storing and managing data
License: BSD

URL:     https://portal.hdfgroup.org/display/HDF5/HDF5
Source0: https://support.hdfgroup.org/ftp/HDF5/releases/hdf5-1.8/hdf5-1.8.20/src/hdf5-1.8.20.tar.bz2

Patch0: hdf5-LD_LIBRARY_PATH.patch
Patch1: hdf5-mpi.patch
Patch2: hdf5-ldouble-ppc64le.patch

BuildRequires: gcc, gcc-c++
BuildRequires: krb5-devel, openssl-devel, zlib-devel, gcc-gfortran, time
BuildRequires: automake libtool
BuildRequires: openssh-clients
BuildRequires: libaec-devel

%description
HDF5 is a data model, library, and file format for storing and managing data. It supports an unlimited variety of datatypes, and is designed for flexible and efficient I/O and for high volume and complex data. HDF5 is portable and is extensible, allowing applications to evolve in their use of HDF5. The HDF5 Technology suite includes tools and applications for managing, manipulating, viewing, and analyzing data in the HDF5 format.

%package devel
Summary: HDF5 development files
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: libaec-devel%{?_isa}
Requires: zlib-devel%{?_isa}
Requires: gcc-gfortran%{?_isa}

%description devel
HDF5 development headers and libraries.

%prep
%setup -q -n %{name}-%{version}
%patch0 -p1
%patch1 -p1
%patch2 -p1

sed -i -e '/^STATIC_AVAILABLE=/s/=.*/=no/' */*/h5[cf]*.in
autoreconf -f -i

sed -e 's|-O -finline-functions|-O3 -finline-functions|g' -i config/gnu-flags

%build
%global _configure ../configure
%global configure_opts \\\
  --disable-silent-rules \\\
  --enable-fortran \\\
  --enable-fortran2003 \\\
  --enable-hl \\\
  --enable-shared \\\
  --with-szlib \\\
%{nil}

export CC=gcc
export CXX=g++
export F9X=gfortran
export LDFLAGS="%{__global_ldflags} -fPIC -Wl,-z,now -Wl,--as-needed"
mkdir build
pushd build
ln -s ../configure .
%configure \
  %{configure_opts} \
  --enable-cxx
sed -i -e 's! -shared ! -Wl,--as-needed\0!g' libtool
make LDFLAGS="%{__global_ldflags} -fPIC -Wl,-z,now -Wl,--as-needed"
popd

%install
%make_install -C build
%delete_la
cat >h5comp <<EOF
#!/bin/bash

ARCH=$(uname -m)

case $ARCH in
    x86_64 ) BITS=64;;
         * ) BITS=32;;
esac

exec $0-${BITS} "$@"
EOF
mkdir -p ${RPM_BUILD_ROOT}%{_fmoddir}
mv ${RPM_BUILD_ROOT}%{_includedir}/*.mod ${RPM_BUILD_ROOT}%{_fmoddir}
find ${RPM_BUILD_ROOT}%{_datadir} \( -name '*.[ch]*' -o -name '*.f90' \) -exec chmod -x {} +

%ifarch x86_64
sed -i -e s/H5pubconf.h/H5pubconf-64.h/ ${RPM_BUILD_ROOT}%{_includedir}/H5public.h
mv ${RPM_BUILD_ROOT}%{_includedir}/H5pubconf.h \
   ${RPM_BUILD_ROOT}%{_includedir}/H5pubconf-64.h
for x in h5c++ h5cc h5fc
do
  mv ${RPM_BUILD_ROOT}%{_bindir}/${x} \
     ${RPM_BUILD_ROOT}%{_bindir}/${x}-64
  install -m 0755 h5comp ${RPM_BUILD_ROOT}%{_bindir}/${x}
done
%else
sed -i -e s/H5pubconf.h/H5pubconf-32.h/ ${RPM_BUILD_ROOT}%{_includedir}/H5public.h
mv ${RPM_BUILD_ROOT}%{_includedir}/H5pubconf.h \
   ${RPM_BUILD_ROOT}%{_includedir}/H5pubconf-32.h
for x in h5c++ h5cc h5fc
do
  mv ${RPM_BUILD_ROOT}%{_bindir}/${x} \
     ${RPM_BUILD_ROOT}%{_bindir}/${x}-32
  install -m 0755 h5comp ${RPM_BUILD_ROOT}%{_bindir}/${x}
done
%endif

mkdir -p ${RPM_BUILD_ROOT}/%{_rpmmacrodir}
cat > ${RPM_BUILD_ROOT}/%{_rpmmacrodir}/macros.hdf5 <<EOF
# HDF5 version is
%%_hdf5_version %{version}
EOF

%check
make -C build check
%ldconfig_scriptlets

%files
%license COPYING
%doc MANIFEST README.txt release_docs/RELEASE.txt
%doc release_docs/HISTORY*.txt
%{_bindir}/gif2h5
%{_bindir}/h52gif
%{_bindir}/h5copy
%{_bindir}/h5debug
%{_bindir}/h5diff
%{_bindir}/h5dump
%{_bindir}/h5import
%{_bindir}/h5jam
%{_bindir}/h5ls
%{_bindir}/h5mkgrp
%{_bindir}/h5perf_serial
%{_bindir}/h5repack
%{_bindir}/h5repart
%{_bindir}/h5stat
%{_bindir}/h5unjam
%{_libdir}/*.so.10*
%{_libdir}/libhdf5_cpp.so.15*
%{_libdir}/libhdf5_hl_cpp.so.11*

%files devel
%{_bindir}/h5c++*
%{_bindir}/h5cc*
%{_bindir}/h5fc*
%{_bindir}/h5redeploy
%{_includedir}/*.h
%{_libdir}/*.so
%{_libdir}/*.settings
%{_fmoddir}/*.mod
%{_datadir}/hdf5_examples/
%{_libdir}/*.a
%{_rpmmacrodir}/macros.hdf5

%changelog
* Tue Sep 15 2020 shaoqiang kang <kangshaoqiang1@openeuler.org> - 1.8.20-8
- Modify source

* Tue Oct 22 2019 openEuler Buildteam <buildteam@openeuler.org> - 1.8.20-7
- Package init
