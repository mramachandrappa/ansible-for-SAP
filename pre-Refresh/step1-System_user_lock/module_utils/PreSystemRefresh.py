from pyrfc import Connection
from configparser import ConfigParser
import os


class PreSystemRefresh:
    data = dict()
    err = str()

    def __init__(self):
        self.config = ConfigParser()
        self.config.read(os.environ["HOME"] + '/.config/sap_config.cnf')
        self.creds = self.config['SAP']

        try:
            self.conn = Connection(user=self.creds['user'], passwd=self.creds['passwd'], ashost=self.creds['ashost'],
                                   sysnr=self.creds['sysnr'], sid=self.creds['sid'], client=self.creds['client'])
        except Exception as e:
            self.err = "Failed when connecting to SAP application, please check the creds passed!"
            module.fail_json(msg=self.err, error=to_native(e), exception=traceback.format_exc())

    def users_list(self, module):
        users = []
        try:
            tables = self.conn.call("RFC_READ_TABLE", QUERY_TABLE='USR02', FIELDS=[{'FIELDNAME': 'BNAME'}])
            for data in tables['DATA']:
                for names in data.values():
                    users.append(names)
            self.data['users'] = users
            self.data['stdout'] = True
            module.exit_json(changed=True, meta=self.data)
        except Exception as e:
            self.err = "Failed to fetch user's list from USR02 table: {}".format(e)
            self.data['stdout'] = False
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

            self.data['existing_locked_users'] = locked_user_list
            self.data['stdout'] = True
            module.exit_json(changed=True, meta=self.data)
        except Exception as e:
            self.err = "Failed to get existing locked user list: {}".format(e)
            self.data['stdout'] = False
            module.fail_json(msg=self.err, error=to_native(e), exception=traceback.format_exc())

    def bapi_user_lock(self, module, users_list, exception_user_list):
        users_locked = []
        errors = dict()
        users_exempted = []
        for user in users_list:
            if user not in exception_user_list:
                try:
                    self.conn.call('BAPI_USER_LOCK', USERNAME=user)
                    users_locked.append(user)
                except Exception as e:
                    errors[user] = e
                    pass
            else:
                users_exempted.append(user)

        self.data['users_locked'] = users_locked
        self.data['errors'] = errors
        self.data['users_exempted'] = users_exempted

        module.exit_json(changed=True, meta=self.data)

    def bapi_user_unlock(self, module, users_list, exception_user_list):
        users_locked = []
        errors = dict()
        users_exempted = []
        for user in users_list:
            if user not in exception_user_list:
                try:
                    self.conn.call('BAPI_USER_UNLOCK', USERNAME=user)
                    users_locked.append(user)
                except Exception as e:
                    errors[user] = e
                    pass
            else:
                users_exempted.append(user)

        self.data['users_locked'] = users_locked
        self.data['errors'] = errors
        self.data['users_exempted'] = users_exempted

        module.exit_json(changed=True, meta=self.data)

    def user_lock(self, user_list, except_users_list, action):
        if action == "lock":
            func_module = 'BAPI_USER_LOCK'
        elif action == "unlock":
            func_module = 'BAPI_USER_UNLOCK'
        else:
            return "Failed! Please pass argument ['lock' | 'unlock']"

        users_locked = []
        errors = dict()
        users_exempted = []
        for user in user_list:
            if user not in except_users_list:
                try:
                    self.conn.call(func_module, USERNAME=user)
                    users_locked.append(user)
                except Exception as e:
                    errors[user] = e
                    pass
            else:
                users_exempted.append(user)

        return users_locked, errors, users_exempted

    #    def suspend_bg_jobs(self):                 Handled in sap_function_call.py module

    #    def export_sys_tables_cmd_insert(self):    Handled in sap_function_call.py module

    #    def export_sys_tables_cmd_execute(self):   Handled in sap_function_call.py module

    def check_variant(self, report, variant_name):
        try:
            output = self.conn.call("RS_VARIANT_CONTENTS_RFC", REPORT=report, VARIANT=variant_name)
        except Exception as e:
            return "Failed to check variant {}: {}".format(variant_name, e)

        var_content = []

        for key, value in output.items():
            if key == 'VALUTAB':
                var_content = value

        for cont in var_content:  # Export Printer devices
            if cont['SELNAME'] == 'FILE' and cont['LOW'] == '/tmp/printers':
                return True

        for cont in var_content:  # User Master Export
            if cont['SELNAME'] == 'COPYCLI' and cont['LOW'] == self.creds['client']:
                return True

        for cont in var_content:  # Delete_old_bg_jobs
            if cont['SELNAME'] == 'FORCE' and cont['LOW'] == 'X':
                return True

        for cont in var_content:  # Delete_outbound_queues_SMQ1
            if cont['SELNAME'] == 'DISPLAY' and cont['LOW'] == 'X':
                return True

        for cont in var_content:  # Delete_outbound_queues_SMQ2
            if cont['SELNAME'] == 'SET_EXEC' and cont['LOW'] == 'X':
                return True

        return False

    def create_variant(self, report, variant_name, desc, content, text, screen):
        try:
            self.conn.call("RS_CREATE_VARIANT_RFC", CURR_REPORT=report, CURR_VARIANT=variant_name, VARI_DESC=desc,
                           VARI_CONTENTS=content, VARI_TEXT=text, VSCREENS=screen)
        except Exception as e:
            return "Variant {} for report {} Creation is Failed! : {}".format(variant_name, report, e)

        if self.check_variant(report, variant_name) is True:
            return "Variant {} Successfully Created for report {}".format(variant_name, report)
        else:
            return "Creation of variant {} for report {} is Failed!!".format(variant_name, report)

    def delete_variant(self, report, variant_name):
        try:
            self.conn.call("RS_VARIANT_DELETE_RFC", REPORT=report, VARIANT=variant_name)
        except Exception as e:
            return "Deletion of variant {} of report {} is Failed!: {}".format(variant_name, report, e)

        if self.check_variant(report, variant_name) is False:
            return "Variant {} for report {} is Successfully Deleted".format(variant_name, report)
        else:
            return "Failed to delete variant {} for report {}".format(variant_name, report)

    #   def export_printer_devices(self, report, variant_name): Handled in sap_function_call.py module

    #   def sid_ctc_val(self):  Handled in sap_function_call.py module

    #   def user_master_export(self, report, variant_name): Handled in sap_function_call.py module

# 1. System user lock               = Done
# 2. Suspend background Jobs        = Done
# 3. Export Quality System Tables   = Not Done # Funciton module is not callable
# 4. Export Printer Devices         = Done     # SSH to fetch /tmp/printers file from target to ansible controller node.
# 5. User Master Export             = Done     # SSH to fetch user master exported file.

