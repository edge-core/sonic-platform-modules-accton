#!/usr/bin/env python
#
# Copyright (C) 2016 Accton Networks, Inc.
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

"""
Usage: %(scriptName)s [options] command object

options:
    -h | --help     : this help message
    -d | --debug    : run with debug mode
    -f | --force    : ignore error during installation or clean
command:
    install     : install drivers and generate related sysfs nodes
    clean       : uninstall drivers and remove related sysfs nodes
    show        : show all systen status
    sff         : dump SFP eeprom
    set         : change board setting with fan|led|sfp
"""

import os
import commands
import sys, getopt
import logging
import re
import time
from collections import namedtuple

PROJECT_NAME = 'as7716_32x'
version = '0.0.1'
verbose = False
DEBUG = False
args = []
ALL_DEVICE = {}
DEVICE_NO = {'led':5, 'fan1':1, 'fan2':1,'fan3':1,'fan4':1,'fan5':1,'thermal':3, 'psu':2, 'sfp':54}


led_prefix ='/sys/devices/platform/as7716_32x_led/leds/accton_'+PROJECT_NAME+'_led::'
fan_prefix ='/sys/devices/platform/as7716_32x_'
hwmon_types = {'led': ['diag','fan','loc','psu1','psu2'],
               'fan1': ['fan'],
               'fan2': ['fan'],
               'fan3': ['fan'],
               'fan4': ['fan'],
               'fan5': ['fan'],
               'fan5': ['fan'],
              }
hwmon_nodes = {'led': ['brightness'] ,
               'fan1': ['fan_duty_cycle_percentage', 'fan1_fault', 'fan1_speed_rpm', 'fan1_direction', 'fanr1_fault', 'fanr1_speed_rpm'],
               'fan2': ['fan_duty_cycle_percentage','fan2_fault', 'fan2_speed_rpm', 'fan2_direction', 'fanr2_fault', 'fanr2_speed_rpm'],
               'fan3': ['fan_duty_cycle_percentage','fan3_fault', 'fan3_speed_rpm', 'fan3_direction', 'fanr3_fault', 'fanr3_speed_rpm'],
               'fan4': ['fan4_duty_cycle_percentage','fan4_fault', 'fan4_speed_rpm', 'fan4_direction', 'fanr4_fault', 'fanr4_speed_rpm'],
               'fan5': ['fan_duty_cycle_percentage','fan5_fault', 'fan5_speed_rpm', 'fan5_direction', 'fanr5_fault', 'fanr5_speed_rpm'],
	      }
hwmon_prefix ={'led': led_prefix,
               'fan1': fan_prefix,
               'fan2': fan_prefix,
               'fan3': fan_prefix,
               'fan4': fan_prefix,
               'fan5': fan_prefix,
              }

i2c_prefix = '/sys/bus/i2c/devices/'
i2c_bus = {'thermal': ['10-0048','10-0049', '10-004a'] ,
           'psu': ['17-0050','18-0053'],
           'sfp': ['-0050']}
i2c_nodes = {
           'thermal': ['hwmon/hwmon*/temp1_input'] ,
           'psu': ['psu_present ', 'psu_power_good']    ,
           'sfp': ['sfp_is_present ', 'sfp_tx_disable']}

sfp_map = [29, 30, 31, 32, 34, 33, 36, 35,
          25, 26, 27, 28, 37, 38, 39, 40, 
          41, 42, 43, 44, 53, 54, 55, 56, 
          45, 46, 47, 48, 49, 50, 51, 52]

mknod =[
'echo pca9548 0x77 > /sys/bus/i2c/devices/i2c-0/new_device',
'echo pca9548 0x76 > /sys/bus/i2c/devices/i2c-1/new_device',
'echo as7716_32x_fan 0x66 > /sys/bus/i2c/devices/i2c-9/new_device',

'echo lm75 0x48 > /sys/bus/i2c/devices/i2c-10/new_device',
'echo lm75 0x49 > /sys/bus/i2c/devices/i2c-10/new_device',
'echo lm75 0x4a > /sys/bus/i2c/devices/i2c-10/new_device',

'echo as7716_32x_cpld1 0x60 > /sys/bus/i2c/devices/i2c-11/new_device',
'echo accton_i2c_cpld 0x62 > /sys/bus/i2c/devices/i2c-12/new_device',
'echo accton_i2c_cpld 0x64 > /sys/bus/i2c/devices/i2c-13/new_device',

'echo pca9548 0x71 > /sys/bus/i2c/devices/i2c-2/new_device',
'echo pca9548 0x72 > /sys/bus/i2c/devices/i2c-2/new_device',
'echo pca9548 0x73 > /sys/bus/i2c/devices/i2c-2/new_device',
'echo pca9548 0x74 > /sys/bus/i2c/devices/i2c-2/new_device',
'echo pca9548 0x75 > /sys/bus/i2c/devices/i2c-2/new_device',

# PSU-1
'echo as7716_32x_psu1 0x53 > /sys/bus/i2c/devices/i2c-18/new_device',
'echo ym2651 0x5b > /sys/bus/i2c/devices/i2c-18/new_device',

# PSU-2
'echo as7716_32x_psu2 0x50> /sys/bus/i2c/devices/i2c-17/new_device',
'echo ym2651 0x58 > /sys/bus/i2c/devices/i2c-17/new_device',



#EERPOM
'echo 24c02 0x56 > /sys/bus/i2c/devices/i2c-1/new_device',
]

mknod2 =[
'echo as7716_32x_cpld1 0x60 > /sys/bus/i2c/devices/i2c-1/new_device',
'echo accton_i2c_cpld 0x61 > /sys/bus/i2c/devices/i2c-1/new_device',
'echo accton_i2c_cpld 0x62 > /sys/bus/i2c/devices/i2c-1/new_device',
'echo pca9548 0x70 > /sys/bus/i2c/devices/i2c-0/new_device',

# PSU-1
'echo as7716_32x_psu1 0x38 > /sys/bus/i2c/devices/i2c-57/new_device',
'echo cpr_4011_4mxx  0x3c > /sys/bus/i2c/devices/i2c-57/new_device',
'echo as7716_32x_psu1 0x50 > /sys/bus/i2c/devices/i2c-57/new_device',
'echo ym2401 0x58 > /sys/bus/i2c/devices/i2c-57/new_device',

# PSU-2
'echo as7716_32x_psu2 0x3b > /sys/bus/i2c/devices/i2c-58/new_device',
'echo cpr_4011_4mxx 0x3f > /sys/bus/i2c/devices/i2c-58/new_device',
'echo as7716_32x_psu2 0x53 > /sys/bus/i2c/devices/i2c-58/new_device',
'echo ym2401 0x5b > /sys/bus/i2c/devices/i2c-58/new_device',

'echo lm75 0x48 > /sys/bus/i2c/devices/i2c-61/new_device',
'echo lm75 0x49 > /sys/bus/i2c/devices/i2c-62/new_device',
'echo lm75 0x4a > /sys/bus/i2c/devices/i2c-63/new_device',

#EERPOM
'echo 24c02 0x57 > /sys/bus/i2c/devices/i2c-1/new_device',
]

FORCE = 0
logging.basicConfig(filename= PROJECT_NAME+'.log', filemode='w',level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)


if DEBUG == True:
    print sys.argv[0]
    print 'ARGV      :', sys.argv[1:]


def main():
    global DEBUG
    global args
    global FORCE

    if len(sys.argv)<2:
        show_help()

    options, args = getopt.getopt(sys.argv[1:], 'hdf', ['help',
                                                       'debug',
                                                       'force',
                                                          ])
    if DEBUG == True:
        print options
        print args
        print len(sys.argv)

    for opt, arg in options:
        if opt in ('-h', '--help'):
            show_help()
        elif opt in ('-d', '--debug'):
            DEBUG = True
            logging.basicConfig(level=logging.INFO)
        elif opt in ('-f', '--force'):
            FORCE = 1
        else:
            logging.info('no option')
    for arg in args:
        if arg == 'install':
           do_install()
        elif arg == 'clean':
           do_uninstall()
        elif arg == 'show':
           device_traversal()
        elif arg == 'sff':
            if len(args)!=2:
                show_eeprom_help()
            elif int(args[1]) ==0 or int(args[1]) > DEVICE_NO['sfp']:
                show_eeprom_help()
            else:
                show_eeprom(args[1])
            return
        elif arg == 'set':
            if len(args)<3:
                show_set_help()
            else:
                set_device(args[1:])
            return
        else:
            show_help()


    return 0

def show_help():
    print __doc__ % {'scriptName' : sys.argv[0].split("/")[-1]}
    sys.exit(0)

def  show_set_help():
    cmd =  sys.argv[0].split("/")[-1]+ " "  + args[0]
    print  cmd +" [led|sfp|fan]"
    print  "    use \""+ cmd + " led 0-4 \"  to set led color"
    print  "    use \""+ cmd + " fan 0-100\" to set fan duty percetage"
    print  "    use \""+ cmd + " sfp 1-32 {0|1}\" to set sfp# tx_disable"
    sys.exit(0)

def  show_eeprom_help():
    cmd =  sys.argv[0].split("/")[-1]+ " "  + args[0]
    print  "    use \""+ cmd + " 1-32 \" to dump sfp# eeprom"
    sys.exit(0)

def my_log(txt):
    if DEBUG == True:
        print "[ACCTON DBG]: "+txt
    return

def log_os_system(cmd, show):
    logging.info('Run :'+cmd)
    status = 1
    output = ""
    status, output = commands.getstatusoutput(cmd)
    my_log (cmd +"with result:" + str(status))
    my_log ("cmd:" + cmd)
    my_log ("      output:"+output)
    if status:
        logging.info('Failed :'+cmd)
        if show:
            print('Failed :'+cmd)
    return  status, output

def driver_inserted():
    ret, lsmod = log_os_system("lsmod| grep accton", 0)
    logging.info('mods:'+lsmod)
    if len(lsmod) ==0:
        return False

#'modprobe cpr_4011_4mxx',

kos = [
'depmod -ae',
'modprobe i2c_dev',
'modprobe i2c_mux_pca954x',
'modprobe accton_i2c_cpld',
'modprobe cpr_4011_4mxx',
'modprobe ym2651y',
'modprobe accton_as7716_32x_cpld1',
'modprobe accton_as7716_32x_fan',
'modprobe accton_as7716_32x_leds',
'modprobe accton_as7716_32x_psu']

def driver_install():
    global FORCE
    for i in range(0,len(kos)):
        status, output = log_os_system(kos[i], 1)
        if status:
            if FORCE == 0:
                return status
    return 0

def driver_uninstall():
    global FORCE
    for i in range(0,len(kos)):
        rm = kos[-(i+1)].replace("modprobe", "modprobe -rq")
        rm = rm.replace("insmod", "rmmod")
        status, output = log_os_system(rm, 1)
        if status:
            if FORCE == 0:
                return status
    return 0



def i2c_order_check():
    # i2c bus 0 and 1 might be installed in different order.
    # Here check if 0x76 is exist @ i2c-0
    tmp = "echo pca9548 0x70 > /sys/bus/i2c/devices/i2c-1/new_device"
    status, output = log_os_system(tmp, 0)
    if not device_exist():
        order = 1
    else:
        order = 0
    tmp = "echo 0x70 > /sys/bus/i2c/devices/i2c-1/delete_device"
    status, output = log_os_system(tmp, 0)
    return order

def device_install():
    global FORCE

    for i in range(0,len(mknod)):
        #for pca932x need times to built new i2c buses
        if mknod[i].find('pca954') != -1:
            time.sleep(2)
        
        status, output = log_os_system(mknod[i], 1)        
        if status:
            print output
            if FORCE == 0:
                return status
    
    for i in range(0,len(sfp_map)):
        status, output =log_os_system("echo optoe1 0x50 > /sys/bus/i2c/devices/i2c-"+str(sfp_map[i])+"/new_device", 1)
        if status:
            print output
            if FORCE == 0:
                return status
        status, output =log_os_system("echo port"+str(i)+" > /sys/bus/i2c/devices/"+str(sfp_map[i])+"-0050/port_name", 1)
        if status:
            print output
            if FORCE == 0:
                return status
    return

def device_uninstall():
    global FORCE

    status, output =log_os_system("ls /sys/bus/i2c/devices/0-0070", 0)
    if status==0:
        I2C_ORDER=1
    else:
    	I2C_ORDER=0

    for i in range(0,len(sfp_map)):
        target = "/sys/bus/i2c/devices/i2c-"+str(sfp_map[i])+"/delete_device"
        status, output =log_os_system("echo 0x50 > "+ target, 1)
        if status:
            print output
            if FORCE == 0:
                return status

    if I2C_ORDER==0:
        nodelist = mknod
    else:
        nodelist = mknod2

    for i in range(len(nodelist)):
        target = nodelist[-(i+1)]
        temp = target.split()
        del temp[1]
        temp[-1] = temp[-1].replace('new_device', 'delete_device')
        status, output = log_os_system(" ".join(temp), 1)
        if status:
            print output
            if FORCE == 0:
                return status

    return

def system_ready():
    if driver_inserted() == False:        
        return False
    if not device_exist():
        print "not device_exist()"
        return False
    return True

def do_install():
    if driver_inserted() == False:
        status = driver_install()
        if status:
            if FORCE == 0:
                return  status
    else:
        print PROJECT_NAME.upper()+" drivers detected...."
    if not device_exist():
        status = device_install()
        if status:
            if FORCE == 0:
                return  status
    else:
        print PROJECT_NAME.upper()+" devices detected...."
    return

def do_uninstall():
    if not device_exist():
        print PROJECT_NAME.upper() +" has no device installed...."
    else:
        print "Removing device...."
        status = device_uninstall()
        if status:
            if FORCE == 0:
                return  status

    if driver_inserted()== False :
        print PROJECT_NAME.upper() +" has no driver installed...."
    else:
        print "Removing installed driver...."
        status = driver_uninstall()
        if status:
            if FORCE == 0:
                return  status

    return

def devices_info():
    global DEVICE_NO
    global ALL_DEVICE
    global i2c_bus, hwmon_types
    for key in DEVICE_NO:
        ALL_DEVICE[key]= {}
        for i in range(0,DEVICE_NO[key]):
            ALL_DEVICE[key][key+str(i+1)] = []

    for key in i2c_bus:
        buses = i2c_bus[key]
        nodes = i2c_nodes[key]
        for i in range(0,len(buses)):
            for j in range(0,len(nodes)):
                if  'fan' == key:
                    for k in range(0,DEVICE_NO[key]):
                        node = key+str(k+1)
                        path = i2c_prefix+ buses[i]+"/fan"+str(k+1)+"_"+ nodes[j]
                        my_log(node+": "+ path)
                        ALL_DEVICE[key][node].append(path)
                elif  'sfp' == key:
                    for k in range(0,DEVICE_NO[key]):
                        node = key+str(k+1)
                        path = i2c_prefix+ str(sfp_map[k])+ buses[i]+"/"+ nodes[j]
                        my_log(node+": "+ path)
                        ALL_DEVICE[key][node].append(path)
                else:
                    node = key+str(i+1)
                    path = i2c_prefix+ buses[i]+"/"+ nodes[j]
                    my_log(node+": "+ path)
                    ALL_DEVICE[key][node].append(path)

    for key in hwmon_types:
        itypes = hwmon_types[key]
        nodes = hwmon_nodes[key]
        for i in range(0,len(itypes)):
            for j in range(0,len(nodes)):
                node = key+"_"+itypes[i]
                path = hwmon_prefix[key]+ itypes[i]+"/"+ nodes[j]
                my_log(node+": "+ path)
                ALL_DEVICE[key][ key+str(i+1)].append(path)

    #show dict all in the order
    if DEBUG == True:
        for i in sorted(ALL_DEVICE.keys()):
            print(i+": ")
            for j in sorted(ALL_DEVICE[i].keys()):
                print("   "+j)
                for k in (ALL_DEVICE[i][j]):
                    print("   "+"   "+k)
    return

def show_eeprom(index):
    if system_ready()==False:
        print("System's not ready.")
        print("Please install first!")
        return

    if len(ALL_DEVICE)==0:
        devices_info()
    node = ALL_DEVICE['sfp'] ['sfp'+str(index)][0]
    node = node.replace(node.split("/")[-1], 'sfp_eeprom')
    # check if got hexdump command in current environment
    ret, log = log_os_system("which hexdump", 0)
    ret, log2 = log_os_system("which busybox hexdump", 0)
    if len(log):
        hex_cmd = 'hexdump'
    elif len(log2):
        hex_cmd = ' busybox hexdump'
    else:
        log = 'Failed : no hexdump cmd!!'
        logging.info(log)
        print log
        return 1

    print node + ":"
    ret, log = log_os_system("cat "+node+"| "+hex_cmd+" -C", 1)
    if ret==0:
        print  log
    else:
        print "**********device no found**********"
    return

def set_device(args):
    global DEVICE_NO
    global ALL_DEVICE
    if system_ready()==False:
        print("System's not ready.")
        print("Please install first!")
        return

    if len(ALL_DEVICE)==0:
        devices_info()

    if args[0]=='led':
        if int(args[1])>4:
            show_set_help()
            return
        #print  ALL_DEVICE['led']
        for i in range(0,len(ALL_DEVICE['led'])):
            for k in (ALL_DEVICE['led']['led'+str(i+1)]):
                ret, log = log_os_system("echo "+args[1]+" >"+k, 1)
                if ret:
                    return ret
    elif args[0]=='fan':
        if int(args[1])>100:
            show_set_help()
            return
        #print  ALL_DEVICE['fan']
        #fan1~6 is all fine, all fan share same setting
        node = ALL_DEVICE['fan1'] ['fan11'][0]
        node = node.replace(node.split("/")[-1], 'fan1_duty_cycle_percentage')
        ret, log = log_os_system("cat "+ node, 1)
        if ret==0:
            print ("Previous fan duty: " + log.strip() +"%")
        ret, log = log_os_system("echo "+args[1]+" >"+node, 1)
        if ret==0:
            print ("Current fan duty: " + args[1] +"%")
        return ret
    elif args[0]=='sfp':
        if int(args[1])> DEVICE_NO[args[0]] or int(args[1])==0:
            show_set_help()
            return
        if len(args)<2:
            show_set_help()
            return

        if int(args[2])>1:
            show_set_help()
            return

        #print  ALL_DEVICE[args[0]]
        for i in range(0,len(ALL_DEVICE[args[0]])):
            for j in ALL_DEVICE[args[0]][args[0]+str(args[1])]:
                if j.find('tx_disable')!= -1:
                    ret, log = log_os_system("echo "+args[2]+" >"+ j, 1)
                    if ret:
                        return ret

    return

#get digits inside a string.
#Ex: 31 for "sfp31"
def get_value(input):
    digit = re.findall('\d+', input)
    return int(digit[0])

def device_traversal():
    if system_ready()==False:
        print("System's not ready.")
        print("Please install first!")
        return

    if len(ALL_DEVICE)==0:
        devices_info()
    for i in sorted(ALL_DEVICE.keys()):
        print("============================================")
        print(i.upper()+": ")
        print("============================================")

        for j in sorted(ALL_DEVICE[i].keys(), key=get_value):
            print "   "+j+":",
            for k in (ALL_DEVICE[i][j]):
                ret, log = log_os_system("cat "+k, 0)
                func = k.split("/")[-1].strip()
                func = re.sub(j+'_','',func,1)
                func = re.sub(i.lower()+'_','',func,1)
                if ret==0:
                    print func+"="+log+" ",
                else:
                    print func+"="+"X"+" ",
            print
            print("----------------------------------------------------------------")


        print
    return

def device_exist():
    ret1, log = log_os_system("ls "+i2c_prefix+"*0077", 0)
    ret2, log = log_os_system("ls "+i2c_prefix+"i2c-2", 0)
    return not(ret1 or ret2)

if __name__ == "__main__":
    main()
