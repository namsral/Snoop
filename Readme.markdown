Snoop
=====

Snoop is a network daemon to tracks iPhones and other mobile iOS devices in buildings based on WiFi connectivity and log their presence for use in other applications.

One use case for this software is as a complimentary service to track the presence of people in a building based on the iPhone they carry. Something along the lines of automatic checkin/checkout.


Usage
-------

Make sure you have enabled WiFi Sync in your mobile iOS device. And you'll need to run snoop with root privileges as it needs to bind to the network interface and capture incoming traffic.

    $ sudo snoop \
        --targets="<MAC>,<MAC>" \
        --interface="eth0" \
        --callback_url="http://example.com/api/devices"

Whenever a device is spotted on the network a POST request will be made to the callback URL containing the a current UTC datestring and the device's MAC address:

    mac_addres="00:00:00:00:00:00", date="2012-06-28T14:59:44Z"


Installation
------------

    $ pip install tornado
    $ python setup.py install


Dependencies
------------

- [Tornado Web][1] Python library
- Linux kernel 2.4 and up


How does it work?
-----------------

Glad you asked because this is the interesting part.

Mobile devices like the iPhone, iPad and iPod Touch are power constrained and therefore tend to be very quiet on a network, not much traffic going in or out in contrast to desktop or even laptop computers.

While there are some obvious approaches to solve this problem most of them are to disruptive and not very flexible:

- Installing a background process on the mobile iOS device to poll a server
- Setup mobile iOS devices with a proxy or gateway to filter traffic

A more subtle and flexible approach is to use WoL (Wake on LAN). And although there is support for WoL (Wake on LAN) in iOS called [Bonjour Sleep Proxy][0] it's only available on the Apple TV and presumably the new Airport Express which also runs iOS. Which leaves out iOS on mobile devices. But since iOS 5.0, iTunes has gained the ability to discover mobile iOS devices with a technique similar to WoL.

So by sending a modified WoL packet to a mobile iOS device it will reveal itself by responding. All this can be done from one machine, in one process.


Requirements
------------

- A mobile iOS device like an iPhone, iPad or iPod Touch running iOS 5.0 and up
- iTunes Wifi Sync must be enabled in iOS
- The MAC address of the Wireless interface on the mobile iOS device
- Linux box connected to the same network as the iOS device
- Root privileges on the Linux box
- Linux box and mobile iOS devices connected to same network


Tested With
-----------

- iPhone 3GS, iPhone 4 and original iPad
- iOS version 5.x
- Linux, Debian 6.0


FAQ
---

Q: Does it work on Windows, OSX or BSD?
A: No, the daemon was written to work on the Linux packet filter system.

Q: Won't this WoL technique drain my mobile iOS battery?
A: If you keep a reasonable WoL interval of 300 seconds it shouldn't pose a problem since iOS itself frequently wakes up to talk to Apple's server.

Q: Does this work with other phones, Android based?
A: No, but a tracking daemon should be a lot easier to implement for Android devices.


Licensing
---------

Snoop is licensed under the terms of the MIT license, see attached LICENSE file for more details.


[0]: http://en.wikipedia.org/wiki/Sleep_Proxy_Service "Bonjour Sleep Proxy on Wikipedia"
[1]: http://tornadoweb.org "Tornado"
[2]: http://www.opensource.org/licenses/MIT "MIT License Details"
