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
#    3/23/2018: Roy Lee modify for as7326_56x
#    6/26/2018: Jostar implement by new thermal policy from HW RD
# ------------------------------------------------------------------

try:
    import os
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

    THERMAL_NUM_MAX = 6
    THERMAL_NUM_1_IDX = 1 # 1_ON_MAIN_BROAD. LM75
    THERMAL_NUM_2_IDX = 2 # 2_ON_MAIN_BROAD. LM75
    THERMAL_NUM_3_IDX = 3 # 3_ON_MAIN_BROAD. LM75
    THERMAL_NUM_4_IDX = 4 # CPU board. LM75
    THERMAL_NUM_5_IDX = 5 # CPU core thermal
    THERMAL_NUM_6_IDX = 6 # BCM thermal
    
    BCM_thermal_cmd = 'bcmcmd "show temp" > /tmp/bcm_thermal'
    BCM_thermal_path = '/tmp/bcm_thermal'
    #BCM_thermal_path = '/tmp/bcm_debug'
    """ Dictionary where
        key1 = thermal id index (integer) starting from 1
        value = path to fan device file (string) """
    #_thermal_to_device_path_mapping = {}

    _thermal_to_device_node_mapping = {
            THERMAL_NUM_1_IDX: ['15', '48'],
            THERMAL_NUM_2_IDX: ['15', '49'],
            THERMAL_NUM_3_IDX: ['15', '4a'],
            THERMAL_NUM_4_IDX: ['15', '4b'],
           }
    thermal_sysfspath ={
    THERMAL_NUM_1_IDX: ["/sys/bus/i2c/drivers/lm75/15-0048/hwmon/hwmon2/temp1_input"],
    THERMAL_NUM_2_IDX: ["/sys/bus/i2c/drivers/lm75/15-0049/hwmon/hwmon3/temp1_input"],  
    THERMAL_NUM_3_IDX: ["/sys/bus/i2c/drivers/lm75/15-004a/hwmon/hwmon4/temp1_input"],
    THERMAL_NUM_4_IDX: ["/sys/bus/i2c/drivers/lm75/15-004b/hwmon/hwmon5/temp1_input"],        
    THERMAL_NUM_5_IDX: ["/sys/class/hwmon/hwmon0/temp1_input"],     
    }

    #def __init__(self):
       
    def _get_thermal_val(self, thermal_num):
        if thermal_num < self.THERMAL_NUM_1_IDX or thermal_num > self.THERMAL_NUM_MAX:
            logging.debug('GET. Parameter error. thermal_num, %d', thermal_num)
            return None
       
        if thermal_num < self.THERMAL_NUM_6_IDX:
            device_path = self.get_thermal_to_device_path(thermal_num)
            if(os.path.isfile(device_path)):                
                for filename in glob.glob(device_path):
                    try:
                        val_file = open(filename, 'r')
                    except IOError as e:
                        logging.error('GET. unable to open file: %s', str(e))
                        return None
                content = val_file.readline().rstrip()
                if content == '':
                    logging.debug('GET. content is NULL. device_path:%s', device_path)
                    return None
                try:
		            val_file.close()
                except:
                    logging.debug('GET. unable to close file. device_path:%s', device_path)
                    return None      
                return int(content)
            
            else:
                print "No such device_path=%s"%device_path
                return 0
            
        else:
            log_os_system(self.BCM_thermal_cmd,0)
            file_path = self.BCM_thermal_path
            check_file = open(file_path)
            try:
                check_file = open(file_path)
            except IOError as e:
                print "Error: unable to open file: %s" % str(e) 
                return 0  
            file_str = check_file.read()
            search_str="average current temperature is"
            print "file_str.find=%s"%file_str.find(search_str)
            str_len = len(search_str)
            idx=file_str.find(search_str)
            if idx==-1:
                print "bcm sdk is not ready ,retrun 0"
                return 0
            else:               
                #print "file_str[idx]=%c"%file_str[idx+str_len+1]
                #print "file_str[idx]=%c"%file_str[idx+str_len+2]
                #print "file_str[idx]=%c"%file_str[idx+str_len+2+1]
                #print "file_str[idx]=%c"%file_str[idx+str_len+2+2]
                #print "file_str[idx]=%c"%file_str[idx+str_len+2+3]
                #print "file_str[idx]=%c"%file_str[idx+str_len+2+4]
                #print "file_str[idx]=%c"%file_str[idx+str_len+2+5]
                #print "file_str[idx]=%c"%file_str[idx+str_len+2+6]
                temp_str=file_str[idx+str_len+1] + file_str[idx+str_len+2] + file_str[idx+str_len+3]+file_str[idx+str_len+4] +file_str[idx+str_len+5]
                print "bcm temp_str=%s"%temp_str
                check_file.close()                 
                return float(temp_str)*1000
 
    def get_num_thermals(self):
        return self.THERMAL_NUM_MAX

    def get_idx_thermal_start(self):
        return self.THERMAL_NUM_1_IDX

    def get_size_node_map(self):
        return len(self._thermal_to_device_node_mapping)

    def get_size_path_map(self):
        return len(self.thermal_sysfspath)

    def get_thermal_to_device_path(self, thermal_num):
        return self.thermal_sysfspath[thermal_num][0]

    def get_thermal_1_val(self):      
        return self._get_thermal_node_val(self.THERMAL_NUM_1_IDX)

    def get_thermal_2_val(self):
        return self._get_thermal_node_val(self.THERMAL_NUM_2_IDX)
    def get_thermal_temp(self):
        return (self._get_thermal_node_val(self.THERMAL_NUM_1_IDX) + self._get_thermal_node_val(self.THERMAL_NUM_2_IDX) +self._get_thermal_node_val(self.THERMAL_NUM_3_IDX))

def main():
    thermal = ThermalUtil()
    print "termal1=%d" %thermal._get_thermal_val(1)
    print "termal2=%d" %thermal._get_thermal_val(2)
    print "termal3=%d" %thermal._get_thermal_val(3)
    print "termal4=%d" %thermal._get_thermal_val(4)
    print "termal5=%d" %thermal._get_thermal_val(5)
    print "termal6=%d" %thermal._get_thermal_val(6)
#
#    print 'get_size_node_map : %d' % thermal.get_size_node_map()
#    print 'get_size_path_map : %d' % thermal.get_size_path_map()
#    for x in range(thermal.get_idx_thermal_start(), thermal.get_num_thermals()+1):
#        print thermal.get_thermal_to_device_path(x)
#
if __name__ == '__main__':
    main()
