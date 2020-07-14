#!/usr/bin/python
# -*- coding: utf-8 -*-

from pyrfc import Connection
from configparser import ConfigParser
from ansible.module_utils.basic import *
import os
import logging


class PreSystemRefresh:
    data = dict()
    err = str()

    def __init__(self):
        self.config = ConfigParser()
        try:
            self.config.read(os.environ["HOME"] + '/.config/sap_config.ini')
            self.creds = self.config['SAP']

            logging.basicConfig(filename="/tmp/system_refresh.log", level=logging.INFO,
                                format='[%(asctime)s]: [%(levelname)s]: [%(message)s]')

            self.conn = Connection(user=self.creds['user'], passwd=self.creds['passwd'], ashost=self.creds['ashost'],
                                   sysnr=self.creds['sysnr'], sid=self.creds['sid'], client=self.creds['client'])
        except KeyError:
            self.config.read(os.path.expanduser('~') + '\.config\sap_config.ini')
            self.creds = self.config['SAP']

            logging.basicConfig(filename=os.path.expanduser('~') + '\system_refresh.log', level=logging.INFO,
                                format='[%(asctime)s]: [%(levelname)s]: [%(message)s]')

            self.conn = Connection(user=self.creds['user'], passwd=self.creds['passwd'], ashost=self.creds['ashost'],
                                   sysnr=self.creds['sysnr'], sid=self.creds['sid'], client=self.creds['client'])

        except Exception as e:
            logging.error("CONNECTION: Failed to connect to SAP. Please check the creds: {}".format(e))

    def users_list(self, module):
        users = []
        try:
            tables = self.conn.call("RFC_READ_TABLE", QUERY_TABLE='USR02', FIELDS=[{'FIELDNAME': 'BNAME'}])
            for data in tables['DATA']:
                for names in data.values():
                    users.append(names)
            self.data['USERS'] = users
            self.data['stdout'] = True
            logging.info("USERS_LIST: Successfully fetched user list from USR02 table!")
            module.exit_json(changed=True, meta=self.data)
        except Exception as e:
            logging.error("Failed to fetch user's list from USR02 table: {}".format(e))
            self.err = "USERS_LIST: Failed to fetch user's list from USR02 table: {}".format(e)
            module.fail_json(msg=self.err, error=to_native(e), exception=traceback.format_exc())

    def existing_locked_users(self, module):
        params = dict(
            PARAMETER='ISLOCKED',
            FIELD='LOCAL_LOCK',
            SIGN='I',
            OPTION='EQ',
            LOW='L'
        )
        try:
            user_list = self.conn.call("BAPI_USER_GETLIST", SELECTION_RANGE=[params])
            locked_user_list = []

            for user in user_list['USERLIST']:
                locked_user_list.append(user['USERNAME'])

            self.data['EXISTING_LOCKED_USERS'] = locked_user_list
            self.data['stdout'] = True
            logging.info("EXISTING_LOCKED_USERS: Successfully fetched existing locked user list!")
            module.exit_json(changed=True, meta=self.data)
        except Exception as e:
            logging.error("EXISTING_LOCKED_USERS: Failed to get existing locked user list: {}".format(e))
            self.err = "Failed to get existing locked user list: {}".format(e)
            module.fail_json(msg=self.err, error=to_native(e), exception=traceback.format_exc())

    def bapi_user_lock(self, module, params):
        users_list = params['ALL_USERS']
        users_locked = []
        errors = dict()
        users_exempted = []
        if users_list:
            for user in users_list:
                if user not in params['EXCEPTION_USERS']:
                    try:
                        self.conn.call('BAPI_USER_LOCK', USERNAME=user)
                        users_locked.append(user)
                    except Exception as e:
                        errors[user] = e
                        pass
                else:
                    users_exempted.append(user)
        else:
            self.err = "Failed to get entire user list before locking users"
            logging.error("BAPI_USER_LOCK: Failed to get entire user list before locking users")
            module.fail_json(msg=self.err, error=to_native(e), exception=traceback.format_exc())

        self.data['USERS_LOCKED'] = users_locked
        self.data['ERRORS'] = errors
        self.data['EXCEPTION_USERS'] = users_exempted

        logging.info("BAPI_USER_LOCK: Exception users list provided are: {}\n"
                     "BAPI_USER_LOCK: Successfully Locked users with exception to the Exception list provided!\n"
                     "BAPI_USER_LOCK: Users that were failed to Lock: {}".format(params['EXCEPTION_USERS'],
                                                                                 errors if errors else None))

        module.exit_json(changed=True, meta=self.data)

    def bapi_user_unlock(self, module, params):
        users_list = params['ALL_USERS']
        users_locked = []
        errors = dict()
        users_exempted = []
        if users_list:
            for user in users_list:
                if user not in params['EXCEPTION_USERS']:
                    try:
                        self.conn.call('BAPI_USER_UNLOCK', USERNAME=user)
                        users_locked.append(user)
                    except Exception as e:
                        errors[user] = e
                        pass
                else:
                    users_exempted.append(user)
        else:
            self.err = "Failed to get entire user list before unlocking the users"
            logging.error("BAPI_USER_UNLOCK: Failed to get entire user list before unlocking the users")
            module.fail_json(msg=self.err, error=to_native(e), exception=traceback.format_exc())

        self.data['USERS_UNLOCKED'] = users_locked
        self.data['ERRORS'] = errors
        self.data['EXCEPTION_USERS'] = users_exempted

        logging.info("BAPI_USER_LOCK: Exception users list: {}\n"
                     "BAPI_USER_LOCK: Successfully Locked users with exception to the Exception list provided!\n"
                     "BAPI_USER_LOCK: Users that were failed to Lock: {}".format(params['EXCEPTION_USERS'],
                                                                                 errors if errors else None))

        module.exit_json(changed=True, meta=self.data)

    def inst_execute_report(self, module, params):
        try:
            self.conn.call("INST_EXECUTE_REPORT", PROGRAM=params['PROGRAM'])
            if params['PROGRAM'] == 'BTCTRNS1':
                self.data["Success"] = "Background Jobs are Suspended!"
                logging.info("INST_EXECUTE_REPORT: Background Jobs are Suspended!")
            module.exit_json(changed=True, meta=self.data)
        except Exception as e:
            if params['PROGRAM'] == 'BTCTRNS1':
                self.err = "Failed to Suspend Background Jobs".format(e)
                logging.error("INST_EXECUTE_REPORT: Failed to Suspend Background Jobs: {}".format(e))
            module.fail_json(msg=self.err, error=to_native(e), exception=traceback.format_exc())

    def start_report_in_batch(self, module, params):
        try:
            self.conn.call("SUBST_START_REPORT_IN_BATCH", IV_JOBNAME=params['IV_JOBNAME'],
                           IV_REPNAME=params['IV_REPNAME'], IV_VARNAME=params['IV_VARNAME'])
            if params['IV_REPNAME'] == 'RSPOXDEV':
                self.data['Success'] = "Printer devices are Successfully exported!"
                logging.info("SUBST_START_REPORT_IN_BATCH: Printer devices are Successfully exported!")
            if params['IV_REPNAME'] == 'ZRSCLXCOP':
                self.data['Success'] = "User Master Export is Successfully Completed!"
                logging.info("SUBST_START_REPORT_IN_BATCH: User Master Export is Successfully Completed!")
            module.exit_json(changed=True, meta=self.data)
        except Exception as e:
            if params['IV_REPNAME'] == 'RSPOXDEV':
                self.err = "Failed to Export Printer devices".format(e)
                logging.error("SUBST_START_REPORT_IN_BATCH: Failed to Export Printer devices".format(e))
            if params['IV_REPNAME'] == 'ZRSCLXCOP':
                self.err = "User Master Export is Failed!".format(e)
                logging.error("SUBST_START_REPORT_IN_BATCH: User Master Export is Failed!".format(e))
            module.fail_json(msg=self.err, Error=to_native(e), exception=traceback.format_exc())

    def command_insert(self, module, params):
        args = dict(
            NAME=params['NAME'],
            OPSYSTEM=params['OPSYSTEM'],
            OPCOMMAND=params['OPCOMMAND'],
            PARAMETERS=params['PARAMETERS']
        )

        try:
            self.conn.call("ZSXPG_COMMAND_INSERT", COMMAND=args)
            self.data["Success!"] = "Successfully inserted command {}".format(params['NAME'])
            logging.info("ZSXPG_COMMAND_INSERT: Successfully inserted command {}".format(params['NAME']))
            module.exit_json(changed=True, meta=self.data)
        except Exception as e:
            self.err = "Failed to insert command {}".format(params['NAME'])
            logging.error("ZSXPG_COMMAND_INSERT: Failed to insert command {}".format(params['NAME']))
            module.fail_json(msg=self.err, error=to_native(e), exception=traceback.format_exc())

    def command_execute(self, module, params):
        try:
            self.conn.call("SXPG_COMMAND_EXECUTE", COMMANDNAME=params['NAME'])
            self.data["Success!"] = "Successfully Executed command {} and exported system tables".format(params['NAME'])
            logging.info("SXPG_COMMAND_EXECUTE: Successfully Executed command {} and exported system tables".format(
                params['NAME']))
            module.exit_json(changed=True, meta=self.data)
        except Exception as e:
            self.err = "Failed to Execute command {}".format(params['NAME'])
            logging.error("SXPG_COMMAND_EXECUTE:  Failed to Execute command {}".format(params['NAME']))
            module.fail_json(msg=self.err, error=to_native(e), exception=traceback.format_exc())

    def fetch(self, module, params):
        if params == 'sys_params':
            try:
                output = self.conn.call("RFC_READ_TABLE",
                                        QUERY_TABLE='E070L')  # IF Condition check needs to be implemented
            except Exception as e:
                self.err = "Failed to get data from E070L Table: {}".format(e)
                logging.error("FETCH: Failed to get data from E070L Table: {}".format(e))
                module.fail_json(msg=self.err, error=to_native(e), exception=traceback.format_exc())

            result = dict()
            trans_val = None
            for data in output['DATA']:
                for val in data.values():
                    trans_val = ((val.split()[1][:3] + 'C') + str(int(val.split()[1][4:]) + 1))
                    result["trans_val"] = trans_val

            try:
                trans_output = self.conn.call("RFC_READ_TABLE", QUERY_TABLE='E070',
                                              OPTIONS=[{"TEXT": "TRFUNCTION EQ 'M' AND AS4USER EQ 'DDIC'"}])
            except Exception as e:
                self.err = "Failed to query E070L Table: {}".format(e)
                logging.error("FETCH: Failed to query E070L Table: {}".format(e))
                module.fail_json(msg=self.err, error=to_native(e), exception=traceback.format_exc())

            trans = []
            for data in trans_output['DATA']:
                for val in data.values():
                    if str(self.creds['sid'] + 'KT') in val.split()[0]:
                        trans.append(val.split()[0])

            trans.sort(reverse=True)
            result['UME_Trans_No'] = trans[0]

            try:
                output = self.conn.call("RFC_READ_TABLE", QUERY_TABLE='TMSPCONF')
            except Exception as e:
                self.err = "Failed to query Table 'TMSPCONF': {}".format(e)
                logging.error("FETCH: Failed to qyery Table 'TMSPCONF': {}".format(e))
                module.fail_json(msg=self.err, error=to_native(e), exception=traceback.format_exc())

            ctc = None
            bin_path = None
            for field in output['DATA']:
                if field['WA'].split()[1] == 'CTC' and self.creds['sid'] in field['WA'].split()[0]:
                    ctc = field['WA'].split()[2]
                if field['WA'].split()[1] == 'TRANSDIR' and self.creds['sid'] in field['WA'].split()[0]:
                    bin_path = field['WA'].split()[2] + '/bin'

            if ctc is '1':
                result["sid_ctc_val"] = self.creds['sid'] + '.' + self.creds['client']
            else:
                result["sid_ctc_val"] = self.creds['sid']

            result["bin_path"] = bin_path
            result["client"] = self.creds['client']
            result["sid_val"] = self.creds['sid']

            logging.info("FETCH: trans_val='{}', UME_Trans_No='{}', bin_path='{}', sid_ctc_val='{}', ctc='{}', "
                         "client='{}', sid='{}'".format(result['trans_val'], result['UME_Trans_No'], result['bin_path'],
                                                        result["sid_ctc_val"], ctc, result['client'], result['sid_val']))

            if trans_val and ctc is not None:
                self.data['stdout'] = result
                module.exit_json(changed=True, meta=self.data)
            else:
                logging.error("FETCH: trans_val or ctc is found None!")
                self.err = "Failed to fetch {}".format(params['sys_params'])
                module.fail_json(msg=self.err, error=to_native(), exception=traceback.format_exc())

    def check_variant(self, module, report, variant_name):
        try:
            output = self.conn.call("RS_VARIANT_CONTENTS_RFC", REPORT=report, VARIANT=variant_name)
        except Exception as e:
            self.err = "Failed while checking variant existance {}: {}".format(variant_name, e)
            logging.error("CHECK VARIANT: Failed while checking variant existance {}: {}".format(variant_name, e))
            module.fail_json(msg=self.err, error=to_native(), exception=traceback.format_exc())

        var_content = []

        for key, value in output.items():
            if key == 'VALUTAB':
                var_content = value

        for cont in var_content:  # Export Printer devices
            if cont['SELNAME'] == 'FILE' and cont['LOW'] == '/tmp/printers':
                self.data['stdout'] = True
                logging.info("CHECK VARIANT: variant {} for report {} is already exist!".format(variant_name, report))
                module.exit_json(changed=True, meta=self.data)

        for cont in var_content:  # User Master Export & Import
            if cont['SELNAME'] == 'COPYCLI' and cont['LOW'] == self.creds['client']:
                self.data['stdout'] = True
                logging.info("CHECK VARIANT: variant {} for report {} is already exist!".format(variant_name, report))
                module.exit_json(changed=True, meta=self.data)

        for cont in var_content:  # Delete_old_bg_jobs
            if cont['SELNAME'] == 'FORCE' and cont['LOW'] == 'X':
                self.data['stdout'] = True
                logging.info("CHECK VARIANT: variant {} for report {} is already exist!".format(variant_name, report))
                module.exit_json(changed=True, meta=self.data)

        for cont in var_content:  # Delete_outbound_queues_SMQ1
            if cont['SELNAME'] == 'DISPLAY' and cont['LOW'] == 'X':
                self.data['stdout'] = True
                logging.info("CHECK VARIANT: variant {} for report {} is already exist!".format(variant_name, report))
                module.exit_json(changed=True, meta=self.data)

        for cont in var_content:  # Delete_outbound_queues_SMQ2
            if cont['SELNAME'] == 'SET_EXEC' and cont['LOW'] == 'X':
                self.data['stdout'] = True
                logging.info("CHECK VARIANT: variant {} for report {} is already exist!".format(variant_name, report))
                module.exit_json(changed=True, meta=self.data)

        for cont in var_content:  # BDLS_Logical_system_conversion
            if cont['SELNAME'] == 'P_TAB' and cont['LOW'] == '*':
                self.data['stdout'] = True
                logging.info("CHECK VARIANT: variant {} for report {} is already exist!".format(variant_name, report))
                module.exit_json(changed=True, meta=self.data)

        self.data['stdout'] = False
        self.data['mes'] = "variant {} for report {} doesn't exist!".format(variant_name, report)
        logging.info("CHECK VARIANT: variant {} for report {} doesn't exist!".format(variant_name, report))
        module.exit_json(changed=False, meta=self.data)

    def create_variant(self, module, report, variant_name, desc, content, text, screen):
        try:
            self.conn.call("RS_CREATE_VARIANT_RFC", CURR_REPORT=report, CURR_VARIANT=variant_name, VARI_DESC=desc,
                           VARI_CONTENTS=content, VARI_TEXT=text, VSCREENS=screen)
            self.data['Success'] = "Successfully Created variant {} for report {}".format(variant_name, report)
            self.data['stdout'] = True
            logging.info("CREATE VARIANT: Created variant {} for report {}".format(variant_name, report))
            module.exit_json(changed=True, meta=self.data)
        except Exception as e:
            self.err = "CREATE VARIANT: Failed to create variant {} for report {} : {}".format(variant_name, report, e)
            logging.error("CREATE VARIANT: Failed to create variant {} for report {} : {}".format(variant_name, report, e))
            module.fail_json(msg=self.err, error=to_native(e), exception=traceback.format_exc())

    def delete_variant(self, module, report, variant_name):
        try:
            self.conn.call("RS_VARIANT_DELETE_RFC", REPORT=report, VARIANT=variant_name)
            self.data['Success'] = "Successfully Deleted variant {} for report {}".format(variant_name, report)
            self.data['stdout'] = True
            logging.info("DELETE VARIANT: Deleted variant {} for report {}".format(variant_name, report))
            module.exit_json(changed=True, meta=self.data)
        except Exception as e:
            self.err = "Failed to delete variant {} for report {}: {}".format(variant_name, report, e)
            logging.error("DELETE VARIANT: Failed to delete variant {} for report {}: {}".format(variant_name, report, e))
            module.fail_json(msg=self.err, error=to_native(e), exception=traceback.format_exc())


