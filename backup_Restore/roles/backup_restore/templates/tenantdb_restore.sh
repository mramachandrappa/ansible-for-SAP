#!/bin/sh
export bkpi="{{ lookup('ini', 'tenantdb_backup_path section=SAP file={{ config_file_path }} ') }}"
. /hana/shared/{{ db_sid }}/HDB{{ db_sysnr }}/hdbenv.sh
hdbsql -U BACKUP "RECOVER DATA USING FILE ('$bkpi') CLEAR LOG" --wait --timeout=600