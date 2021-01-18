%global with_mpich 1
%global with_openmpi 1
%if %{with_mpich}
%global mpi_list mpich
%endif
%if %{with_openmpi}
%global mpi_list %{?mpi_list} openmpi
%endif

Name: hdf5
Version: 1.8.20
Release: 11
Summary: A data model, library, and file format for storing and managing data
License: GPL

URL:     https://portal.hdfgroup.org/display/HDF5/HDF5
Source0: https://support.hdfgroup.org/ftp/HDF5/releases/hdf5-1.8/hdf5-1.8.20/src/hdf5-1.8.20.tar.bz2

Patch0: hdf5-LD_LIBRARY_PATH.patch
Patch1: hdf5-mpi.patch
Patch2: hdf5-ldouble-ppc64le.patch
Patch3: CVE-2018-17233.patch
Patch4: CVE-2018-17234.patch
Patch5: CVE-2018-17237.patch
Patch6: CVE-2018-17434-CVE-2018-17437.patch
Patch7: CVE-2018-17438.patch
Patch8: CVE-2017-17506.patch
Patch9: fix-compile-error.patch
Patch10: CVE-2018-17432.patch
Patch11: CVE-2018-17435.patch
Patch12: CVE-2018-13869-CVE-2018-13870.patch
Patch13: CVE-2018-13873.patch

BuildRequires: gcc, gcc-c++
BuildRequires: krb5-devel, openssl-devel, zlib-devel, gcc-gfortran, time
BuildRequires: automake libtool
BuildRequires: openssh-clients
BuildRequires: libaec-devel

%description
HDF5 is a data model, library, and file format for storing and managing data. It supports an unlimited variety of datatypes, and is designed for flexible and efficient I/O and for high volume and complex data. HDF5 is portable and is extensible, allowing applications to evolve in their use of HDF5. The HDF5 Technology suite includes tools and applications for managing, manipulating, viewing, and analyzing data in the HDF5 format.

%package devel
Summary: HDF5 development files
Provides: hdf5-static = %{version}-%{release}
Obsoletes: hdf5-static < %{version}-%{release}
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: libaec-devel%{?_isa}
Requires: zlib-devel%{?_isa}
Requires: gcc-gfortran%{?_isa}

%description devel
HDF5 development headers and libraries.

%if %{with_mpich}
%package mpich
Summary: HDF5 mpich libraries
BuildRequires: mpich-devel
Provides: %{name}-mpich2 = %{version}-%{release}
Obsoletes: %{name}-mpich2 < %{version}-%{release}

%description mpich
HDF5 parallel mpich libraries


%package mpich-devel
Summary: HDF5 mpich development files
Requires: %{name}-mpich%{?_isa} = %{version}-%{release}
Requires: libaec-devel%{?_isa}
Requires: zlib-devel%{?_isa}
Requires: mpich-devel%{?_isa}
Provides: %{name}-mpich2-devel = %{version}-%{release}
Obsoletes: %{name}-mpich2-devel < %{version}-%{release}

%description mpich-devel
HDF5 parallel mpich development files

%package mpich-static
Summary: HDF5 mpich static libraries
Requires: %{name}-mpich-devel%{?_isa} = %{version}-%{release}
Provides: %{name}-mpich2-static = %{version}-%{release}
Obsoletes: %{name}-mpich2-static < %{version}-%{release}

%description mpich-static
HDF5 parallel mpich static libraries
%endif

%if %{with_openmpi}
%package openmpi
Summary: HDF5 openmpi libraries
BuildRequires: openmpi-devel

%description openmpi
HDF5 parallel openmpi libraries


%package openmpi-devel
Summary: HDF5 openmpi development files
Requires: %{name}-openmpi%{?_isa} = %{version}-%{release}
Requires: libaec-devel%{?_isa}
Requires: zlib-devel%{?_isa}
Requires: openmpi-devel%{?_isa}

%description openmpi-devel
HDF5 parallel openmpi development files


%package openmpi-static
Summary: HDF5 openmpi static libraries
Requires: %{name}-openmpi-devel%{?_isa} = %{version}-%{release}

%description openmpi-static
HDF5 parallel openmpi static libraries
%endif

%prep
%autosetup -n %{name}-%{version} -p1

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

export CC=mpicc
export CXX=mpicxx
export F9X=mpif90
export LDFLAGS="%{__global_ldflags} -fPIC -Wl,-z,now -Wl,--as-needed"
for mpi in %{?mpi_list}
do
  mkdir $mpi
  pushd $mpi
  module load mpi/$mpi-%{_arch}
  ln -s ../configure .
  %configure \
    %{configure_opts} \
    FCFLAGS="$FCFLAGS -I$MPI_FORTRAN_MOD_DIR" \
    --enable-parallel \
    --exec-prefix=%{_libdir}/$mpi \
    --libdir=%{_libdir}/$mpi/lib \
    --bindir=%{_libdir}/$mpi/bin \
    --sbindir=%{_libdir}/$mpi/sbin \
    --includedir=%{_includedir}/$mpi-%{_arch} \
    --datarootdir=%{_libdir}/$mpi/share \
    --mandir=%{_libdir}/$mpi/share/man
  sed -i -e 's! -shared ! -Wl,--as-needed\0!g' libtool
  make LDFLAGS="%{__global_ldflags} -fPIC -Wl,-z,now -Wl,--as-needed"
  module purge
  popd
done

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

for mpi in %{?mpi_list}
do
  module load mpi/$mpi-%{_arch}
  make -C $mpi install DESTDIR=${RPM_BUILD_ROOT}
  rm $RPM_BUILD_ROOT/%{_libdir}/$mpi/lib/*.la
  #Fortran modules
  mkdir -p ${RPM_BUILD_ROOT}${MPI_FORTRAN_MOD_DIR}
  mv ${RPM_BUILD_ROOT}%{_includedir}/${mpi}-%{_arch}/*.mod ${RPM_BUILD_ROOT}${MPI_FORTRAN_MOD_DIR}/
  module purge
done

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

%if %{with_mpich}
%files mpich
%license COPYING
%doc MANIFEST README.txt release_docs/RELEASE.txt
%doc release_docs/HISTORY*.txt
%{_libdir}/mpich/bin/gif2h5
%{_libdir}/mpich/bin/h52gif
%{_libdir}/mpich/bin/h5copy
%{_libdir}/mpich/bin/h5debug
%{_libdir}/mpich/bin/h5diff
%{_libdir}/mpich/bin/h5dump
%{_libdir}/mpich/bin/h5import
%{_libdir}/mpich/bin/h5jam
%{_libdir}/mpich/bin/h5ls
%{_libdir}/mpich/bin/h5mkgrp
%{_libdir}/mpich/bin/h5redeploy
%{_libdir}/mpich/bin/h5repack
%{_libdir}/mpich/bin/h5perf
%{_libdir}/mpich/bin/h5perf_serial
%{_libdir}/mpich/bin/h5repart
%{_libdir}/mpich/bin/h5stat
%{_libdir}/mpich/bin/h5unjam
%{_libdir}/mpich/bin/ph5diff
%{_libdir}/mpich/lib/*.so.10*

%files mpich-devel
%{_includedir}/mpich-%{_arch}
%{_fmoddir}/mpich/*.mod
%{_libdir}/mpich/bin/h5pcc
%{_libdir}/mpich/bin/h5pfc
%{_libdir}/mpich/lib/lib*.so
%{_libdir}/mpich/lib/lib*.settings
%{_libdir}/mpich/share/hdf5_examples/

%files mpich-static
%{_libdir}/mpich/lib/*.a
%endif

%if %{with_openmpi}
%files openmpi
%license COPYING
%doc MANIFEST README.txt release_docs/RELEASE.txt
%doc release_docs/HISTORY*.txt
%{_libdir}/openmpi/bin/gif2h5
%{_libdir}/openmpi/bin/h52gif
%{_libdir}/openmpi/bin/h5copy
%{_libdir}/openmpi/bin/h5debug
%{_libdir}/openmpi/bin/h5diff
%{_libdir}/openmpi/bin/h5dump
%{_libdir}/openmpi/bin/h5import
%{_libdir}/openmpi/bin/h5jam
%{_libdir}/openmpi/bin/h5ls
%{_libdir}/openmpi/bin/h5mkgrp
%{_libdir}/openmpi/bin/h5perf
%{_libdir}/openmpi/bin/h5perf_serial
%{_libdir}/openmpi/bin/h5redeploy
%{_libdir}/openmpi/bin/h5repack
%{_libdir}/openmpi/bin/h5repart
%{_libdir}/openmpi/bin/h5stat
%{_libdir}/openmpi/bin/h5unjam
%{_libdir}/openmpi/bin/ph5diff
%{_libdir}/openmpi/lib/*.so.10*

%files openmpi-devel
%{_includedir}/openmpi-%{_arch}
%{_fmoddir}/openmpi/*.mod
%{_libdir}/openmpi/bin/h5pcc
%{_libdir}/openmpi/bin/h5pfc
%{_libdir}/openmpi/lib/lib*.so
%{_libdir}/openmpi/lib/lib*.settings
%{_libdir}/openmpi/share/hdf5_examples/

%files openmpi-static
%{_libdir}/openmpi/lib/*.a
%endif

%changelog
* Fri Jan 15 2021 yanan li <liyanan32@huawei.com> - 1.8.20-11
- add sub packages hdf5-openmpi-static, hdf5-openmpi-devel, hdf5-openmpi,
- hdf5-mpich-static, hdf5-mpich-devel, hdf5-mpich

* Mon Dec 14 2020 openEuler Buildteam <buildteam@openeuler.org> - 1.8.20-10
- fix CVE-2017-17506 CVE-2018-17432 CVE-2018-17435 CVE-2018-13869 CVE-2018-13870 CVE-2018-13873

* Mon Nov 9 2020 wangxiao <wangxiao65@huawei.com> - 1.8.20-9
- fix CVE-2018-17233 CVE-2018-17234 CVE-2018-17237 CVE-2018-17434 CVE-2018-17437 CVE-2018-17438

* Tue Sep 15 2020 shaoqiang kang <kangshaoqiang1@openeuler.org> - 1.8.20-8
- Modify source

* Tue Oct 22 2019 openEuler Buildteam <buildteam@openeuler.org> - 1.8.20-7
- Package init
