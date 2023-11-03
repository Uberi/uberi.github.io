---
title: Activating the Xreal Air 2 on Linux
date: 2023-11-02
description: How to get around WebUSB permission issues when setting up the Xreal Air 2 AR glasses.
layout: post
---

For productivity purposes, I recently got an [Xreal Air 2](https://www.xreal.com/air/). One of the big reasons for these glases over other AR/VR options was that it has standard USB-C DisplayPort alt-mode support, so it'll work without any additional untrustworthy/proprietary software.

I didn't find this out until they arrived, but the glasses don't work out of the box - they require you to activate them using Chrome on Windows, an Android device, or an Xreal Beam! The process seems to be used to update the firmware and perform some diagnostics on the device, which is somewhat understandable, but I'd have to borrow or buy one to proceed.

[This post on the /r/nreal subreddit](https://old.reddit.com/r/nreal/comments/y86vj2/can_a_linux_system_use_its_version_of_chrome_to/jeey4bc/) has a workaround targeted to the Xreal Air 1, but it doesn't work here because the workaround is only applied until the device is disconnected, and the Air 2 seems to disconnect/reconnect several times during the update process, losing the workaround midway through.

Here's a process that does work for the Air 2, tested on Ubuntu 22.04 LTS:

1. Create a udev rule that makes all newly-added `hidraw` devices readable/writeable: `echo 'SUBSYSTEM=="hidraw", MODE="0666", GROUP="plugdev"' | sudo tee /etc/udev/rules.d/50-xreal-air-2.rules && sudo udevadm control --reload-rules`.
    * Generally you would add a filter on similar udev rules for `idVendor` or other hardware-specific attributes, but in this case the vendor ID is actually on one of the ancestor devices instead.
2. Download a Chromium AppImage and make it executable: https://github.com/ivan-hc/Chromium-Web-Browser-appimage/releases/tag/continuous
    * Some systems sandbox their Chrome/Chromium using Snap or Flatpak. This causes countless issues with WebUSB, and I want these instructions to be foolproof, so we'll skip all of that and just download a known-good AppImage instead.
3. Open the Chromium AppImage and go to the [Xreal Air 2 firmware update webpage](https://ota.xreal.com/air2-update?version=1).
    * You may find the `chrome://device-log` page useful as well to see if the Air 2's HID interfaces are being properly detected by Chromium.
4. Connect the Xreal Air 2 via USB-C port. It has to be a USB-C port that supports Power Delivery, due to the hardware's relatively high power requirements.
5. Follow the steps on the firmware update webpage. They should now succeed where they would previously fail.
6. Remove the udev rule we added earlier: `sudo rm /etc/udev/rules.d/50-xreal-air-2.rules && sudo udevadm control --reload-rules`
    * This rule is too general, and you can always add it back next time you need to update the firmware.

With this, we're ready to go! For fun, I'm also trying out [a driver that uses the onboard IMU as a mouse](https://github.com/wheaney/xrealAirLinuxDriver/).