#!/usr/bin/python
# -*- coding: utf-8 -*-

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: variant
short_description: Manage variants in SAP.
description:
    - Interacts with SAP application using RFC protocol.
    - create, check and delete variants.
    - For all the pre and post refresh activities of SAP System Refresh.
version_added: "1.1"
author: "Mahesh Ramachandrappa (@mramachandrappa)"

options:
  report:
    description:
    - Name of the report.
    required: yes
    type: str
  variant_name:
    description:
    - Name of the variant.
    required: yes
    type: str
  action:
    description:
    - creates, deletes or checks the report in SAP system.
    choices=['create', 'delete', 'check']
    required: yes
    type: str

requirements:
    - pyrfc >= 2.0
    - configparser
    - variant_data [module_utils/variant_data.py] (That contains variant details)
notes:
    - For pyrfc and SAP network SDK's installation visit > https://sap.github.io/PyRFC/install.html
'''

EXAMPLES = '''

#create
- name: Creates variant in SAP.
  variant:
    report: "RSPOXDEV"
    variant_name: "SST_ZPRINT_EXP"
    action: create

#delete
- name: Deletes variant.
  variant:
    report: "RSPOXDEV"
    variant_name: "SST_ZPRINT_EXP"
    action: delete

#check
- name: Checks variant if it exists. returns True or False.
  variant:
    report: "RSPOXDEV"
    variant_name: "SST_ZPRINT_EXP"
    action: check

'''

from ansible.module_utils.basic import *
from ansible.module_utils.PreSystemRefresh import PreSystemRefresh
from ansible.module_utils.variant_data import *


def main():
    fields = dict(
        report=dict(required=True, type='str'),
        variant_name=dict(required=True, type='str'),
        action=dict(required=True, choices=['create', 'delete', 'check'], type='str')
    )

    module = AnsibleModule(
        argument_spec=fields,
        supports_check_mode=False
    )

    if module.check_mode:
        module.exit_json({"Mes": "CheckMode is not supported as of now!"})

    report = module.params['report']
    variant_name = module.params['variant_name']
    action = module.params['action']

    prefresh = PreSystemRefresh(module)

    if action == "create":
        prefresh.create_variant(module, report, variant_name, desc, content, text, screen)
    elif action == "delete":
        prefresh.delete_variant(module, report, variant_name)
    elif action == "check":
        prefresh.check_variant(module, report, variant_name)


if __name__ == "__main__":
    main()

