#!/usr/bin/env python
#
# Copyright (C) 2017 Accton Technology Corporation
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# ------------------------------------------------------------------
# HISTORY:
#    mm/dd/yyyy (A.D.)
#    5/10/2018: Jostar Yang, Create
#
# ------------------------------------------------------------------

try:
    import os
    import sys, getopt
    import subprocess
    import click
    import imp
    import logging
    import logging.config
    import types
    import time  # this is only being used as part of the example
    import traceback
    import commands
    from tabulate import tabulate   
except ImportError as e:
    raise ImportError('%s - required module not found' % str(e))

# Deafults
VERSION = '1.0'
FUNCTION_NAME = 'accton_drv_handler'

global log_file
global log_level
DEBUG = False

def my_log(txt):
    if DEBUG == True:
        print "[ACCTON DBG]: "+txt
    return

def log_os_system(cmd, show):
    logging.info('Run :'+cmd)
    status = 1
    output = ""
    status, output = commands.getstatusoutput(cmd)
    if DEBUG == True:
        my_log (cmd +" , result:" + str(status))
    else:
        if show:
            print "ACC: " + str(cmd) + " , result:"+ str(status)
    #my_log ("cmd:" + cmd)
    #my_log ("      output:"+output)
    if status:
        logging.info('Failed :'+cmd)
        if show:
            print('Failed :'+cmd)
    return  status, output

swss_check_cmd = "systemctl status swss.service -l > /tmp/swss_status"
# Make a class we can use to capture stdout and sterr in the log
class accton_drv_monitor(object):
   
    def __init__(self, log_file, log_level):
        """Needs a logger and a logger level."""
        # set up logging to file
        logging.basicConfig(
            filename=log_file,
            filemode='w',
            level=log_level,
            format= '[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )

        # set up logging to console
        if log_level == logging.DEBUG:
            console = logging.StreamHandler()
            console.setLevel(log_level)
            formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
            console.setFormatter(formatter)
            logging.getLogger('').addHandler(console)

        logging.debug('SET. logfile:%s / loglevel:%d', log_file, log_level)

    def cpld_reset_mac(self):
        #log_os_system("i2cset -f -y 0 0x77 0x1", 1)
        #log_os_system("i2cset -f -y 0 0x71 0x2", 1)
        #log_os_system("i2cset -f -y 0 0x60 0x7 0xdf", 1)
        log_os_system("i2cset -f -y 18 0x60 0x7 0xdf", 1)
        
        time.sleep(1)
        #ret, lsmod = log_os_system("i2cset -f -y 0 0x60 0x7 0xff", 1)
        log_os_system("i2cset -f -y 18 0x60 0x7 0xff", 1)
        return 1
    
    def monitor_swss(self):
        log_os_system(swss_check_cmd, 0)
        file_path = "/tmp/swss_status"
        print(file_path)
        check_file = open(file_path)
        try:
            check_file = open(file_path)
        except IOError as e:
            print "Error: unable to open file: %s" % str(e) 
    
        file_str = check_file.read() 
        id_filter = "Active: active"
        id_pos = file_str.find(id_filter)        
        check_file.close()
        if id_pos==-1:
            print "swss inactive,swss_id_pos=%d"%id_pos
            return 0
        else:
            print "swss actvie,swss_id_pos=%d"%id_pos            
            return 1
def main(argv):
    log_file = '%s.log' % FUNCTION_NAME
    log_level = logging.INFO
    if len(sys.argv) != 1:
        try:
            opts, args = getopt.getopt(argv,'hdl:',['lfile='])
        except getopt.GetoptError:
            print 'Usage: %s [-d] [-l <log_file>]' % sys.argv[0]
            return 0
        for opt, arg in opts:
            if opt == '-h':
                print 'Usage: %s [-d] [-l <log_file>]' % sys.argv[0]
                return 0
            elif opt in ('-d', '--debug'):
                log_level = logging.DEBUG
            elif opt in ('-l', '--lfile'):
                log_file = arg
    restart_swss = 0
    monitor = accton_drv_monitor(log_file, log_level)

    # Loop forever, doing something useful hopefully:
    while True:
        #monitor.manage_fans()
        if restart_swss==0:
            ret=monitor.monitor_swss()
            if ret==1:
                print "do stop swss,opennsl, reset mac, start opennsl, start swss"
                log_os_system("systemctl stop swss.service",1)
                log_os_system("systemctl stop opennsl-modules-3.16.0-5-amd64.service",1)
                #monitor.cpld_reset_mac()
                log_os_system("systemctl start opennsl-modules-3.16.0-5-amd64.service",1)
                log_os_system("systemctl start swss.service", 1)
                restart_swss=1
        else:
            print "restart_swss=1, so not need to check swss. Exit"
            return 1
        time.sleep(3)

if __name__ == '__main__':
    main(sys.argv[1:])
