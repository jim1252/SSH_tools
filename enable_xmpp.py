"""
# File: enable_xmpp.py
# Brief: A script to configure a STB for XMPP with A2.0        

# Copyright
# ---------
# Copyright 2009-2025 Commscope Inc. All rights reserved.
# This program is confidential and proprietary to Commscope Inc.
# (CommScope), and may not be copied, reproduced, modified, disclosed to
# others, published or used, in whole or in part, without the express
# prior written permission of CommScope.
# ================================================================

# IMPORTANT!!
# -----------
# Your STB must be running DEBUG software before running this script
# SSH will be used to configure settings required for automation
"""
# std imports 
import argparse
import sys

# framework imports
from boxscope.utilities.UseSSH import UseSSH

def get_args():
    """Get some basic parameters for the script"""
    parser = argparse.ArgumentParser(description="Update STB's")
    parser.add_argument('IP', help='IP Address of the STB to Update')
    parser.add_argument('--xmpp-environment', default="COMMSCOPE_A2.0", choices=["COMMSCOPE", "COMMSCOPE_A2.0", "FOXTEL", "FOXTEL_PTS", "FOXTEL_SANDPIT"], help='Select')
    parser.add_argument('--debug', action='store_true', help='Debug Printing')
    parser.add_argument('--perm', action='store_true', help='Make tungsten.provisioning.xmpp1 a permanent change in '
                        '/mnt/ffs/permanent/default.db')
    
    return parser.parse_args()

domains = {
    "COMMSCOPE": "xmpp.connectedhomesolutions.net", 
    "COMMSCOPE_A2.0": "xmpp.connectedhomesolutions.net", 
    "FOXTEL": "xmpp.connectedhomesolutions.net", 
    "FOXTEL_PTS" : "managed.dev-xmpp.foxtel.com.au", 
    "FOXTEL_SANDPIT" : "xmpp.thomasholtdrive.com"
}

# START
# -------------------------------------------------------------------------------
args = get_args()

selected_domain = domains[args.xmpp_environment]
print(f"Selected Domain: {selected_domain}")

session = UseSSH(ipaddr=args.IP, debug=args.debug)

# Get CDSN from STB
session.call_the_API_command_on_the_STB("pace.CA.getSerialNumber(1)")
CDSN = session.get_API_response().replace('"', '')
print('The CDSN is: {}'.format(CDSN))
if not CDSN:
    print("No CDSN Returned, aborting")
    sys.exit(1)

# Enable XMPP
print('1) Setting tungsten.provisioning.xmpp1 provisioning settings')

setting =  'description=server,user=%s.iq3,password=%s.iq3,domain=%s,resource=iq3,auth=digest' \
                  % (CDSN, CDSN, selected_domain)

if args.perm:
    print('1b) Making setting permanent')
    command = """sqlite3 /mnt/ffs/permanent/default.db 'insert or replace into active_Table VALUES("tungsten.provisioning.xmpp1","{}","false","true","false");' """.format(setting)
    if args.debug:
        print(" - Sending: {}".format(command))
    session.send_ssh_command_to_STB(command)
    response = session.get_API_response()

command = 'settings_cli Set "tungsten.provisioning.xmpp1" "{}"'.format(setting)
if args.debug:
    print(" - Sending: {}".format(command))
session.send_ssh_command_to_STB(command)
response = session.get_API_response()

# Update DB
print('2) Updating tungsten.provisioning.xmppConfiguration in the DB')
command = """sqlite3 /mnt/ffs/settings/active.db 'update active_table set value = "trustedJids=remotedvr@cobalt.pace.com,remotedvr@elements-dev.xyz,remotedvr@xmpp.connectedhomesolutions.net,remotedvr@elements.commscope.com,scripts@elements-dev.xyz,human@elements-dev.xyz,automation2.0@elements-dev.xyz,remotedvr@xmpp.connectedhomesolutions.net,automation2.0@xmpp.connectedhomesolutions.net,scripts@xmpp.connectedhomesolutions.net,human@xmpp.connectedhomesolutions.net,foxtel_automation@managed.dev-xmpp.foxtel.com.au,foxtel_automation@xmpp.thomasholtdrive.com", modified = "true" where key = "tungsten.provisioning.xmppConfiguration";' """
if args.debug:
    print(" - Sending: {}".format(command))
session.send_ssh_command_to_STB(command)
response = session.get_API_response()

print('3) Checking Settings from the DB')
command = """sqlite3 /mnt/ffs/settings/active.db 'Select * from active_table where key = "tungsten.provisioning.xmppConfiguration" ' """
if args.debug:
    print(" - Sending: {}".format(command))
session.send_ssh_command_to_STB(command)
response = session.get_API_response()

check1 = "automation2.0@xmpp.connectedhomesolutions.net" in response
if not check1:
    print("Error: {}".format(response))
    sys.exit(1)


print('3) rebooting')
session.send_ssh_command_to_STB('/sbin/reboot > /dev/null 2>&1 &', return_all=True)
response = session.get_API_response()

print("Done - Wait for your STB to reboot")
