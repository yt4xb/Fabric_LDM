#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
Copyright (C) 2018 University of Virginia. All rights reserved.

file      IP_Ex.py
modifier  Yuanlong Tan <yt4xb@virginia.edu>
version   1.0
date      Oct. 1, 2018
LICENSE
This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the Free
Software Foundation; either version 2 of the License, or（at your option）
any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
more details at http://www.gnu.org/copyleft/gpl.html

brief     Parses the Cloudlab RSpec and extracts control plane IP addresses.
"""

import re
import sys
targetIP = []
def parseIP(line):
    """Parses the input xml file and finds the control plane IP.

    Args:
        line: A line of the raw xml file.

    Returns:
        ip:     The IP address found.
        -1:     Indicates invalid IP or none found.
    """
    match = re.search(r'ipv4=\"(.*)\"', line)
    if match:
        name = match.group(1)
        return name
    else:
        return -1

def main(response):
    """Reads the XML response and parses the IP addresses.

    Args:
        xmlfile : Filename of the XML response.
    """
    with open(response, 'r') as xmlfile:
        for i, line in enumerate(xmlfile):
            ip = parseIP(line)
            if ip != -1:
                targetIP.append(ip)
                print ip
    xmlfile.close()
    with open(sys.argv[1]+".list", 'w') as dn:
        for i in targetIP:
            dn.write(i)
            dn.write('\n')
    dn.close

if __name__ == "__main__":
    main(sys.argv[1])
