#!/usr/bin/env python
# coding: utf-8

import cloudgenix
import json
import csv
import os
import sys
import datetime
import argparse

import pprint
pp = pprint.PrettyPrinter(indent=4)

bulkcsv = sys.argv[1]

sys.path.append(os.getcwd())
try:
    from cloudgenix_settings import CLOUDGENIX_CRYPTKEY, CLOUDGENIX_AUTH_TOKEN
    print(CLOUDGENIX_CRYPTKEY,CLOUDGENIX_AUTH_TOKEN)

except ImportError:
    # Get AUTH_TOKEN/X_AUTH_TOKEN from env variable, if it exists. X_AUTH_TOKEN takes priority.
    if "X_AUTH_TOKEN" in os.environ:
        CLOUDGENIX_AUTH_TOKEN = os.environ.get('X_AUTH_TOKEN')
    elif "AUTH_TOKEN" in os.environ:
        CLOUDGENIX_AUTH_TOKEN = os.environ.get('AUTH_TOKEN')
    else:
        # not set
        CLOUDGENIX_AUTH_TOKEN = None

try:
    from cloudgenix_settings import CLOUDGENIX_USER, CLOUDGENIX_PASSWORD

except ImportError:
    # will get caught below
    CLOUDGENIX_USER = None
    CLOUDGENIX_PASSWORD = None

cgx_session = cloudgenix.API(controller = "https://api.elcapitan.cloudgenix.com", ssl_verify=False)

cgx_session.interactive.use_token(AUTH_TOKEN)


#Creating system role map

ROLES = []
rolemap = {}

resp = cgx_session.get.base_roles()
if resp.cgx_status:
    sysroles = resp.cgx_content.get("items", None)
    for role in sysroles:
        base_rolemap = {role["name"]: [{"name": role["name"]}]}
        ROLES.append(role["name"])
        rolemap.update(base_rolemap)
else:
    print("ERR: Could not retrieve base roles")
    cloudgenix.jd_detailed(resp)
    
# Retrieve custom roles and update rolemap
resp = cgx_session.get.roles()

if resp.cgx_status:
    custom_roles = resp.cgx_content.get("items", None)
    for role in custom_roles:
        custom_rolemap = {role["name"]: [{"name": role["name"]}]}
        ROLES.append(role["name"])
        rolemap.update(custom_rolemap)
else:
    print("ERR: Could not retrieve base roles")
    cloudgenix.jd_detailed(resp[name])
    
    

#check existing operators and generate key field list to avoid deuplication
resp = cgx_session.get.tenant_operators()

if resp.cgx_status:
    existing_users = resp.cgx_content.get("items",None)
    email_list = []
    for user in existing_users:
        email_list.append(user["email"])
else:
    print("ERR: Could not retrieve base roles")
    cloudgenix.jd_detailed(resp)


# Read and validate roles from CSV
# Only validate if email is in csv and no duplication in existing operators. 
with open(bulkcsv, 'r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    
    for data in csv_reader:
    
        roles = data["roles"]
        email = data["email"]
        
        #multiple system roles not working now. 
        if roles:
            if "," in roles:
                tmp = roles.split(",")

                for role in tmp:
                    if role not in ROLES:
                        print("ERR: Invalid role. Please choose from: 'tenant_iam_admin', 'tenant_network_admin', 'tenant_security_admin', 'tenant_viewonly', 'tenant_super' or custom roles defined in system")
                        sys.exit()
                    else:
                        mappedrole = rolemap[role]
            else:
                if roles in ROLES:
                    mappedrole = rolemap[roles]
                    data["roles"] = mappedrole
                else:
                    print("ERR: Invalid role. Please choose from: super,viewonly,secadmin,nwadmin or iamadmin")
                    sys.exit()
        if email:
            if email in email_list:
                print("ERR: Operator existed, duplicated operator email is ", email)
                sys.exit()
        else:
                print("ERR: Need primary email to create user account. Please make sure all new users input emails. ")
                sys.exit()
        
        resp = cgx_session.post.signup(data=data)

        if resp.cgx_status:
            oid = resp.cgx_content.get("id", None)
            print("Operator created. ID: {}".format(oid))
        else:
            print("ERR: Could not create Operator")

