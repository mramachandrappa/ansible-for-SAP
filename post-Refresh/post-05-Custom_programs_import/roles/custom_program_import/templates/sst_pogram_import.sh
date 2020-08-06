#!/bin/csh
tp addtobuffer PC3K900002 {{ target_sap_sid }} u1248 pf={{ bin_path }}/TP_DOMAIN_{{ target_sap_sid }}.PFL
tp addtobuffer PC3K900017 {{ target_sap_sid }} u1248 pf={{ bin_path }}/TP_DOMAIN_{{ target_sap_sid }}.PFL
sleep 10
tp import PC3K900002 {{ target_sap_sid }} CLIENT={{ client }} u1248 pf={{ bin_path }}/TP_DOMAIN_{{ target_sap_sid }}.PFL
tp import PC3K900017 {{ target_sap_sid }} CLIENT={{ client }} u1248 pf={{ bin_path }}/TP_DOMAIN_{{ target_sap_sid }}.PFL
sleep 20
