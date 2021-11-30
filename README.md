CloudGenix - bulk_user_creation
---

Quick script to bulk create Prisma SDWAN Controller Portal Operators

#### Requirements
* Active CloudGenix Account
* Python >= 2.7 or >=3.6
* Python modules:
    * cloudgenix >=4.4.5b2 - <https://github.com/CloudGenix/sdk-python>
    * progressbar2 >=3.34.3 - <https://github.com/WoLpH/python-progressbar>

#### License
MIT

#### Usage Example:
bash#python Bulk-User-Creation.py bulk_list_simple.csv 

#### Prepare buulk csv file:
Please make sure to input system accepted roles:
'tenant_iam_admin', 'tenant_network_admin', 'tenant_security_admin', 'tenant_viewonly', 'tenant_super'


#### Version
Version | Changes
------- | --------
**1.0.0**| Initial Release.
