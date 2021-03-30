#!/usr/bin/env 
export DEBIAN_FRONTEND="noninteractive"
echo 'debconf debconf/frontend select Noninteractive' | sudo debconf-set-selections;
ARG DEBIAN_FRONTEND=noninteractive;
apt purge r-base* r-recommended r-cran-*
apt autoremove
apt update
ARG DEBIAN_FRONTEND=noninteractive;
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys E298A3A825C0D65DFD57CBB651716619E084DAB9
add-apt-repository 'deb https://cloud.r-project.org/bin/linux/ubuntu bionic-cran35/';
apt update;
apt install -y r-base;
ARG DEBIAN_FRONTEND=noninteractive;
apt-get install libxml2-dev libcurl4-openssl-dev libssl-dev -y;
Rscript /autograder/source/install_rags_packages.R;
Rscript /autograder/source/install_packages.R;
apt purge libxml2-dev libcurl4-openssl-dev libssl-dev -y;