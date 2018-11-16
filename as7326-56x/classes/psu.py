#!/usr/bin/env python
#
# Copyright (C) 2018 Accton Technology Corporation
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
#    7/2/2018:  Jostar create for as7326-56x
# ------------------------------------------------------------------

try:
    import time
    import logging
    import glob
    import commands
    from collections import namedtuple
except ImportError as e:
    raise ImportError('%s - required module not found' % str(e))


def log_os_system(cmd, show):
    logging.info('Run :'+cmd)
    status = 1
    output = ""
    status, output = commands.getstatusoutput(cmd)
    if show:
        print "ACC: " + str(cmd) + " , result:"+ str(status)
   
    if status:
        logging.info('Failed :'+cmd)
        if show:
            print('Failed :'+cmd)
    return  status, output


class ThermalUtil(object):
    """Platform-specific ThermalUtil class"""

    PSU_NUM_MAX = 2
    PSU_IDX_1 = 1 
    PSU_IDX_2 = 2
    
    PSU_1_BASE_PATH = '/sys/bus/i2c/devices/17-0051/'
    PSU_2_BASE_PATH = '/sys/bus/i2c/devices/13-0053/'

def main():
   print "Not use this file currently"

if __name__ == '__main__':
    main()
