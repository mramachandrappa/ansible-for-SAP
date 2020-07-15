#!/usr/bin/python
#  -*- coding: utf-8 -*-

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: sap_function_call
short_description: To perform System Refresh Activities.
description:
    - Interacts with SAP application using RFC protocol.
    - Calls SAP Function modules by passing params required.
    - For all the pre and post refresh activities of SAP System Refresh.
version_added: "1.1"

options:
  FETCH:
    description:
    - Fetches following information from SAP Application.
        'sys_params' > returns trans_val, UME_Trans_No, sid_ctc_val, bin_path, client, sid_val
        'sys_users'  > returns entire System user list
        'sys_locked_users' > returns existing locked users.
        'bgd_val'    > returns bgd value.
    type: str
    choices: ['sys_params', 'sys_users', 'sys_locked_users', 'bgd_val']
  BAPI_USER_LOCK:
    description:
    - Lock SAP System users. 
    options:
        EXCEPTION_USERS: 
        - Exception user list to keep them from Locking.
        required: yes
        type: list
        All_USERS: 
        - Entire SAP System user list.
        required: yes
        type: list
    type: dict
  BAPI_USER_UNLOCK:
    description:
    - UnLocks SAP System users. 
    options:
        EXCEPTION_USERS: 
        - Exception user list to keep them from Locking.
        required: yes
        type: list
        All_USERS: 
        - Entire SAP System user list.
        required: yes
        type: list
    type: dict
  INST_EXECUTE_REPORT:
    description:
    - Executes an SAP Program.
    options:
        PROGRAM: 
        - Program to run.
        required: yes
        type: str
    type: dict
  SUBST_START_REPORT_IN_BATCH:
    description:
    - Starts report in batch.
    options:
        IV_JOBNAME: 
        - Jobname to run
        required: yes
        type: str
        IV_REPNAME: 
        - Report name
        required: yes
        type: str
        IV_VARNAME: 
        - Variant name
        required: yes
        type: str
    type: dict
  ZSXPG_COMMAND_INSERT:
    description: 
    - Inserts a command to execute.
    options:
        NAME: 
        - Name of the command
        required: yes
        type: str
        OPSYSTEM: 
        - OS Environment
        required: yes
        type: str
        OPCOMMAND: 
        - Command
        required: yes
        type: str 
        PARAMETERS: 
        - params for command
        required: yes
        type: str
    type: dict
  SXPG_COMMAND_EXECUTE:
    description: 
    - Executes the command created.
    options:
        COMMAND: 
        - Entire command to execute
        required: yes
        type: str
    type: dict
requirements:
    - pyrfc >= 2.0
    - configparser
notes:
    - For pyrfc and SAP network SDK's installation visit > https://sap.github.io/PyRFC/install.html
    
author: "Mahesh Ramachandrappa" [maheshramachandrappa91@gmail.com]
'''

EXAMPLES = r'''
# FETCH
- name: Fetches the values. choices['sys_params', 'sys_users', 'sys_locked_users'] 
  sap_function_call:
    FETCH: sys_users
  register: users

#BAPI_USER_LOCK
- name: Locks all users with exception to the EXCEPTION_USERS List provided.
  sap_function_call:
    BAPI_USER_LOCK:
        EXCEPTION_USERS: "['MRAM', 'GIRIDR']"
        ALL_USERS: "{{ users.meta.USERS }}"

#BAPI_USER_UNLOCK
- name: Locks all users with exception to the EXCEPTION_USERS List provided.
  sap_function_call:
    BAPI_USER_LOCK:
        EXCEPTION_USERS: "['MRAM', 'GIRIDR']"
        ALL_USERS: "{{ users.meta.USERS }}"

#INST_EXECUTE_REPORT
- name: Executes the SAP program.
  sap_function_call:
    INST_EXECUTE_REPORT:
        PROGRAM: 'BTCTRNS1'

#SUBST_START_REPORT_IN_BATCH
- name: Starts report in batch.
  sap_function_call:
    SUBST_START_REPORT_IN_BATCH:
        IV_JOBNAME: "ZRSCLXCOP"
        IV_REPNAME: "ZRSCLXCOP"
        IV_VARNAME: "SST_ZUSR_EXP"

#ZSXPG_COMMAND_INSERT
- name: Inserts command into OS level.
  sap_function_call:
    ZSXPG_COMMAND_INSERT:
        NAME: 'ZTABEXP'
        OPSYSTEM: 'Linux'
        OPCOMMAND: 'R3trans'
        PARAMETERS: '-w /tmp/exp_ecc.log /tmp/exp.ctl'

#SXPG_COMMAND_EXECUTE
- name: Executes the command inserted.
  sap_function_call:
    SXPG_COMMAND_EXECUTE:
        NAME: "ZTABEXP"
'''

from ansible.module_utils.basic import *
from ansible.module_utils.PreSystemRefresh import PreSystemRefresh
from ansible.module_utils.PostSystemRefresh import PostSystemRefresh


def main():
    fields = dict(
        FETCH=dict(
            choices=['sys_params', 'sys_users', 'sys_locked_users', 'bgd_val'], type='str'),
        BAPI_USER_LOCK=dict(
            EXCEPTION_USERS=dict(required=True, type='list'),
            ALL_USERS=dict(required=True, type='list'), type='dict'),
        BAPI_USER_UNLOCK=dict(
            EXCEPTION_USERS=dict(required=True, type='list'),
            ALL_USERS=dict(required=True, type='list'), type='dict'),
        INST_EXECUTE_REPORT=dict(
            PROGRAM=dict(required=True, type='str'), type='dict'),
        SUBST_START_REPORT_IN_BATCH=dict(
            IV_JOBNAME=dict(required=True, type='str'),
            IV_REPNAME=dict(required=True, type='str'),
            IV_VARNAME=dict(required=True, type='str'), type='dict'),
        ZSXPG_COMMAND_INSERT=dict(
            NAME=dict(required=True, type='str'),
            OPSYSTEM=dict(required=True, type='str'),
            OPCOMMAND=dict(required=True, type='str'),
            PARAMETERS=dict(required=True, type='str'), type='dict'),
        SXPG_COMMAND_EXECUTE=dict(
            COMMAND=dict(required=True, type='str'), type='dict')
    )

    module = AnsibleModule(
        argument_spec=fields,
        supports_check_mode=False
    )

    if module.check_mode:
        module.exit_json({"Mes": "CheckMode is not supported as of now!"})

    prefresh = PreSystemRefresh(module)
    postRefresh = PostSystemRefresh(module)

    if module.params['FETCH']:
        params = module.params['FETCH']
        if params == 'sys_params':
            prefresh.fetch(module, params)
        if params == 'sys_users':
            prefresh.users_list(module)
        if params == 'sys_locked_users':
            prefresh.existing_locked_users(module)
        if params == 'bgd_val':
            postRefresh.check_bg_jobs(module)

    if module.params['BAPI_USER_LOCK']:
        params = module.params['BAPI_USER_LOCK']
        prefresh.bapi_user_lock(module, params)

    if module.params['BAPI_USER_UNLOCK']:
        params = module.params['BAPI_USER_UNLOCK']
        prefresh.bapi_user_unlock(module, params)

    if module.params['INST_EXECUTE_REPORT']:
        params = module.params['INST_EXECUTE_REPORT']
        postRefresh.inst_execute_report(module, params)

    if module.params['SUBST_START_REPORT_IN_BATCH']:
        params = module.params['SUBST_START_REPORT_IN_BATCH']
        postRefresh.start_report_in_batch(module, params)

    if module.params['ZSXPG_COMMAND_INSERT']:
        params = module.params['ZSXPG_COMMAND_INSERT']
        prefresh.command_insert(module, params)

    if module.params['SXPG_COMMAND_EXECUTE']:
        params = module.params['SXPG_COMMAND_EXECUTE']
        prefresh.command_execute(module, params)


if __name__ == "__main__":
    main()
