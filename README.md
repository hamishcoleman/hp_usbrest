Tools to interact with HP USB Multifunction Printers.

Modern models of these printers appear to have a HTTP-over-USB server running
on them, so there needs to be a special tool to query this.

Tested on
    DeskJet 2130 series

channel.py:

Perform one transaction with the USB device.  First, read from stdin until EOF
and send that to the USB device, then keep reading from the USB device until
a timeout, writing any received data to stdout.

Usage:
    echo -e "GET /Scan/ScanCaps HTTP/1.1\n\n" |python3 ./channel.py
