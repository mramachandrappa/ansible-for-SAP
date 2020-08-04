#!/bin/sh
export bkpi="{{ lookup('ini', 'tenantdb_backup_path section=SAP file={{ config_file_path }} ') }}"
. /hana/shared/SS2/HDB00/hdbenv.sh
hdbsql -U BACKUPSYS "RECOVER DATA USING FILE ('$bkpi') CLEAR LOG" --wait --timeout=600