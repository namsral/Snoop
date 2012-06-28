#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Standard modules
import sys, os, traceback
from optparse import OptionParser
import logging
import functools
import socket
from struct import *
import datetime
from urllib import urlencode

# 3rd party modules
from tornado import ioloop, options, httpclient

# Network packet vars
ETH_P_ARP = 0x0806
ETH_P_WOL = 0x0842
ARP_PROTOCOL = 1544


def eth_addr(a):
  b = "%.2x:%.2x:%.2x:%.2x:%.2x:%.2x" % (
    ord(a[0]),
    ord(a[1]),
    ord(a[2]),
    ord(a[3]),
    ord(a[4]),
    ord(a[5])
  )
  return b


def http_callback(target, url):
    # Prepare the data
    data = {
        'mac_address':target,
        'date': datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        }
    body = urlencode(data)

    # Setup and make the call
    http_client = httpclient.AsyncHTTPClient()
    http_client.fetch(url, on_http_callback, method='POST',
        headers=None, body=body)


def on_http_callback(response):
    if response.error:
        logging.error('Error: Callback failed, server responded with HTTP {0}'.format(response.error))


def WakeUpiOSDevice(target, interface):
    logging.debug('Sending WoL packet to {0}'.format(target))

    if ':' in target:
        target = target.replace(':', '')
    target = target.lower()

    sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(ETH_P_WOL))
    
    sock.bind((interface, ETH_P_WOL))
    src_address = sock.getsockname()[4]

    target_address = target.decode('hex')
    package = ''.join([target_address, src_address, '\x08\x42\xff\xff\xff\xff\xff\xff'] + 
        [target_address] * 16 + ['\x00\x00\x00\x00\x00\x00'])

    sock.send(package)
    sock.close()


def signal_devices(devices):
    for target in devices:
        WakeUpiOSDevice(target, INTERFACE)


def handle_packet(sock, fd, events):

    packet = sock.recvfrom(65565)
    packet = packet[0]

    eth_header = packet[:14]
    eth = unpack('!6s6sH' , eth_header)
    eth_protocol = socket.ntohs(eth[2])

    src_address = eth_addr(packet[6:12])
    dest_address = eth_addr(packet[0:6])
    local_address = eth_addr(sock.getsockname()[4])

    if ARP_PROTOCOL == eth_protocol and src_address in TARGETS and local_address == dest_address:
        logging.info('Found matching MAC address {0}'.format(src_address))
        if CALLBACK:
            logging.debug('Attempt to call callback: {0}'.format(CALLBACK))
            http_callback(src_address, CALLBACK)
    else:
        logging.debug('Ignoring packet from {0}'.format(src_address))


def main():
    global INTERFACE, TARGETS, INTERVAL, CALLBACK, io_loop

    # Register command line options
    options.define('config', default='/etc/torpedo/torpedo.conf', help='Path to config file')
    options.define('targets',
        help='Devices to targets, list of MAC addresses seperated by comma\'s.')
    options.define('interface', default='eth0', type=int,
        help='Network interface to bind to')
    options.define('callback_url',
        help='URL to callback when a device is found.')
    options.define('wol_interval', default=300, 
        help='Interval to send out WoL packets. Defined in seconds')
    options.parse_command_line()

    # Read config
    CONFIG = options.options.config
    if os.access(CONFIG, 4):
        options.parse_config_file(CONFIG)

    # Clean targets
    targets = []
    if options.options.targets:
        s = options.options.targets
        # targets = [i.strip() for i in s.split(',')]
        targets = [i.strip() for i in s.split(',')]
    
    # Make options global
    TARGETS = targets
    INTERFACE = options.options.interface
    INTERVAL = options.options.wol_interval * 1000
    CALLBACK = options.options.callback_url

    # Establish the Tornado loop
    io_loop = ioloop.IOLoop.instance()

    try:
        # Attach to network interface and caputer traffic
        sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(ETH_P_ARP))
        sock.setblocking(0)
        sock.bind((INTERFACE, ETH_P_ARP))
        callback = functools.partial(handle_packet, sock)
        io_loop.add_handler(sock.fileno(), callback, io_loop.READ)

        # Setup a schedule to send WoL packets
        callback = functools.partial(signal_devices, TARGETS)
        scheduler = ioloop.PeriodicCallback(callback, INTERVAL, io_loop=io_loop)
        scheduler.start()
    except socket.error, e:
        print "Error: No permission to bind to the network interface.\n\n"
        sys.exit(1)

    # Start Tornado
    try:
        io_loop.start()
        logging.log("Snoop started.")
    except KeyboardInterrupt:
        io_loop.stop()
        print "Snoop stopped."

if __name__ == "__main__":
    main()
