#!/usr/bin/env python3
'''
Routines to find the usb device and communicate via the channels

TODO
- implement a timeout for either direction in the main function, not just a
  usb receive timeout.
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


def _ep_type(intf, type):
    ep = usb.util.find_descriptor(
        intf,
        custom_match=lambda e:
            usb.util.endpoint_direction(e.bEndpointAddress) == type)

    assert ep is not None
    return ep


def ep_out(intf):
    return _ep_type(intf, usb.util.ENDPOINT_OUT)


def ep_in(intf):
    return _ep_type(intf, usb.util.ENDPOINT_IN)


if __name__ == "__main__":
    import argparse
    import select

    BUFSIZE = 2048

    a = argparse.ArgumentParser('USB channel stdin -> TX, RX -> stdout')
    a.add_argument('-i', '--interface', action='store', default=0, type=int)
    a.add_argument('-t', '--timeout', action='store', default=200, type=int)
    args = a.parse_args()

    intf = init(interface=args.interface)

    from_usb = ep_in(intf)
    to_usb = ep_out(intf)

    from_pipe = open(0, 'rb', buffering=0)
    to_pipe = open(1, 'wb', buffering=0)

    rsocks = [from_pipe]
    xsocks = [from_pipe, to_pipe]

    usb_timeouts = 0

    while True:
        (rlist, _, xlist) = select.select(rsocks, [], xsocks, args.timeout/1000)

        if xlist:
            # one of our pipes is closed, bail out
            break

        if rlist:
            # only one rx socket, so no need to loop
            buf = from_pipe.read(BUFSIZE)

            nbytes = to_usb.write(buf)
            if nbytes != len(buf):
                raise ValueError("Short write to usb")

        try:
            buf = from_usb.read(BUFSIZE, timeout=args.timeout)
            if buf:
                to_pipe.write(buf)


        except usb.core.USBError as e:
            if e.errno == errno.ETIMEDOUT:
                usb_timeouts += 1
                if usb_timeouts > 5:
                    # I think this request might be done ..
                    break

                continue
            else:
                raise e
