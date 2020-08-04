#!/bin/sh
. /hana/shared/{{ db_sid }}/HDB{{ db_sysnr }}/hdbenv.sh
hdbuserstore SET DEFAULT {{ db_hostname }}:3{{ db_sysnr }}15 SAPABAP1 {{ source_schema_passwd }}
