#!/usr/bin/env python3
'''
Routines to find the usb device and communicate via the channels
'''

import errno

import usb.core
import usb.util


def init(interface=0, alternate=0):
    dev = usb.core.find(idVendor=0x03f0, idProduct=0xe111)

    if dev is None:
        raise ValueError("MFD usb device not found")

    # dev.set_configuration()

    cfg = dev.get_active_configuration()
    intf = cfg[(interface, alternate)]

    return intf

def _ep_type(intf,type):
    ep = usb.util.find_descriptor(
        intf,
        custom_match = \
        lambda e: \
            usb.util.endpoint_direction(e.bEndpointAddress) == \
            type)

    assert ep is not None
    return ep

def ep_out(intf):
    return _ep_type(intf, usb.util.ENDPOINT_OUT)

def ep_in(intf):
    return _ep_type(intf, usb.util.ENDPOINT_IN)

if __name__ == "__main__":
    intf = init()

    from_usb = ep_in(intf)
    to_usb = ep_out(intf)

    from_pipe = open(0, 'rb')
    to_pipe = open(1, 'wb')

    # Assume stdin has just one request on it, so read it all in one go
    buf = from_pipe.read()

    nbytes = to_usb.write(buf)
    if nbytes != len(buf):
        raise ValueError("Short write to usb")

    # Assume that usb has a large amount of data, and try to read it all:

    while True:
        try:
            buf = from_usb.read(4096)
            if len(buf) == 0:
                raise Exception("Zero length data from usb")

            to_pipe.write(buf)
        except usb.core.USBError as e:
            if e.errno == errno.ETIMEDOUT:
                break
            else:
                raise e
