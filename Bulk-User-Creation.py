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
tenant_roles = []
tenant_rolemap = {}

resp = cgx_session.get.base_roles()

if resp.cgx_status:
    sysroles = resp.cgx_content.get("items", None)
    for role in sysroles:
        base_rolemap = {role["name"]: {"name": role["name"]}}
        tenant_roles.append(role["name"])
        tenant_rolemap.update(base_rolemap)
else:
    print("ERR: Could not retrieve base roles")
    cloudgenix.jd_detailed(resp)
    
# Create custom roles and update custom rolemap
custom_roles = []
custome_rolemap = {}

resp = cgx_session.get.roles()

if resp.cgx_status:
    roles = resp.cgx_content.get("items", None)
    for role in roles:
        rolemap = {role["name"]: {"id": role["id"]}}
        custom_roles.append(role["name"])
        custom_rolemap.update(rolemap)
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
# Only validate if email is in csv and no duplication in existing operators. More key field to be defined.
with open('bulk_list_simple.csv', 'r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    
    for data in csv_reader:
    
        roles = data["roles"]
        email = data["email"]        
        
        signup_data = {
            "first_name": [],
            "email": [],
            "secondary_emails": [],
            "phone_numbers": [],
            "roles": [],
            "custom_roles": [],
            "disabled": False,
            "disable_idp_login": True,
            "enable_session_ip_lock": False,
            "ipv4_list": [],
            "last_name": [],
            "password": [],
            "repeatPassword": []
        }
        
        signup_data["first_name"] = data["first_name"]
        signup_data["last_name"] = data["last_name"]
        signup_data["email"] = data["email"]
        signup_data["password"] = data["password"]
        signup_data["repeatPassword"] = data["password"]
        
        if roles:
            if "," in roles:
                tmp = roles.split(",")

                for role in tmp:
                    if role not in tenant_roles:
                        if role not in custom_roles:
                            print("ERR: Invalid role. Please input defined custom roles")
                            sys.exit()
                        else:
                            mappedrole = custom_rolemap[role]
                            signup_data["custom_roles"].append(mappedrole)
                                
                    else:
                        mappedrole = tenant_rolemap[role]
                        signup_data["roles"].append(mappedrole)
            else:
                if roles not in tenant_roles:
                    if roles not in custom_roles:
                        print("ERR: Invalid role. Please input defined custom roles")
                        sys.exit()
                    else:
                        mappedrole = custom_rolemap[roles]
                        signup_data["custom_roles"].append(mappedrole)
                            
                else:
                    mappedrole = tenant_rolemap[roles]
                    signup_data["roles"].append(mappedrole)

        if email:
            if email in email_list:
                print("ERR: Operator existed, duplicated operator email is ", email)
                sys.exit()
        else:
                print("ERR: Need primary email to create user account. Please make sure all new users input emails. ")
                sys.exit()

        resp = cgx_session.post.signup(signup_data)

        if resp.cgx_status:
            oid = resp.cgx_content.get("id", None)
            print("Operator created. ID: {}".format(oid))
        else:
            print("ERR: Could not create Operator")
