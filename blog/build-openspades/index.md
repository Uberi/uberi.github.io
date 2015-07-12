---
title: Building OpenSpades on Ubuntu 14.04
date: 2014-08-19
layout: post
---

[OpenSpades](https://sites.google.com/a/yvt.jp/openspades/) is a multiplayer voxel-based FPS with fully destructible terrain and pretty complete building mechanics. Based on an older game called Ace of Spades, I'd have to say it really captures the feel of the original:

![OpenSpades Screenshot](screenshot.png)

The downloads page has packages for Windows and OS X, so [give it a spin](https://sites.google.com/a/yvt.jp/openspades/downloads)! On Ubuntu, we'll need to be a little creative to get things running:

* The `libopenal-dev`, `libpng-dev`, and `libtiff-dev` packages are required - without them, the program will build but not run.
* "SDL_Image" needs to be configured with the `--disable-png-shared option.
* CMake and Make need to be available. While Make usually is, CMake often isn't.
* A resource pack to actually run the game - an archive with the models, sounds, and etc. These are available from a different place, and the game will not run without one.

Here's a [nice bash script to do the whole build from scratch](build-openspades.sh). When run with something like `bash build-openspades.sh`, the script downloads, builds, and installs the game completely automatically. You may need to enter your password when prompted in order to do the actual installation.

Additionally, if you're running Ubuntu, here's [a prebuilt DEB package](https://dl.dropboxusercontent.com/u/8097754/openspades-0.0.12-Linux-x86_64.deb) for 14.04 (Trusty Tahr).
