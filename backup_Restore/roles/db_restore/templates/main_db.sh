#!/bin/sh
ssh {{ remote_user }}@{{ db_hostname }} mkdir -p scripts
scp scripts/* {{ remote_user }}@{{ db_hostname }}:scripts/
ssh {{ remote_user }}@{{ db_hostname }} sudo -u {{ db_sid }}adm sh scripts/stop_db.sh
sleep 60
ssh {{ remote_user }}@{{ db_hostname }} sudo -u {{ db_sid }}adm sh scripts/systemdb_restore.sh
sleep 60
ssh {{ remote_user }}@{{ db_hostname }} sudo -u {{ db_sid }}adm sh scripts/user_sql.sh
ssh {{ remote_user }}@{{ db_hostname }} sudo -u {{ db_sid }}adm sh scripts/tenantdb_restore.sh
sleep 120
ssh {{ remote_user }}@{{ db_hostname }} rm -rf scripts
