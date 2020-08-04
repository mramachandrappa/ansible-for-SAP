#!/bin/sh
export bkp="{{ lookup('ini', 'systemdb_backup_path section=SAP file={{ config_file_path }}') }}"
. /hana/shared/{{ db_sid }}/HDB{{ db_sysnr }}/hdbenv.sh
HDBSettings.sh recoverSys.py --command="RECOVER DATA USING FILE ('$bkp') CLEAR LOG" --wait --timeout=600