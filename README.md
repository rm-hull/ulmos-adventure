Ulmo's Adventure
================

A fork of Sam Eldred's http://code.google.com/p/rpg-world/

What's New
----------
* (10/06/2013) Forked from svn into git
* (10/06/2013) Use a Wii-mote to control Ulmo
* (10/06/2013) Optimized screen for QVGA LCD

Now optimised for the Raspberry Pi!
-----------------------------------
Help Ulmo evade enemies, collect coins and find his way to the end of an 
amazing (but short) adventure. Use cursor keys to move, space to do stuff,
X to toggle sound and ESC to quit.

16-bit style graphics, a top-down perspective and tile-based maps - a retro
style RPG much like the old SNES classics. Also features some pseudo-3D 
elements, eg. the ability to move underneath bridges, etc.

Graphics were created in Gimp, sounds in CFXR. The game itself is 
implemented in Python/Pygame and the map editor is in Java SWT.

See also http://pygame.org/project-Ulmo%27s+Adventure-2042-3702.html

![Screenshot](https://raw.github.com/rm-hull/ulmos-adventure/master/2042.png)

Using the Wiimote
-----------------
Ensure that the pythonr-cwiid module is installed and bluetooth is
installed and enabled (apt package 'bluez').

    $ dmesg | grep -i blue
    [    5.819514] Bluetooth: Core ver 2.16
    [    5.824335] Bluetooth: HCI device and connection manager initialized
    [    5.824407] Bluetooth: HCI socket layer initialized
    [    5.824451] Bluetooth: L2CAP socket layer initialized
    [    5.824536] Bluetooth: SCO socket layer initialized
    [   30.849159] Bluetooth: BNEP (Ethernet Emulation) ver 1.3
    [   30.849192] Bluetooth: BNEP filters: protocol multicast
    [   30.849239] Bluetooth: BNEP socket layer initialized
    [   30.872984] Bluetooth: RFCOMM TTY layer initialized
    [   30.873067] Bluetooth: RFCOMM socket layer initialized
    [   30.873084] Bluetooth: RFCOMM ver 1.11

    
