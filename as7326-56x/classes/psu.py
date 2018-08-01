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

    BASE_VAL_PATH = '/sys/bus/i2c/devices/{0}-00{1}/hwmon/hwmon*/temp1_input'
    CPU_thermal_PATH = "/sys/class/hwmon/hwmon0/temp1_input"
    BCM_thermal_cmd = 'bcmcmd "show temp" > /tmp/bcm_thermal'
    BCM_thermal_path = '/tmp/bcm_thermal'
    """ Dictionary where
        key1 = thermal id index (integer) starting from 1
        value = path to fan device file (string) """
    _thermal_to_device_path_mapping = {}

    _thermal_to_device_node_mapping = {
            THERMAL_NUM_1_IDX: ['15', '48'],
            THERMAL_NUM_2_IDX: ['15', '49'],
            THERMAL_NUM_3_IDX: ['15', '4a'],
            THERMAL_NUM_4_IDX: ['15', '4b'],
           }

    def __init__(self):
        thermal_path = self.BASE_VAL_PATH

        for x in range(self.THERMAL_NUM_1_IDX, self.THERMAL_NUM_4_IDX+1):
            self._thermal_to_device_path_mapping[x] = thermal_path.format(
                self._thermal_to_device_node_mapping[x][0],
                self._thermal_to_device_node_mapping[x][1])
            #print "x=%d"%x
            #print "_thermal_to_device_path_mapping=%s"%self._thermal_to_device_path_mapping[x]
        self._thermal_to_device_path_mapping[self.THERMAL_NUM_5_IDX] =  self.CPU_thermal_PATH
        #print "_thermal_to_device_path_mapping=%s"%self._thermal_to_device_path_mapping[self.THERMAL_NUM_5_IDX]
            
    def _get_thermal_val(self, thermal_num):
        if thermal_num < self.THERMAL_NUM_1_IDX or thermal_num > self.THERMAL_NUM_MAX:
            logging.debug('GET. Parameter error. thermal_num, %d', thermal_num)
            return None
        if thermal_num < self.THERMAL_NUM_6_IDX:
            device_path = self.get_thermal_to_device_path(thermal_num)
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
            #print "file_str[idx]=%c"%file_str[idx+str_len+2]
            #print "file_str[idx]=%c"%file_str[idx+str_len+2+1]
            #print "file_str[idx]=%c"%file_str[idx+str_len+2+2]
            #print "file_str[idx]=%c"%file_str[idx+str_len+2+3]
            #print "file_str[idx]=%c"%file_str[idx+str_len+2+4]
            #print "file_str[idx]=%c"%file_str[idx+str_len+2+5]
            #print "file_str[idx]=%c"%file_str[idx+str_len+2+6]
            temp_str= file_str[idx+str_len+2] + file_str[idx+str_len+3]+file_str[idx+str_len+4] +file_str[idx+str_len+5]
            print "temp_str=%s"%temp_str
            check_file.close() 
            return float(temp_str)*1000
 
    def get_num_thermals(self):
        return self.THERMAL_NUM_MAX

    def get_idx_thermal_start(self):
        return self.THERMAL_NUM_1_IDX

    def get_size_node_map(self):
        return len(self._thermal_to_device_node_mapping)

    def get_size_path_map(self):
        return len(self._thermal_to_device_path_mapping)

    def get_thermal_to_device_path(self, thermal_num):
        return self._thermal_to_device_path_mapping[thermal_num]

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
