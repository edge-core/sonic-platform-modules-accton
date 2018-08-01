#!/bin/bash
test_log=/usr/local/bin/check_mac_status.txt
modprobe i2c-dev
i2cset -y 0 0x77 0x1
i2cset -y 0 0x70 0x1
i2cget -y 0 0x54 0 b > /dev/null
if [ $? -ne 0 ];then
    printf "Device 8v89307(0x54) not found, MAC reset at CPLD directly\n"
    i2cset -y 0 0x77 0x1
    i2cset -y 0 0x71 0x2
    echo "Reset both MAC and PCI (write 0xD7)"
    i2cset -y 0 0x60 0x7 0xD7
    echo "Sleep 1s"
    sleep 1    
    echo "Pull back MAC reset, keep PCIE reset (write 0xF7)"
    i2cset -y 0 0x60 0x7 0xF7
    echo "Sleep 1s"
    sleep 1
    echo "Set to default normal state (write 0xFF)"
    i2cset -y 0 0x60 0x7 0xff 
    echo "remove PCI device"
    echo 1 > /sys/bus/pci/devices/0000:07:00.0/remove
    ls /sys/bus/pci/devices/
    echo "rescan PCI device"
    echo 1 > /sys/bus/pci/rescan
    ls /sys/bus/pci/devices/
    echo "Sleep 1s"
    sleep 1
    lspci -n|grep 07:00.0
    if [ $? -ne 0 ];then
        echo "Broadcom Corporation Device is not detect">>$test_log
        echo "rescan PCI again" >>$test_log
        echo 1 > /sys/bus/pci/rescan
        sleep 1
        lspci -n|grep 07:00.0
        if [ $? -ne 0 ];then
            echo "Broadcom Corporation Device NG">>$test_log
            echo "rescan PCI again-2" >>$test_log    
            echo 1 > /sys/bus/pci/rescan
            sleep 1
        else
            echo "done mac_pci_reset_rescan"
        fi
    fi
    exit 1

else

echo "idt init 1"
#Select to Page 0
i2cset -y 0 0x54 0x2D 0x00
i2cset -y 0 0x54 0x7F 0x05
i2cset -y 0 0x54 0x7E 0x85
i2cset -y 0 0x54 0x7B 0x00
i2cset -y 0 0x54 0x7A 0x00
i2cset -y 0 0x54 0x79 0x40
i2cset -y 0 0x54 0x78 0x06
i2cset -y 0 0x54 0x73 0x40
i2cset -y 0 0x54 0x72 0x40

# OUT3:25MHz
i2cset -y 0 0x54 0x71 0x0A 
i2cset -y 0 0x54 0x70 0x00

# OUT1:1pps
i2cset -y 0 0x54 0x6B 0x4E 
i2cset -y 0 0x54 0x69 0x00
i2cset -y 0 0x54 0x68 0x00
i2cset -y 0 0x54 0x67 0x19
i2cset -y 0 0x54 0x66 0xAB
i2cset -y 0 0x54 0x65 0x8C
i2cset -y 0 0x54 0x64 0x00
i2cset -y 0 0x54 0x63 0x00
i2cset -y 0 0x54 0x62 0x00
i2cset -y 0 0x54 0x5F 0x00
i2cset -y 0 0x54 0x5E 0x00
i2cset -y 0 0x54 0x5D 0x00
i2cset -y 0 0x54 0x5C 0x78
i2cset -y 0 0x54 0x5B 0x02
i2cset -y 0 0x54 0x5A 0xE5
i2cset -y 0 0x54 0x59 0x88
i2cset -y 0 0x54 0x58 0x4B
i2cset -y 0 0x54 0x57 0x6C
i2cset -y 0 0x54 0x56 0x6C

# Lock to DPLL, output 625MHz
i2cset -y 0 0x54 0x55 0x80 
i2cset -y 0 0x54 0x53 0x00
i2cset -y 0 0x54 0x52 0x81
i2cset -y 0 0x54 0x50 0x00
i2cset -y 0 0x54 0x4F 0x00
i2cset -y 0 0x54 0x4E 0x00
i2cset -y 0 0x54 0x4C 0xCB
i2cset -y 0 0x54 0x4A 0x00
i2cset -y 0 0x54 0x45 0x66
i2cset -y 0 0x54 0x44 0x66
i2cset -y 0 0x54 0x42 0x80
i2cset -y 0 0x54 0x41 0x03
i2cset -y 0 0x54 0x40 0x01
i2cset -y 0 0x54 0x3F 0x08
i2cset -y 0 0x54 0x3E 0x04
i2cset -y 0 0x54 0x3D 0x20
i2cset -y 0 0x54 0x3C 0x13
i2cset -y 0 0x54 0x3B 0x00
i2cset -y 0 0x54 0x3A 0x98
i2cset -y 0 0x54 0x39 0x01
i2cset -y 0 0x54 0x38 0xE6
i2cset -y 0 0x54 0x37 0x04
i2cset -y 0 0x54 0x36 0xCE
i2cset -y 0 0x54 0x35 0x7C
i2cset -y 0 0x54 0x34 0x01
i2cset -y 0 0x54 0x33 0x08
i2cset -y 0 0x54 0x32 0x08
i2cset -y 0 0x54 0x31 0x08
i2cset -y 0 0x54 0x30 0x03
i2cset -y 0 0x54 0x2F 0x23
i2cset -y 0 0x54 0x2E 0x0B
i2cset -y 0 0x54 0x2D 0x00
i2cset -y 0 0x54 0x28 0x76
i2cset -y 0 0x54 0x27 0x54
i2cset -y 0 0x54 0x25 0x00
i2cset -y 0 0x54 0x24 0x03
i2cset -y 0 0x54 0x23 0x06
i2cset -y 0 0x54 0x1A 0x8C
i2cset -y 0 0x54 0x19 0x8C
i2cset -y 0 0x54 0x18 0x00
i2cset -y 0 0x54 0x16 0x0D
i2cset -y 0 0x54 0x11 0x00
i2cset -y 0 0x54 0x10 0x00
i2cset -y 0 0x54 0x0E 0x3F
i2cset -y 0 0x54 0x0D 0xFF
i2cset -y 0 0x54 0x0C 0x02
i2cset -y 0 0x54 0x0B 0xA1
i2cset -y 0 0x54 0x0A 0x89
i2cset -y 0 0x54 0x09 0xA2
i2cset -y 0 0x54 0x08 0x32
i2cset -y 0 0x54 0x06 0x00
i2cset -y 0 0x54 0x05 0x00
i2cset -y 0 0x54 0x04 0x00
i2cset -y 0 0x54 0x03 0x00
i2cset -y 0 0x54 0x02 0x05
i2cset -y 0 0x54 0x01 0x33
i2cset -y 0 0x54 0x00 0x91

echo "idt init 2"
# PreDivider_Parameters
#IN1
i2cset -y 0 0x54 0x23 0x05 
i2cset -y 0 0x54 0x24 0x03
i2cset -y 0 0x54 0x25 0x00
#IN2
i2cset -y 0 0x54 0x23 0x06 
i2cset -y 0 0x54 0x24 0x03
i2cset -y 0 0x54 0x25 0x00
#IN3
i2cset -y 0 0x54 0x23 0x03 
i2cset -y 0 0x54 0x24 0x00
i2cset -y 0 0x54 0x25 0x00

echo "idt init 3"
# Page1_Parameters
#Select to Page 1
i2cset -y 0 0x54 0x2D 0x01
i2cset -y 0 0x54 0x30 0x03
i2cset -y 0 0x54 0x31 0x08
i2cset -y 0 0x54 0x32 0x08
i2cset -y 0 0x54 0x33 0x08
i2cset -y 0 0x54 0x35 0x7C
i2cset -y 0 0x54 0x36 0xCE
i2cset -y 0 0x54 0x37 0x04
i2cset -y 0 0x54 0x38 0xE6
i2cset -y 0 0x54 0x39 0x01
i2cset -y 0 0x54 0x3A 0x98
i2cset -y 0 0x54 0x3B 0x00
i2cset -y 0 0x54 0x3C 0x13
i2cset -y 0 0x54 0x3D 0x20
#Return to Page 0
i2cset -y 0 0x54 0x2D 0x00

echo "idt init 4"
#reset the in-path mux
i2cset -y 0 0x70 0x0
i2cset -y 0 0x77 0x0

#flip MAC reset at CPLD
echo "MAC reset at CPLD"
i2cset -y 0 0x77 0x1
i2cset -y 0 0x71 0x2
#i2cset -y 0 0x60 0x7 0xdf
#sleep 1

echo "Reset both MAC and PCI (write 0xD7)"
    i2cset -y 0 0x60 0x7 0xD7

    echo "Sleep 1s"
    sleep 1
    
    echo "Pull back MAC reset, keep PCIE reset (write 0xF7)"
    i2cset -y 0 0x60 0x7 0xF7

    echo "Sleep 1s"
    sleep 1

    echo "Set to default normal state (write 0xFF)"
    i2cset -y 0 0x60 0x7 0xff
    
 
    echo "remove PCI device"
    echo 1 > /sys/bus/pci/devices/0000:07:00.0/remove
    ls /sys/bus/pci/devices/
    echo "rescan PCI device"
    echo 1 > /sys/bus/pci/rescan
    ls /sys/bus/pci/devices/
    echo "Sleep 1s"
    sleep 1
    lspci -n|grep 07:00.0
    if [ $? -ne 0 ];then
        echo "Broadcom Corporation Device is not detect">>$test_log
        echo "rescan PCI again" >>$test_log
        echo 1 > /sys/bus/pci/rescan
        sleep 1
        lspci -n|grep 07:00.0
        if [ $? -ne 0 ];then
            echo "Broadcom Corporation Device NG">>$test_log
            echo "rescan PCI again-2" >>$test_log    
            echo 1 > /sys/bus/pci/rescan
            sleep 1
        else
            echo "done mac_pci_reset_rescan"
        fi
    fi
#i2cset -y 0 0x60 0x7 0xff
fi
