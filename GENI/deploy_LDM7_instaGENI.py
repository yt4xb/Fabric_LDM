#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""@package deploy_LDM7
Copyright (C) 2018 University of Virginia. All rights reserved.

file      deploy_LDM7.py
author    Shawn Chen <sc7cq@virginia.edu>
version   1.0
date      Oct. 28, 2015

modifier  Yuanlong Tan <yt4xb@virginia.edu>
version   2.0
date      Oct. 22, 2018
LICENSE
This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the Free
Software Foundation; either version 2 of the License, or（at your option）
any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
more details at http://www.gnu.org/copyleft/gpl.html

brief     Installs and deploys LDM7 on the GENI testbed.
"""

import logging
import sys
from StringIO import StringIO
from fabric.api import env, run, cd, get, sudo, put
from fabric.context_managers import settings

logging.basicConfig()
paramiko_logger = logging.getLogger("paramiko.transport")
paramiko_logger.disabled = True

LDM_VER = 'ldm-6.13.6'
LDM_PACK_NAME = LDM_VER + '.tar.gz'
LDM_PACK_PATH = '~/Downloads/'
TC_RATE = 20 # Mbps
RTT = 1 # ms
SINGLE_BDP = TC_RATE * 1000 * RTT / 8 # bytes
RCV_NUM = 2 # number of receivers
LOSS_RATE = 0.01
IFACE_NAME = 'eth1'

def read_hosts():
    """
    Reads hosts IP from sys.stdin line by line, expecting one per line.
    Then appends the username to each IP address.
    """
    env.hosts = []
    for line in sys.stdin.readlines():
        host = line.strip()
        if host and not host.startswith("#"):
            host = 'yt4xb@' + host
            env.hosts.append(host)

def clear_home():
    """
    Clears the ldm user home directory, including the existing product queue.
    """
    with cd('/users/yt4xb'):
        run('sudo rm -rf *')

def upload_pack():
    """
    Uploads the LDM source code package onto the test node. Also uploads a
    LDM start script.
    """
    put(LDM_PACK_PATH + LDM_PACK_NAME, '/users/yt4xb', mode=0664)
    #put('~/Downloads/util/', '/users/yt4xb',
    #    mode=0664)
    #with cd('/users/yt4xb'):
    #    #run('chown yt4xb.yt4xb %s' % LDM_PACK_NAME)
    #    run('chmod +x util/run_ldm util/insert.sh util/cpu_mon.sh util/tc_mon.sh')
    #    #run('chown -R yt4xb.yt4xb util')

def init_dependecies():
    """
    Setting the VM environment.
    """
    with settings(sudo_user='yt4xb'):
	run('sudo apt-get update', quiet=True)
        run('sudo apt-get install -y libxml2-dev', quiet=True)
	run('sudo apt-get install -y libpng-dev', quiet=True)
	run('sudo apt-get install -y zlib1g-dev', quiet=True)
	run('sudo apt-get install -y pax', quiet=True)
	run('sudo apt-get install -y libyaml-dev', quiet=True)
	run('sudo apt-get install -y gcc', quiet=True)
	run('sudo apt-get install -y g++', quiet=True)
	#run('sudo apt-get install -y sysstat', quiet=True)
	run('sudo apt-get install -y ntp', quiet=True)
	run('sudo apt-get install -y autoconf', quiet=True)
	run('sudo apt-get install -y m4', quiet=True)
	run('sudo apt-get install -y automake make', quiet=True)
	run('sudo apt-get install -y gnuplot', quiet=True)

def install_pack():
    """
    Compiles and installs the LDM source code.
    """
    with settings(sudo_user='yt4xb'):
        with cd('/users/yt4xb'):
            run('gunzip -c %s | pax -r \'-s:/:/src/:\'' % LDM_PACK_NAME)
        #patch_linkspeed()
        #patch_frcv()
        with cd('/users/yt4xb/%s/src' % LDM_VER):
            run('make distclean', quiet=True)
            #run('find -exec touch \{\} \;', quiet=True)
            run('./configure --enable-port=38800 --with-multicast --with-debug\
                 --disable-root-actions CFLAGS=-g CXXFLAGS=-g > Configure.log 2>&1 && echo Configured')
            run('make install > Install.log 2>&1 && echo Installed')
            run('sudo make root-actions')


def init_config():
    """
    Configures the etc file and environment variables. Also sets up tc and
    routing table on the sender.
    """
    run('sudo service ntp start', quiet=True)
    #run('service iptables start', quiet=True)
    run('sudo sed -i -e \'s/*\/10/*\/1/g\' /etc/cron.d/sysstat', quiet=True)
    run('sudo rm /var/log/sa/*', quiet=True)
    run('sudo service cron start', quiet=True)
    run('sudo service sysstat start', quiet=True)
    iface = run('hostname -I | awk \'{print $2}\'')
    if iface == '10.10.1.1':
	put('~/Workspace/std_data/1h_std', '/home/cc', mode=0664)
	put('~/Workspace/std_data/NGRID', '/home/cc', mode=0664)
        config_str = ('MULTICAST ANY 224.0.0.1:38800 1 10.10.1.1\n'
                      'ALLOW ANY ^.*$\nEXEC \"insert.sh\"'
                      '\nEXEC \"cpu_mon.sh\"\nEXEC \"tc_mon.sh\"')
        run('sudo route add 224.0.0.1 dev %s' % IFACE_NAME, quiet=True)
        #with cd('/users/yt4xb'):
        #    run('git clone \
        #         https://github.com/shawnsschen/LDM6-LDM7-comparison.git',
        #         quiet=True)
        run('regutil -s 5G /queue/size', quiet=True)
    else:
	iface = run('hostname -I | awk \'{print $1}\'')
        config_str = 'RECEIVE ANY 172.17.3.12 ' + iface
        run('regutil -s 2G /queue/size', quiet=True)
        #patch_sysctl()
    fd = StringIO()
    get('/users/yt4xb/.bashrc', fd)
    content = fd.getvalue()
    if 'ulimit -c "unlimited"' in content:
        update_bashrc = True
    else:
        update_bashrc = False
    get('/users/yt4xb/.profile', fd)
    content = fd.getvalue()
    if 'export PATH=$PATH:$HOME/util' in content:
        update_profile = True
    else:
        update_profile = False
    with settings(sudo_user='yt4xb'):
        with cd('/users/yt4xb'):
            run('echo \'%s\' > etc/ldmd.conf' % config_str)
            if not update_bashrc:
                run('echo \'ulimit -c "unlimited"\' >> .bashrc')
            if not update_profile:
                run('echo \'export PATH=$PATH:$HOME/util\' >> .profile')
        run('regutil -s %s /hostname' % iface)
        #sudo('regutil -s 5G /queue/size')
        run('regutil -s 35000 /queue/slots')

def start_LDM():
    """
    Start LDM and writes log file to a specified location.
    """
    with settings(sudo_user='yt4xb'):
	run('ldmadmin mkqueue -f')        
	#run('ldmadmin restart -v')
	#run('ps aux | grep ldm')

def stop_LDM():
    """
    Stops running LDM.
    """
    with settings(sudo_user='ldm'), cd('/users/yt4xb'):
        run('ldmadmin stop')
	run('ldmadmin clean')
	run('ldmadmin delqueue')

def fetch_log():
    """
    Fetches the LDM log.
    """
    iface = run('hostname -I | awk \'{print $2}\'')
    with cd('/users/yt4xb/var/logs'):
        run('mv ldmd.log.1 %s.log' % iface)
    get('/users/yt4xb/var/logs/%s.log' % iface, '~/Workspace/LDM7-LOG')
    """
    if iface == '10.10.1.1':
        with settings(sudo_user='yt4xb'), cd('/users/yt4xb'):
            run('sudo sar -n DEV | grep %s > bandwidth.log' % IFACE_NAME)
            get('cpu_measure.log', '~/Workspace/LDM7-LOG/')
            get('bandwidth.log', '~/Workspace/LDM7-LOG/')
            get('tc_mon.log', '~/Workspace/LDM7-LOG/')
    """
def patch_linkspeed():
    """
    Patches the receiving side linkspeed.
    """
    with settings(sudo_user='yt4xb'), cd(
        '/users/yt4xb/%s/src/mcast_lib/vcmtp/VCMTPv3/receiver' % LDM_VER):
        sudo('sed -i -e \'s/linkspeed(20000000)/linkspeed(%s)/g\' \
             vcmtpRecvv3.cpp' % str(TC_RATE*1000*1000), quiet=True)

def patch_frcv():
    """
    Patches the frcv value.
    """
    with settings(sudo_user='yt4xb'), cd(
        '/users/yt4xb/%s/src/mcast_lib/vcmtp/VCMTPv3/receiver' % LDM_VER):
        sudo('sed -i -e \'s/Frcv 20/Frcv 5/g\' vcmtpRecvv3.cpp', quiet=True)

def patch_sysctl():
    """
    Patches the core mem size in sysctl config.
    """
    run('sysctl -w net.core.rmem_max=%s' % str(int(2*1000*1000*1000)))
    #run('sysctl -w net.core.wmem_max=%s' % str(1*1024*1024*1024))
    run('sysctl -w net.core.rmem_default=%s' % str(int(2*1000*1000*1000)))
    #run('sysctl -w net.core.wmem_default=%s' % str(1*1024*1024*1024))

def add_loss():
    """
    Adds loss in iptables.
    """
    run('iptables -A INPUT -i %s -m statistic --mode random \
        --probability %s -p udp -j DROP' % (IFACE_NAME, str(LOSS_RATE)))

def rm_loss():
    """
    Removes loss in iptables.
    """
    run('iptables -D INPUT -i %s -m statistic --mode random \
        --probability %s -p udp -j DROP' % (IFACE_NAME, str(LOSS_RATE)))

def deploy():
	clear_home()
	upload_pack()
	#init_dependecies()
	install_pack()
	init_config()
	#start_LDM()
