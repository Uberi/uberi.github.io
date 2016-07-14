---
title: Installing Ubuntu 15.10 on a Thinkpad W540
date: 2015-09-05
description: Instructions, pitfalls, gotchas, flaming acidic spike traps, and notes about loading a Linux distro onto the Thinkpad W540.
layout: post
---

The [Thinkpad W540](http://shop.lenovo.com/ca/en/laptops/thinkpad/w-series/w540/#tab-tech_specs) is a lovely machine. With an i7-4800MQ, 16GB of RAM, and a Quadro K2100M, it makes for a pretty solid workstation. However, setting it up proved a bit of a pain; this post outlines steps taken from a fresh machine to fully functional development environment on top of Ubuntu 15.10.

### Step 1: How to brick your motherboard

BIOS versions 2.08 and below will actually [brick the motherboard](https://forums.lenovo.com/t5/ThinkPad-W-Series-Laptops/HOWTO-Brick-a-W540-in-easy-steps/td-p/1400393) if you try to install Ubuntu. Make sure to upgrade this if it's not 2.09 or higher!

My machine came with Windows pre-installed on the 512GB SSD. I wanted to keep this for electronics and CAD stuff, so I shrank the Windows partition and left some free space for the Linux partition using the Disk Management utility in Windows (this tool often works better than GParted). I already happen to have a Ubuntu 15.04 [bootable USB](https://www.ubuntu.com/download/desktop/create-a-usb-stick-on-windows) lying around.

**Update:** I recently wanted to reinstall my OS, which meant these steps got another test run. This time, I started with Ubuntu GNOME 15.10 rather than Ubuntu Unity 15.04, and the instructions below have been updated to match. Note that they have also been tested and confirmed working with Ubuntu Unity 15.10 as well.

The boot device selection on the Thinkpad is triggered by F12. Booting the USB, I edited the "Install Ubuntu" GRUB entry to replace `quiet splash` with `quiet splash nomodeset` (editing is done by highlighting an option without selecting it, then pressing "e"), then booted with that ("Ctrl + X" finishes editing and boots). Note that this will make the resolution really low, but we'll fix that in the next step.

Going through the installer, Ubuntu was put in the empty space allocated earlier on the 512GB SSD. Similar to the live USB boot procedure, the kernel flags need to be added again by replacing `quiet splash` with `quiet splash nomodeset`.

### Step 2: Not setting the graphics card on fire

**Update:** If you don't really care about using the Nvidia card, just edit `/etc/default/grub` to replace `GRUB_CMDLINE_LINUX_DEFAULT="quiet splash"` with `GRUB_CMDLINE_LINUX_DEFAULT="quiet splash i915.modeset=1 nouveau.modeset=0"`, then run `sudo update-grub`. This makes everything use only the integrated Intel graphics.

**Update:** Nvidia's [new proprietary driver](http://www.nvidia.com/download/driverResults.aspx/95159/en-us) (other versions available [here](http://www.nvidia.com/download/index.aspx)) now seems to correctly support the Quadro K2100M. I personally haven't had much success with it, though some people have apparently made it work.

**Update:** some users report that nvidia-355 doesn't work with their hardware. The workaround for this is to use `nvidia-352` for all of the steps below in place of `nvidia-355`. Many thanks to **Hanno** for confirming that these steps also work on Linux Mint 17.

[This article](http://www.linuxveda.com/2015/07/16/how-to-install-drivers-for-nvidia-optimus-cards/) was a great starting point for making the nVidia GPU behave properly. However, the instructions needed quite a few changes to work properly. Here's what it took (make sure to run these one-by-one; copy/pasting these commands won't always work!):

* Get rid of the current, broken nVidia drivers:

{% highlight bash linenos=table %}
sudo apt-get remove --purge 'nvidia*'
sudo apt-get remove --purge xserver-xorg-video-nouveau
{% endhighlight %}

* Disable the bad nVidia drivers for the Quadro:

{% highlight bash linenos=table %}
echo '
# disable bad nVidia drivers
blacklist nouveau
blacklist lbm-nouveau
blacklist nvidia-96
blacklist nvidia-173
blacklist nvidia-current
blacklist nvidia-173-updates
blacklist nvidia-96-updates
alias nvidia nvidia_current_updates
alias nouveau off
alias lbm-nouveau off
options nouveau modeset=0' | sudo tee --append /etc/modprobe.d/blacklist.conf
{% endhighlight %}

* Install working nVidia drivers as well as [Bumblebee](http://bumblebee-project.org/), which adds nVidia Optimus support for making GPU switching work:

{% highlight bash linenos=table %}
sudo apt-add-repository ppa:bumblebee/stable -y
sudo add-apt-repository ppa:graphics-drivers/ppa -y
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install linux-source && sudo apt-get install linux-headers-$(uname -r)
sudo apt-get install nvidia-355 nvidia-settings
sudo apt-get install bumblebee bbswitch bumblebee-nvidia virtualgl virtualgl-libs virtualgl-libs-ia32:i386 virtualgl-libs:i386
sudo usermod -a -G bumblebee $USER
{% endhighlight %}

* Since Xorg-Edgers is on the bleeding edge, the latest nVidia drivers can have stability issues. That means it's necessary to explicitly write the version as 355. As root, make the following edits to `/etc/bumblebee/bumblebee.conf` (by the way, you can do this using `sudo gedit FILE_THAT_YOU_WANT_TO_EDIT_AS_ROOT`):
    * In the `[bumblebeed]` section, replace `Driver=` with `Driver=nvidia`.
    * In the `[driver-nvidia]` section, replace `KernelDriver=` with `KernelDriver=nvidia-355`.
    * In the `[driver-nvidia]` section, replace `LibraryPath=` with `LibraryPath=/usr/lib/nvidia-355:/usr/lib32/nvidia-355` (or prepend the paths to the existing paths if there are any, making sure to separate paths with **colons**).
    * In the `[driver-nvidia]` section, replace `XorgModulePath=` with `XorgModulePath=/usr/lib/nvidia-355,/usr/lib/xorg/modules` (or prepend the paths to the existing paths if there are any, making sure to separate paths with **commas**).
* Now to make sure that the display is set correctly. As root, edit `/etc/bumblebee/xorg.conf.nvidia `: replace `Option “ConnectedMonitor” “DFP”` with `Option “UseDisplayDevice” “none”` if the latter is not already present, and do nothing otherwise.

* Reboot the machine and check if it worked! Run `glxspheres64` and the output should show the info for the integrated graphics, and run `optirun glxspheres64` and the output should show the info for the nVidia graphics (and run at a much higher framerate too).

### Step 3: Avoiding computational defenestration

I started off with Ubuntu GNOME in order to GNOME-specific software like the Wacom tablet configuration GUI. However, if you didn't, it's simple to install GNOME afterward, by running the following:

{% highlight bash linenos=table %}
sudo apt-get install ubuntu-gnome-desktop
sudo service gdm restart
{% endhighlight %}

The fingerprint sensor was actually surprisingly easy to get working - there are pretty clear instructions over at the [Fingerprint GUI PPA](https://launchpad.net/~fingerprint/+archive/ubuntu/fingerprint-gui):

{% highlight bash linenos=table %}
sudo add-apt-repository ppa:fingerprint/fingerprint-gui
sudo apt-get update
sudo apt-get install libbsapi policykit-1-fingerprint-gui fingerprint-gui
{% endhighlight %}

After rebooting, Fingerprint GUI can be used to to log in, or even use fingerprint swipes to authenticate `sudo`! I ended up not using this after a while, but the whole experience is very smooth.

The battery life is pretty bad in this configuration. To improve it, install TLP to enable more advanced power settings when running off the battery:

{% highlight bash linenos=table %}
sudo apt-get install tlp tlp-rdw
sudo apt-get install tp-smapi-dkms acpi-call-dkms # Thinkpad-specific packages
{% endhighlight %}

I've always found the GNOME window grouping behaviour quite annoying, since it takes several extra keystrokes to get to the window you actually want. This can be fixed by turning on "Alternatetab" under "Extensions" in `gnome-tweak-tool`, which should already be installed.

One little tweak that makes life easier is swapping the CapsLock and Escape keys. This is also easily done using `gnome-tweak-tool`, where "Caps Lock key behaviour", under "Typing", can be set to "Swap ESC and Caps Lock". Likewise, you can disable Alt + Drag window moving by setting "Window Action key", under "Windows", to "Disabled".

There's also a bunch of other hardware-related things to consider over at the [ThinkWiki page for the W540](http://www.thinkwiki.org/wiki/Category:W540).

Of course, at this point we've only got the OS set up - there's still the matter of installing/configuring all the software!

### Other notes

* Thinkpad Ultra Docks and the built in 4-in-1 card reader are not supported. Unfortunately, there's no real workaround known at this time.
* The X-Rite Huey PRO Colorimeter doesn't work with Argyll color management. Basically, it'll be necessary to boot into Windows to generate the ICC file using Lenovo's official tools, then boot back into Ubuntu and apply the `*.icc` color profile using something like [dispcalGUI](http://dispcalgui.hoech.net/).
* When you have multiple monitors, a Wacom tablet will move the cursor across all of them. GNOME's Wacom configuration utility can map the tablet to a single monitor. If not using GNOME, modify this script to suit your needs:

{% highlight bash linenos=table %}
#!/usr/bin/env bash

# force Wacom graphics tablet to map to only one monitor
# run this on startup by adding it to `~/.bashrc`

# get the hardware values for the Wacom using `xinput --list`, and for the displays using `xrandr`
# the form is `xsetwacom set WACOM_HARDWARE_VALUE MapToOutput DISPLAY_HARDWARE_VALUE`
xsetwacom set "Wacom Intuos PT S Pen stylus" MapToOutput HDMI1
xsetwacom set "Wacom Intuos PT S Pen eraser" MapToOutput HDMI1
{% endhighlight %}

* I like to keep the mechanical keyboard on top of the laptop while using it, but it often presses down on the built-in keyboard, causing random extra keystrokes. To enable/disable the built-in keyboard on command, I've bound the following script to a hotkey:

{% highlight bash linenos=table %}
#!/usr/bin/env bash

if xinput list-props "AT Translated Set 2 keyboard" | grep "Device Enabled.*:.*0" > /dev/null; then
	xinput enable "AT Translated Set 2 keyboard"
	echo "Device enabled."
else
	xinput disable "AT Translated Set 2 keyboard"
	echo "Device disabled."
fi
{% endhighlight %}

* The Alt + Drag window moving behaviour in GNOME is rather annoying when trying to use applications that also use Alt + Drag, so this can be changed to Super + Drag using the following command:

{% highlight bash linenos=table %}
gsettings set org.gnome.desktop.wm.preferences mouse-button-modifier "<Super>"
{% endhighlight %}