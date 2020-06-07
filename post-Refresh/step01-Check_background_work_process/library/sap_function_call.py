#!/usr/bin/python
from ansible.module_utils.basic import *
from ansible.module_utils.PreSystemRefresh import PreSystemRefresh


class SAPFunctionCall(PreSystemRefresh):
    data = dict()
    err = str()

    def inst_execute_report(self, module, params):
        try:
            self.conn.call("INST_EXECUTE_REPORT", PROGRAM=params['PROGRAM'])
            if params['PROGRAM'] == 'BTCTRNS1':
                self.data["Success"] = "Background Jobs are Suspended!"
            if params['PROGRAM'] == 'CSM_TAB_CLEAN':
                self.data["Success"] = "Cleaned CCMS data!"
            if params['PROGRAM'] == 'RSPO1043':
                self.data["Success"] = "Spool Consistency is being checked!"
            module.exit_json(changed=True, meta=self.data)
        except Exception as e:
            if params['PROGRAM'] == 'BTCTRNS1':
                self.err = "Failed to Suspend Background Jobs"
            if params['PROGRAM'] == 'CSM_TAB_CLEAN':
                self.err = "Failed to clean CCMS data"
            if params['PROGRAM'] == 'RSPO1043':
                self.err = "Failed to check spool consistency"
            module.fail_json(msg=self.err, error=to_native(e), exception=traceback.format_exc())

    def check_bg_jobs(self, module):
        try:
            output = self.conn.call("TH_WPINFO")
        except Exception as e:
            self.err = "Error while calling Function Module TH_WPINFO"
            module.fail_json(msg=self.err, Error=to_native(e), exception=traceback.format_exc())

        wp_type = []
        for type in output['WPLIST']:
            wp_type.append(type['WP_TYP'])

        if 'BGD' in wp_type:
            self.data['result'] = True
            module.exit_json(changed=True, meta=self.data)
        else:
            self.data['result'] = False
            module.exit_json(changed=True, meta=self.data)

    def start_report_in_batch(self, module, params):
        try:
            self.conn.call("SUBST_START_REPORT_IN_BATCH", IV_JOBNAME=params['IV_JOBNAME'],
                           IV_REPNAME=params['IV_REPNAME'], IV_VARNAME=params['IV_VARNAME'])
            if params['IV_REPNAME'] == 'RSBTCDEL':
                self.data['Success'] = "Old Background jobs logs are successfully deleted!"
            if params['IV_REPNAME'] == 'RSTRFCQD':
                self.data['Success'] = "Successfully Deleted SMQ1 Outbound Queues!"
            if params['IV_REPNAME'] == 'RSTRFCID':
                self.data['Success'] = "Successfully Deleted SMQ2 Outbound Queues!"
            module.exit_json(changed=True, meta=self.data)
        except Exception as e:
            if params['IV_REPNAME'] == 'RSBTCDEL':
                self.err = "Failed to delete Old Background job logs"
            if params['IV_REPNAME'] == 'RSTRFCQD':
                self.err = "Failed to delete SMQ1 Outbound Queues"
            if params['IV_REPNAME'] == 'RSTRFCID':
                self.err = "Failed to delete SMQ2 Outbound Queues"
            module.fail_json(msg=self.err, Error=to_native(e), exception=traceback.format_exc())

    def fetch(self, module, params):
        if params == 'sys_params':
            try:
                output = self.conn.call("RFC_READ_TABLE", QUERY_TABLE='E070L')  # IF Condition check needs to be implemented
            except Exception as e:
                self.err = "Failed while querying E070L Table: {}".format(e)
                module.fail_json(msg=self.err, error=to_native(e), exception=traceback.format_exc())

            result = dict()
            trans_val = None
            for data in output['DATA']:
                for val in data.values():
                    trans_val = ((val.split()[1][:3] + 'C') + str(int(val.split()[1][4:]) + 1))
                    result["trans_val"] = trans_val

            try:
                output = self.conn.call("RFC_READ_TABLE", QUERY_TABLE='TMSPCONF',
                                        FIELDS=[{'FIELDNAME': 'NAME'}, {'FIELDNAME': 'SYSNAME'}, {'FIELDNAME': 'VALUE'}])
            except Exception as e:
                self.err = "Failed while fetching TMC CTC Value: {}".format(e)
                module.fail_json(msg=self.err, error=to_native(e), exception=traceback.format_exc())

            ctc = None
            for field in output['DATA']:
                if field['WA'].split()[0] == 'CTC' and field['WA'].split()[1] == self.creds['sid']:
                    ctc = field['WA'].split()[2]

            if ctc is '1':
                sid_ctc_val = self.creds['sid'] + '.' + self.creds['client']
                result["sid_ctc_val"] = sid_ctc_val
            else:
                sid_ctc_val = self.creds['sid']
                result["sid_ctc_val"] = sid_ctc_val

            result["client"] = self.creds['client']
            result["sid_val"] = self.creds['sid']

            if trans_val and ctc is not None:
                self.data['stdout'] = result
                module.exit_json(changed=True, meta=self.data)
            else:
                self.err = "Failed to fetch {}".format(params['sys_params'])
                module.fail_json(msg=self.err, error=to_native(), exception=traceback.format_exc())


# For setting users to Administer Lock and Unlock
def bapi_user_lock(module, prefresh, params):
    data = dict()

    try:
        if params['fetch'] == 'users':
            user_list = prefresh.users_list()
            data["Entire System User List"] = user_list

        if params['fetch'] == 'locked_users':
            existing_locked_users = prefresh.existing_locked_users()
            data["User's who's status is already set to Administer Lock"] = existing_locked_users

        module.exit_json(changed=True, meta=data)

    except KeyError:
        if params['lock_users']['action'] == 'lock':
            user_list = prefresh.users_list()
            existing_locked_users = prefresh.existing_locked_users()
            exception_list = params['lock_users']['exception_list']

            active_users = [user for user in user_list if user not in existing_locked_users]

            locked_users, errors, excempted_users = prefresh.user_lock(active_users, exception_list, 'lock')

            data["Exception user list provided to keep them from locking"] = exception_list
            data["User's Locked with exception to the Exception user list provided ^^"] = locked_users

            module.exit_json(changed=True, meta=data)

        if params['lock_users']['action'] == 'unlock':
            user_list = prefresh.users_list()
            exception_list = params['lock_users']['exception_list']

            locked_users, errors, excempted_users = prefresh.user_lock(user_list, exception_list, 'unlock')

            data["User's who's current status is set to Lock(*including existing users that are locked)"] = exception_list
            data["User's Unlocked with exception to the users who's status was already locked prior to the activity"] = locked_users

            module.exit_json(changed=True, meta=data)

    except Exception as e:
        err = e
        module.fail_json(msg=err, Error=to_native(e), exception=traceback.format_exc())


def main():
    fields = dict(
        FETCH=dict(choices=['sys_params'], type='str'),
        BAPI_USER_LOCK=dict(
            fetch=dict(choices=['users', 'locked_users'], type='str'),
            lock_users=dict(action=dict(choices=['lock', 'unlock'], required=True),
                            exception_list=dict(required=True, type='list'), type='dict'),
            type='dict'),
        INST_EXECUTE_REPORT=dict(PROGRAM=dict(type='str'), type='dict'),
        TH_WPINFO=dict(fetch=dict(choices=['bgd_val'], type='str'), type='dict'),
        SUBST_START_REPORT_IN_BATCH=dict(
            IV_JOBNAME=dict(type='str'),
            IV_REPNAME=dict(type='str'),
            IV_VARNAME=dict(type='str'), type='dict')
    )

    module = AnsibleModule(
        argument_spec=fields,
        supports_check_mode=False
    )

    if module.check_mode:
        module.exit_json({"Mes": "CheckMode is not supported as of now!"})

    prefresh = PreSystemRefresh()
    functioncall = SAPFunctionCall()

    if module.params['FETCH']:
        params = module.params['FETCH']
        functioncall.fetch(module, params)

    if module.params['BAPI_USER_LOCK']:
        params = module.params['BAPI_USER_LOCK']
        bapi_user_lock(module, prefresh, params)

    if module.params['INST_EXECUTE_REPORT']:
        params = module.params['INST_EXECUTE_REPORT']
        functioncall.inst_execute_report(module, params)

    if module.params['TH_WPINFO']:
        functioncall.check_bg_jobs(module)

    if module.params['SUBST_START_REPORT_IN_BATCH']:
        params = module.params['SUBST_START_REPORT_IN_BATCH']
        functioncall.start_report_in_batch(module, params)


if __name__ == "__main__":
    main()
