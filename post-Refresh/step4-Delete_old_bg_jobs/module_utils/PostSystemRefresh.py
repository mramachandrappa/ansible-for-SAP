# -*- coding: utf-8 -*-
from pyrfc import Connection
from configparser import ConfigParser
import os
from ansible.module_utils.PreSystemRefresh import PreSystemRefresh


class PostSystemRefresh(PreSystemRefresh):
    # for post refresh step3 and step11.
    def check_background_jobs(self):
        try:
            output = self.conn.call("TH_WPINFO")
        except Exception as e:
            return "Error while call Function Module: {}".format(e)

        wp_type = []
        for type in output['WPLIST']:
            wp_type.append(type['WP_TYP'])

        if 'BGD' in wp_type:
            return True
        else:
            return False

    # Change in Requirement.
    def import_sys_tables(self):
        try:
            self.conn.call("SXPG_COMMAND_EXECUTE", COMMANDNAME='ZTABIMP')
            return "Successfully Imported Quality System Tables"
        except Exception as e:
            return "Error while exporting system tables: {}".format(e)

    def del_old_bg_jobs(self, report, variant_name):
        try:
            self.conn.call("SUBST_START_REPORT_IN_BATCH", IV_JOBNAME=report, IV_REPNAME=report, IV_VARNAME=variant_name)
            return "Old Background jobs logs are successfully deleted."
        except Exception as e:
            return "Failed to delete Old Background job logs: {}".format(e)

    # Deletes outbound queues SMQ1 & SMQ2
    def del_outbound_queues(self, jobname, report, variant_name): #For SMQ1 and SMQ2

        desc = dict(
            MANDT=self.creds['client'],
            REPORT=report,
            VARIANT=variant_name
        )

        content = [{'SELNAME': 'TID', 'KIND': 'P', 'LOW': '*'},
                   {'SELNAME': 'PACKAGE', 'KIND': 'P', 'LOW': '10.000'},
                   {'SELNAME': 'DISPLAY', 'KIND': 'P', 'LOW': 'X'}]

        text = [{'MANDT': self.creds['client'], 'LANGU': 'EN', 'REPORT': report, 'VARIANT':variant_name, 'VTEXT': 'Delete all outbound Queues'}]

        screen = [{'DYNNR': '1000', 'KIND': 'P'}]

        if self.check_variant(report, variant_name) is False:
            try:
                self.create_variant(report, variant_name, desc, content, text, screen)
            except Exception as e:
                return "Failed to create variant {}: {}".format(variant_name, e)

        if self.check_variant(report, variant_name) is True:
            try:
                self.conn.call("SUBST_START_REPORT_IN_BATCH", IV_JOBNAME=jobname, IV_REPNAME=report, IV_VARNAME=variant_name)
                return "Deleted all Outbound Queues Successfully!"
            except Exception as e:
                return "Failed to delete Outbound Queues: {}".format(e)
        else:
            return "Failed to create variant {}".format(variant_name)

    def del_trc_queues_sm58(self):
        jobname = "DELTE_SM58_QUEUES"
        report = "RSARFCDL"
        variant_name= "ZDELSM58"

        desc = dict(
            MANDT=self.creds['client'],
            REPORT=report,
            VARIANT=variant_name
        )

        content = [{'SELNAME': 'TID', 'KIND': 'P', 'LOW': '*'},
                   {'SELNAME': 'SET_EXEC', 'KIND': 'P', 'LOW': 'X'}]

        text = [{'MANDT': self.creds['client'], 'LANGU': 'EN', 'REPORT': report, 'VARIANT':variant_name, 'VTEXT': 'Delete all TRFC Queues'}]

        screen = [{'DYNNR': '1000', 'KIND': 'P'}]

        if self.check_variant(report, variant_name) is False:
            try:
                self.create_variant(report, variant_name, desc, content, text, screen)
            except Exception as e:
                return "Failed to create variant {}: {}".format(variant_name, e)

        if self.check_variant(report, variant_name) is True:
            try:
                self.conn.call("SUBST_START_REPORT_IN_BATCH", IV_JOBNAME=jobname, IV_REPNAME=report, IV_VARNAME=variant_name)
                return "Deleted all TRC Queues SM58"
            except Exception as e:
                return "Failed to delete Outbound Queues: {}".format(e)
        else:
            return "Failed to create variant {}".format(variant_name)

    # Testing - Phase
    def clean_ccms_data(self):
        try:
            self.conn.call("INST_EXECUTE_REPORT", PROGRAM='CSM_TAB_CLEAN')
            return "Successfully cleansed CCMS data"
        except Exception as e:
            return "Error while cleaning CCMS data: {}".format(e)

    # Testing - Phase
    def check_spool_consistency(self):
        try:
            output = self.conn.call("INST_EXECUTE_REPORT", PROGRAM='RSPO1043')
            # Needs to wait until report is executed successfully.
            return output
        except Exception as e:
            return "Error while checking_spool_consistency: {}".format(e)

    # Implementation phase
    def se06_post_copy_transport(self):
        pass


# Steps Completed in Post Refresh
# 1. Quality System User Lock           = Done
# 2. Suspend background jobs            = Done
# 3. Check background process           = Done
# 4. Import Quality System Tab          = Not Done  #FM not callable  (.ctl file to target sap server.)
# 5. Delete old background jobs         = Done
# 6. Delete outbound Queues SMQ1        = Done
# 7. Delete outbound Queues SMQ2        = Done
# 8. Delete TRC Queues SM58             = Done
# 9. Clean CCMS data                    = Testing phase
# 10. Check Spool Consistency           = Testing phase
# 11. Set background process to normal= Done
# 11. SE06 – Post copy transport process            = Not Done >            #SAP GUI
# 12. RDDNEWPP – RDDIMPDP background job execution  = Not Done >            #SAP GUI
# 13. User Master Import                            = Not Done >            #variants
# 14. Import all Printer output devices             = Not Done >            #SAP GUI
# 15. BDLS – Logical system conversion              = Not Done >            #variants
# 16. ZSCREEN_LOGIN_INFO - change                   = Not Done >            #variants
# 17. Quality System User Unlock                    = Testing Phase


