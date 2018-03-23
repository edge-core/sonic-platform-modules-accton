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
#    3/23/2018: Roy Lee modify for as7326_56x
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
    from as7326_56x.fanutil import FanUtil
    from as7326_56x.thermalutil import ThermalUtil
except ImportError as e:
    raise ImportError('%s - required module not found' % str(e))

# Deafults
VERSION = '1.0'
FUNCTION_NAME = 'accton_as7326_monitor'

global log_file
global log_level

#   (LM75_1+ LM75_2+ LM75_3) is LM75 at i2c addresses 0x48, 0x49, and 0x4A.
#   TMP = (LM75_1+ LM75_2+ LM75_3)/3
#1. If TMP < 35, All fans run with duty 31.25%.
#2. If TMP>=35 or the temperature of any one of fan is higher than 40,
#   All fans run with duty 50%
#3. If TMP >= 40 or the temperature of any one of fan is higher than 45,
#   All fans run with duty 62.5%.
#4. If TMP >= 45 or the temperature of any one of fan is higher than 50,
#   All fans run with duty 100%.
#5. Any one of 6 fans is fault, set duty = 100%.
#6. Direction factor. If it is B2F direction, duty + 12%.

 # MISC:
 # 1.Check single LM75 before applied average.
 # 2.If no matched fan speed is found from the policy,
 #     use FAN_DUTY_CYCLE_MIN as default speed
 # Get current temperature
 # 4.Decision 3: Decide new fan speed depend on fan direction/current fan speed/temperature



     
# Make a class we can use to capture stdout and sterr in the log
class accton_as7326_monitor(object):
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
           0: [32, 0,      105000],
           1: [50, 105000, 120000],
           2: [63, 120000, 135000],
           3: [max_duty, 135000, sys.maxsize],
        }
        fan_policy_b2f = {
           0: [44, 0,      105000],
           1: [63, 105000, 120000],
           2: [75, 120000, 135000],
           3: [max_duty, 135000, sys.maxsize],
        }
        fan_policy_single = {
           0: 40000,
           1: 45000,
           2: 50000,
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
 
        fan_dir=fan.get_fan_dir(1)
        if fan_dir == 1:
            fan_policy = fan_policy_f2b
        else:
            fan_policy = fan_policy_b2f
       
        #Decide fan duty by if any of sensors > fan_policy_single. 
        new_duty_cycle = fan_policy[0][0]
        for x in range(thermal.get_idx_thermal_start(), thermal.get_num_thermals()+1):
            single_thm = thermal._get_thermal_node_val(x)
            for y in range(0, len(fan_policy_single)):
                if single_thm > fan_policy_single[y]:
                    if fan_policy[y+1][0] > new_duty_cycle:
                        new_duty_cycle = fan_policy[y+1][0]
                        logging.debug('INFO. Single thermal sensor %d with temp %d > %d , new_duty_cycle=%d', 
                                x, single_thm, fan_policy_single[y], new_duty_cycle)
	single_result = new_duty_cycle	


        #Find if current duty matched any of define duty. 
	#If not, set it to highest one.
        cur_duty_cycle = fan.get_fan_duty_cycle()       
        for x in range(0, len(fan_policy)):
            if cur_duty_cycle == fan_policy[x][0]:
                break
        if x == len(fan_policy) :
            fan.set_fan_duty_cycle(fan_policy[0][0])
            cur_duty_cycle = max_duty

        #Decide fan duty by if sum of sensors falls into any of fan_policy{}
        get_temp = thermal.get_thermal_temp()            
        new_duty_cycle = cur_duty_cycle
        for x in range(0, len(fan_policy)):
            y = len(fan_policy) - x -1 #checked from highest
            if get_temp > fan_policy[y][1] and get_temp < fan_policy[y][2] :
                new_duty_cycle= fan_policy[y][0]
                logging.debug('INFO. Sum of temp %d > %d , new_duty_cycle=%d', get_temp, fan_policy[y][1], new_duty_cycle)

	sum_result = new_duty_cycle
	if (sum_result>single_result): 
		new_duty_cycle = sum_result;
	else:
		new_duty_cycle = single_result

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

    monitor = accton_as7326_monitor(log_file, log_level)

    # Loop forever, doing something useful hopefully:
    while True:
        monitor.manage_fans()
        time.sleep(10)

if __name__ == '__main__':
    main(sys.argv[1:])
