#!/bin/sh
export bkp="{{ lookup('ini', 'systemdb_backup_path section=SAP file={{ ansible_env.HOME }}/.config/sap_config.ini') }}"
. /hana/shared/SS2/HDB00/hdbenv.sh
HDBSettings.sh recoverSys.py --command="RECOVER DATA USING FILE ('$bkp') CLEAR LOG" --wait --timeout=600