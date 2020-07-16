#!/bin/sh
export bkpi="{{ lookup('ini', 'tenantdb_backup_path section=SAP file={{ ansible_env.HOME }}/.config/sap_config.ini') }}"
. /hana/shared/SS2/HDB00/hdbenv.sh
hdbsql -U BACKUPSYS "RECOVER DATA USING FILE ('$bkpi') CLEAR LOG" --wait --timeout=600