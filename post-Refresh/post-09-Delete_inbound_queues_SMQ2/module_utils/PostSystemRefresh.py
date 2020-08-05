#!/usr/bin/python
from ansible.module_utils.basic import *
from ansible.module_utils.PreSystemRefresh import PreSystemRefresh
import logging


class PostSystemRefresh(PreSystemRefresh):
    data = dict()
    err = str()

    def inst_execute_report(self, module, params):
        try:
            self.conn.call("INST_EXECUTE_REPORT", PROGRAM=params['PROGRAM'])
            if params['PROGRAM'] == 'BTCTRNS1':
                self.data["Success"] = "Background Jobs are Suspended!"
                logging.info("PROGRAM: BTCTRNS1 - Background Jobs are Suspended!")
            if params['PROGRAM'] == 'CSM_TAB_CLEAN':
                self.data["Success"] = "Cleaned CCMS data!"
                logging.info("PROGRAM: CSM_TAB_CLEAN - Cleaned CCMS data!")
            if params['PROGRAM'] == 'RSPO1043':
                self.data["Success"] = "Spool Consistency is being checked!"
                logging.info("PROGRAM: RSPO1043 - Spool Consistency is being checked!")
            module.exit_json(changed=True, meta=self.data)
        except Exception as e:
            if params['PROGRAM'] == 'BTCTRNS1':
                self.err = "Failed to Suspend Background Jobs!"
                logging.info("PROGRAM: BTCTRNS1 - Failed to Suspend Background Jobs!")
            if params['PROGRAM'] == 'CSM_TAB_CLEAN':
                self.err = "Failed to clean CCMS data"
                logging.info("PROGRAM: CSM_TAB_CLEAN - Failed to clean CCMS data!")
            if params['PROGRAM'] == 'RSPO1043':
                self.err = "Failed to check spool consistency"
                logging.info("PROGRAM: RSPO1043 - Failed to check spool consistency!")
            module.fail_json(msg=self.err, error=to_native(e), exception=traceback.format_exc())

    def check_bg_jobs(self, module):
        try:
            output = self.conn.call("TH_WPINFO")
        except Exception as e:
            self.err = "Error while calling Function Module TH_WPINFO"
            logging.error("Error while calling Function Module TH_WPINFO")
            module.fail_json(msg=self.err, Error=to_native(e), exception=traceback.format_exc())

        wp_type = []
        for type in output['WPLIST']:
            wp_type.append(type['WP_TYP'])

        if 'BGD' in wp_type:
            self.data['result'] = True
            logging.info("TH_WPINFO: BGD entry found!")
            module.exit_json(changed=True, meta=self.data)
        else:
            self.data['result'] = False
            logging.info("TH_WPINFO: No BGD entry found!")
            module.exit_json(changed=True, meta=self.data)

    def start_report_in_batch(self, module, params):
        try:
            self.conn.call("SUBST_START_REPORT_IN_BATCH", IV_JOBNAME=params['IV_JOBNAME'],
                           IV_REPNAME=params['IV_REPNAME'], IV_VARNAME=params['IV_VARNAME'])
            if params['IV_REPNAME'] == 'RSBTCDEL':
                self.data['Success'] = "Old Background jobs logs are successfully deleted!"
                logging.info("SUBST_START_REPORT_IN_BATCH(RSBTCDEL): Old Background jobs logs are successfully deleted!")
            if params['IV_REPNAME'] == 'RSTRFCQD':
                self.data['Success'] = "Successfully Deleted SMQ1 Outbound Queues!"
                logging.info("SUBST_START_REPORT_IN_BATCH(RSTRFCQD): Successfully Deleted SMQ1 Outbound Queues!")
            if params['IV_REPNAME'] == 'RSTRFCID':
                self.data['Success'] = "Successfully Deleted SMQ2 Outbound Queues!"
                logging.info("SUBST_START_REPORT_IN_BATCH(RSTRFCID): Successfully Deleted SMQ2 Outbound Queues!")
            if params['IV_REPNAME'] == 'RSARFCDL':
                self.data['Success'] = "Successfully Deleted SM58 TRC Queues!"
                logging.info("SUBST_START_REPORT_IN_BATCH(RSARFCDL): Successfully Deleted SM58 TRC Queues!")
            if params['IV_REPNAME'] == 'ZRSCLXCOP':
                self.data['Success'] = "Successfully Executed Reports in Batch for User Master Import!"
                logging.info("SUBST_START_REPORT_IN_BATCH(ZRSCLXCOP): Successfully Executed Reports in Batch for User Master Import!")
            if params['IV_REPNAME'] == 'RSPOXDEV':
                self.data['Success'] = "Printer devices are Successfully Imported!"
                logging.info("SUBST_START_REPORT_IN_BATCH(RSPOXDEV): Printer devices are Successfully Imported!")
            if params['IV_REPNAME'] == 'STC_SC_UI_BDLS':
                self.data['Success'] = "Successfully converted the logical system names of tables from production SID to quality!"
                logging.info("SUBST_START_REPORT_IN_BATCH(STC_SC_UI_BDLS): Successfully converted the logical system names of tables from production SID to quality!")
            module.exit_json(changed=True, meta=self.data)
        except Exception as e:
            if params['IV_REPNAME'] == 'RSBTCDEL':
                self.err = "Failed to delete Old Background job logs"
                logging.info("SUBST_START_REPORT_IN_BATCH(RSBTCDEL): Failed to delete Old Background job logs!")
            if params['IV_REPNAME'] == 'RSTRFCQD':
                self.err = "Failed to delete SMQ1 Outbound Queues"
                logging.info("SUBST_START_REPORT_IN_BATCH(RSTRFCQD): Failed to delete SMQ1 Outbound Queues!")
            if params['IV_REPNAME'] == 'RSTRFCID':
                self.err = "Failed to delete SMQ2 Outbound Queues"
                logging.info("SUBST_START_REPORT_IN_BATCH(RSTRFCID): Failed to delete SMQ2 Outbound Queues!")
            if params['IV_REPNAME'] == 'RSARFCDL':
                self.err = "Failed to delete SM58 TRC Queues"
                logging.info("SUBST_START_REPORT_IN_BATCH(RSARFCDL): Failed to delete SM58 TRC Queues!")
            if params['IV_REPNAME'] == 'ZRSCLXCOP':
                self.data['Success'] = "Failed to Execute Report in Batch for User Master Import!"
                logging.info("SUBST_START_REPORT_IN_BATCH(ZRSCLXCOP): Failed to Execute Report in Batch for User Master Import!")
            if params['IV_REPNAME'] == 'RSPOXDEV':
                self.data['Success'] = "Failed to Import Printer devices!"
                logging.info("SUBST_START_REPORT_IN_BATCH(RSPOXDEV): Failed to Import Printer devices!")
            if params['IV_REPNAME'] == 'STC_SC_UI_BDLS':
                self.data['Success'] = "Failed to convert the logical system names of tables from production SID to quality!"
                logging.info("SUBST_START_REPORT_IN_BATCH(STC_SC_UI_BDLS): Failed to convert the logical system names of tables from production SID to quality!")
                module.exit_json(changed=True, meta=self.data)
            module.fail_json(msg=self.err, Error=to_native(e), exception=traceback.format_exc())
