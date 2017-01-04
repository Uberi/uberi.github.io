---
title: Building OpenSpades on Ubuntu 14.04
date: 2014-08-19
description: More comprehensive instructions for building OpenSpades, including solutions for several common build issues.
layout: post
---

[OpenSpades](http://openspades.yvt.jp/) is a multiplayer voxel-based FPS with fully modifiable terrain, based on an older game called Ace of Spades. It's best enjoyed with a large map and a couple of friends:

![OpenSpades Screenshot](screenshot.png)

Building this on non-Windows/OS X systems is a bit of a pain. Here's what the instructions are missing:

* The `libopenal-dev`, `libpng-dev`, and `libtiff-dev` packages are required - without them, the program will build but not run.
* "SDL_Image" needs to be configured with the `--disable-png-shared option.
* A resource pack to actually run the game - an archive with the models, sounds, and etc. These are available from a different place, and the game will not run without one.

Here's a [nice bash script to do the whole build from scratch](build-openspades.sh). When run with something like `bash build-openspades.sh`, the script does everything needed to download, builds, and install the game. You may need to enter your password when prompted in order to do the actual installation. It's meant to be usable on a fresh OS install.

If you're running Ubuntu 16.04 LTS, here's [a prebuilt DEB package](openspades-0.0.12b-Linux-x86_64.deb).
