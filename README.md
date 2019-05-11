A tool to interact with HP USB Multifunction Printers.

Modern models of these printers appear to have a HTTP-over-USB server
running on them, which is used as a REST service for allmost all
interactions with the printer and scanner.

While I could find other clients written to talk to this REST endpoint, none
of them were written to work with USB - they all expected to connect to a
normal HTTP-over-TCP server.

Tested on
    DeskJet 2130 series

channel.py:

Connect stdin and stdout to a USB device endpoint.  Bi-directional
communication will continue until there is a timeout.  There is no attempt
made to interpret the data to find the end of the conversation.

Usage:
    echo -e "GET /Scan/ScanCaps HTTP/1.1\n\n" |python3 ./channel.py

    socat -d -d TCP-LISTEN:8082,fork,max-children=1 "EXEC:python3 ./channel.py"
