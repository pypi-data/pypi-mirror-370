#!/bin/sh
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                          Conda environment for Docker/Linux (x64)                            %     
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Shell script to install various predefined programs on the executing linux system with known 
# compatibility fixes.
#
# Created on 11.06.2021
# 
# Version: 1.0
# -------------------------------------------------------------------------------------------------
#    Requirements and dependencies:
#        - 
#
#     Changelog:
#        - Added Alpine support
#        - Added silent mode for wget
#        - Added rust compiler and git-lfs option                                 // mg 23.02.2023
#        - Added alias to gcc                                                     // mg 20.09.2024
#
# -------------------------------------------------------------------------------------------------
for i in "$@"
do
case $i in
    -p=*|--package=*)
    package="${i#*=}"
    shift # Past Argument=Value
    ;;
    *)    # Unknown option
    ;;
esac
done
# Check which package is requested for installation. Defaults to all.
export INSTALL_PACKAGE=${package:-"conda"};
# Get current OS
{ export OS=$(grep 'VERSION_CODENAME=' /etc/os-release | sed 's/^.*=//') ; } || { export OS="unknown" } ; } ;
# Get current version
{ export ID=$(grep 'VERSION_ID=' /etc/os-release | sed 's/^.*=//') ; } || { export ID="unknown" } ; } ;
# Interoperability and EOL of RHEL
{ command -v yum >/dev/null 2>&1 ; } && { sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-Linux-* >/dev/null 2>&1 && sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-Linux-* ; } || { true ; } ; 
{ command -v yum >/dev/null 2>&1 ; } && { yum -y --enablerepo=powertools update >/dev/null 2>&1 && export powertools="--enablerepo=powertools" ; } || { true ; } ;
# Interoperability and EOL of CENTOS
if [ "$ID" \< "8" ]; then { command -v yum >/dev/null 2>&1 ; } \
 && { sed -i s/mirror.centos.org/vault.centos.org/g /etc/yum.repos.d/*.repo ; } \
 && { sed -i s/^#.*baseurl=http/baseurl=http/g /etc/yum.repos.d/*.repo ; } \
 && { sed -i s/^mirrorlist=http/#mirrorlist=http/g /etc/yum.repos.d/*.repo ; } \
 && { sh -c 'echo "sslverify=false" >> /etc/yum.conf' ; } ; fi ; 
# Interoperability and EOL of STRETCH
if [ "$OS" = 'stretch' ]; then { rm -f /etc/apt/sources.list \
 && echo "deb http://archive.debian.org/debian/ stretch main contrib non-free" >> /etc/apt/sources.list \
 && echo "deb http://archive.debian.org/debian-security/ stretch/updates main contrib non-free" >> /etc/apt/sources.list ; } ; fi;
# Function for creating a conda environment
conda()
{
# Support Alpine
command -v apk >/dev/null 2>&1 && { apk --update add py3-pip bash ca-certificates jq wget curl doxygen git git-lfs subversion docker openrc alpine-sdk libstdc++ glib musl-locales musl-locales-lang; rc-update add docker boot; } ; 
command -v apk >/dev/null 2>&1 && { \
   wget -q -O /etc/apk/keys/sgerrand.rsa.pub https://alpine-pkgs.sgerrand.com/sgerrand.rsa.pub \
&& curl -L "https://github.com/sgerrand/alpine-pkg-glibc/releases/download/2.34-r0/glibc-2.34-r0.apk" -o glibc.apk \
&& apk add --force glibc.apk \
&& curl -L "https://github.com/sgerrand/alpine-pkg-glibc/releases/download/2.34-r0/glibc-bin-2.34-r0.apk" -o glibc-bin.apk \
&& apk add glibc-bin.apk \
&& curl -L "https://github.com/andyshinn/alpine-pkg-glibc/releases/download/2.34-r0/glibc-i18n-2.34-r0.apk" -o glibc-i18n.apk \
&& apk add --allow-untrusted glibc-i18n.apk \
&& /usr/glibc-compat/bin/localedef -i en_US -f UTF-8 en_US.UTF-8 \
&& /usr/glibc-compat/sbin/ldconfig /lib /usr/glibc/usr/lib \
&& rm -rf glibc*apk /var/cache/apk/* ; }
# Support Debian & Ubuntu
{ command -v apt >/dev/null 2>&1 ; } && { apt-get update && apt-get install -y --no-install-recommends pip cpp ca-certificates jq wget curl doxygen docker.io git git-lfs subversion locales locales-all ; } ;
# Support CentOs
{ command -v yum >/dev/null 2>&1 ; } && { yum -y ${powertools:-} update ; } && { yum -y update && yum -y ${powertools:-} install python3-pip cpp ca-certificates jq wget curl doxygen docker git git-lfs subversion langpacks-en glibc-all-langpacks ; } ;
# Support OpenSuse
{ command -v zypper >/dev/null 2>&1 ; } && { zypper update -y && zypper install -y python3-pip cpp ca-certificates jq wget curl doxygen docker git git-lfs subversion ; } ;
# Support both Fedora & AlmaLinux
{ command -v dnf >/dev/null 2>&1 ; } && { packages="python3-pip cpp ca-certificates jq wget curl doxygen docker git git-lfs subversion"; dnf update -y && dnf install -y $packages || dnf --enablerepo=crb --allowerasing install -y $packages ; } ;
# Install conda environment
alias pip=pip3 && pip install anybadge >/dev/null 2>&1 ;
# Fetch an old installer known for its stability.
wget -q https://github.com/conda-forge/miniforge/releases/download/23.11.0-0/Mambaforge-$(uname)-$(uname -m).sh -O miniconda.sh ;
# Install a compatible version of conda.
bash miniconda.sh -b -p /opt/conda && rm -rf miniconda.sh ;
# Update PATH variable and update base version of conda to its latest release.
export PATH=/opt/conda/bin:$PATH ; command conda install -y -n base "conda>=$(command conda -V | awk '{print $2}')" ;
}
# Function to install compiler dependencies
compiler()
{
# Support Alpine
{ command -v apk >/dev/null 2>&1 ; } && { apk --update add sed curl make gcc g++ gfortran meson musl-dev blas-dev lapack-dev libffi-dev openblas-dev openssl-dev jpeg-dev zlib-dev linux-headers ; } ; 
# Support Debian & Ubuntu
{ command -v apt >/dev/null 2>&1 ; } && { apt-get update && apt-get install -y curl make gcc g++ gfortran libblas-dev liblapack-dev libffi-dev libssl-dev ; } ;
# Support CentOs
{ command -v yum >/dev/null 2>&1 && yum -y ${powertools:-} update ; } && { yum -y update && yum -y ${powertools:-} install curl make gcc gcc-c++ gcc-gfortran blas-devel lapack-devel libffi-devel openssl-devel ; } ;
# Support OpenSuse
{ command -v zypper >/dev/null 2>&1 ; } && { zypper update -y && zypper install -y curl make gcc gcc-c++ gcc-fortran blas-devel lapack-devel libffi-devel openssl-devel ; } ;
# Support Fedora
{ command -v dnf >/dev/null 2>&1 ; } && { dnf update -y && dnf install -y curl make gcc gcc-c++ gcc-gfortran blas-devel lapack-devel libffi-devel openssl-devel ; } ;
}
# Function for installing git-lfs from script.
lfs()
{ { curl -sSL https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | bash - ; } || true ; }
# Function for installing rust compiler
rust()
{ { curl https://sh.rustup.rs -sSf | sh -s -- -y ; } || true ; }
# Install a conda environment with all preset compiler dependencies
if [ "$INSTALL_PACKAGE" = 'all' ] || [ "$INSTALL_PACKAGE" = 'conda' ]; then conda; fi;
if [ "$INSTALL_PACKAGE" = 'all' ] || [ "$INSTALL_PACKAGE" = 'compiler' ]; then compiler; fi;
# Optional non-default installation options. Fetch git-lfs or rust compiler from shell script.
if [ "$INSTALL_PACKAGE" = 'all' ] || [ "$INSTALL_PACKAGE" = 'git-lfs' ]; then lfs; fi;
if [ "$INSTALL_PACKAGE" = 'all' ] || [ "$INSTALL_PACKAGE" = 'rust' ]; then rust; fi;
if [ "$INSTALL_PACKAGE" = 'gcc' ]; then compiler; fi; 
# Compatibility option. Can be safely executed on most platforms.
if [ "$INSTALL_PACKAGE" = 'compat' ]; then compiler; rust; fi; 
exit 0