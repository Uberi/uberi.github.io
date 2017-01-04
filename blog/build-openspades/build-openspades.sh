#!/bin/bash

# OpenSpades automatic build script
# by Anthony Zhang <azhang9@gmail.com>

# set up working directory
mkdir OpenSpades
cd OpenSpades

# install some packages first
sudo apt-get install pkg-config cmake build-essential
sudo apt-get install libopenal-dev libpng-dev libtiff-dev libglew-dev libcurl3-openssl-dev
sudo apt-get install libsdl2-dev libsdl2-image-dev

# build OpenSpades
wget https://github.com/yvt/openspades/archive/master.tar.gz
tar -zxvf master.tar.gz
cd openspades-master
cmake . -DCMAKE_BUILD_TYPE=Release
make

# install and run OpenSpades
sudo make install
