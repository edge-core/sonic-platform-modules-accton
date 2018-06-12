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
#    11/13/2017: Polly Hsu, Create
#    1/10/2018: Jostar modify for as7716_32
#    6/12/2018: Roy Lee modify for as7816_64x
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
    from tabulate import tabulate
    from as7816_64x.fanutil import FanUtil
    from as7816_64x.thermalutil import ThermalUtil
except ImportError as e:
    raise ImportError('%s - required module not found' % str(e))

# Deafults
VERSION = '1.0'
FUNCTION_NAME = 'accton_as7816_monitor'

global log_file
global log_level

#* 1. If any FAN failed, set all the other fans as full speed (100%)
#* 2. When (0x48 + 0x49 + 0x4A + 0x4B + 0x4D + 0x4E)/6=T, T<= 43 C, set fan speed to 7 (52.9%)
#* 3. When (0x48 + 0x49 + 0x4A + 0x4B + 0x4D + 0x4E)/6=T, 43<T<= 46 C, set fan speed to 9 (64.7%)
#* 4. When (0x48 + 0x49 + 0x4A + 0x4B + 0x4D + 0x4E)/6=T, 46<T<= 52 C, set fan speed to B (76.5%)
#* 5. When (0x48 + 0x49 + 0x4A + 0x4B + 0x4D + 0x4E)/6=T, 52<T<= 57 C, set fan speed to D (88.2%)
#* 6. When (0x48 + 0x49 + 0x4A + 0x4B + 0x4D + 0x4E)/6=T, T>57 C, set fan speed to F (100%)
#* 7. The default FAN speed is 5 (41.2%)

     
# Make a class we can use to capture stdout and sterr in the log
class accton_as7816_monitor(object):
    # static temp var
    _ori_temp = 0
    _new_perc = 0
    _ori_perc = 0

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

    def manage_fans(self):
        max_duty = 100
        fan_policy_f2b = {
           0: [52, 0,      43000],
           1: [64, 43000,  46000],
           2: [76, 46000,  52000],
           3: [88, 52000,  57000],
           4: [max_duty, 57000, sys.maxsize],
        }
  
        thermal = ThermalUtil()
        fan = FanUtil()
        for x in range(fan.get_idx_fan_start(), fan.get_num_fans()+1):
            fan_status = fan.get_fan_status(x)
            if fan_status is None:
                logging.debug('INFO. SET new_perc to %d (FAN stauts is None. fan_num:%d)', max_duty, x)
                return False
            if fan_status is False:             
                logging.debug('INFO. SET new_perc to %d (FAN fault. fan_num:%d)', max_duty, x)
                fan.set_fan_duty_cycle(max_duty)
                return True
            #logging.debug('INFO. fan_status is True (fan_num:%d)', x)
 
        fan_policy = fan_policy_f2b
        cur_duty_cycle = fan.get_fan_duty_cycle()       

        #Decide fan duty by if average of sensors falls into any of fan_policy{}
        get_temp = thermal.get_thermal_temp()            
        new_duty_cycle = cur_duty_cycle
        for x in range(0, len(fan_policy)):
            y = len(fan_policy) - x -1 #checked from highest
            if get_temp > fan_policy[y][1] and get_temp < fan_policy[y][2] :
                new_duty_cycle= fan_policy[y][0]
                logging.debug('INFO. AVG. of temp %d > %d , new_duty_cycle=%d', get_temp, fan_policy[y][1], new_duty_cycle)

        logging.debug('INFO. Final duty_cycle=%d', new_duty_cycle)
        if(new_duty_cycle != cur_duty_cycle):
            fan.set_fan_duty_cycle(new_duty_cycle)
        return True

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

    monitor = accton_as7816_monitor(log_file, log_level)

    # Loop forever, doing something useful hopefully:
    while True:
        monitor.manage_fans()
        time.sleep(10)

if __name__ == '__main__':
    main(sys.argv[1:])
