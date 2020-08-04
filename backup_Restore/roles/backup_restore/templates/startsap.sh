#!/bin/csh
stopsap r3
mv /usr/sap/{{ target_sap_sid }}/SYS/profile/{{ target_sap_sid }}_DVEBMGS{{ sysnr }}_{{ ashost }} /usr/sap/{{ target_sap_sid }}/SYS/profile/{{ target_sap_sid }}_DVEBMGS{{ sysnr }}_{{ ashost }}.bak
awk '/wp_no_btc/{sub($NF, 0)}1' /usr/sap/{{ target_sap_sid }}/SYS/profile/{{ target_sap_sid }}_DVEBMGS{{ sysnr }}_{{ ashost }}.bak > /usr/sap/{{ target_sap_sid }}/SYS/profile/{{ target_sap_sid }}_DVEBMGS{{ sysnr }}_{{ ashost }}
startsap r3