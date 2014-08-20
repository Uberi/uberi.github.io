#!/bin/bash

# OpenSpades automatic build script
# by Anthony Zhang <azhang9@gmail.com>

# set up working directory
mkdir OpenSpades
cd OpenSpades

# install some packages first
sudo apt-get install libopenal-dev libpng-dev libtiff-dev
sudo apt-get install pkg-config libglew-dev libcurl3-openssl-dev

# install SDL
wget http://www.libsdl.org/release/SDL2-2.0.2.tar.gz
tar -zxvf SDL2-2.0.2.tar.gz
cd SDL2-2.0.2/
./configure
make clean
make
sudo make install
cd ../

# install SDL_image
wget https://www.libsdl.org/projects/SDL_image/release/SDL2_image-2.0.0.tar.gz
tar -zxvf SDL2_image-2.0.0.tar.gz
cd SDL2_image-2.0.0/
./configure --disable-png-shared
make clean
make
sudo make install
cd ../

# build OpenSpades
wget https://github.com/yvt/openspades/archive/master.tar.gz
tar -zxvf master.tar.gz
cd openspades-master
cmake . -DCMAKE_BUILD_TYPE=Release
make

# install and run OpenSpades
sudo make install
openspades
