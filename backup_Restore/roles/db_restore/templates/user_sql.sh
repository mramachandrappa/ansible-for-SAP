#!/bin/sh
. /hana/shared/{{ db_sid }}/HDB{{ db_sysnr }}/hdbenv.sh
hdbsql -i {{ db_sysnr }} -d SYSTEMDB -u SYSTEM -p {{ source_db_systemuser_passwd }} -I user.sql
hdbuserstore -i SET backup {{ db_hostname }}:3{{ db_sysnr }}13 BKP_OPERATOR Initial1
sleep 10