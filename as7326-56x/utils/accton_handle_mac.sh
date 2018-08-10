#!/bin/bash

if [ -s /usr/local/bin/done_mac_reset ];then
    echo "There is a done_mac_reset file"
else
    
    cat /etc/init.d/opennsl-modules-3.16.0-5-amd64|grep mac_reset.sh
    if [ $? -ne 0 ];then
        echo "Add mac_reset.sh"
        echo "Add mac_reset to opennsl-modules for TD3 MAC"
        sed -i '/modprobe linux-kernel-bde/i     sleep 1' /etc/init.d/opennsl-modules-3.16.0-5-amd64
        sed -i '/sleep/i /usr/local/bin/mac_reset.sh' /etc/init.d/opennsl-modules-3.16.0-5-amd64
        sed -i '/mac_reset/i echo "MAC reset" ' /etc/init.d/opennsl-modules-3.16.0-5-amd64
        sed -i '/MAC reset/i echo 1 > /usr/local/bin/done_mac_reset'  /etc/init.d/opennsl-modules-3.16.0-5-amd64

    fi

fi


