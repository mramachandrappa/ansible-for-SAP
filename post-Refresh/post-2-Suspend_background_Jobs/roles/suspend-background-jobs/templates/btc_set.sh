#!/bin/csh
stopsap r3
sleep 10
mv /usr/sap/{{ target_sap_sid }}/SYS/profile/{{ target_sap_sid }}_DVEBMGS{{ sysnr }}_{{ ashost }}.bak /usr/sap/{{ target_sap_sid }}/SYS/profile/{{ target_sap_sid }}_DVEBMGS{{ sysnr }}_{{ ashost }}
startsap r3