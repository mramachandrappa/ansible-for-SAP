#!/bin/sh
hdbsql -i {{ db_sysnr }} -d SYSTEMDB -u SYSTEM -p {{ source_db_system_user_pass }} -I /tmp/user.sql
hdbuserstore -i SET backup {{ db_hostname }}:3{{ db_sysnr }}15 bkp_operator Initial1