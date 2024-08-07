'''
File:           update_stb.py
Brief:          Downloads update to USB inserted in STB and then reboots the box.

Copyright
---------
Copyright 2009-2020 Commscope Inc. All rights reserved.
This program is confidential and proprietary to Commscope Inc.
(CommScope), and may not be copied, reproduced, modified, disclosed to
others, published or used, in whole or in part, without the express
prior written permission of CommScope.
'''

from boxscope.utilities.UseSSH import UseSSH
import argparse
import sys
import time

# =====================================================================================================================
# README!!
# =====================================================================================================================
#
# Before running this script, you must have already plugged a USB stick into your STB.
# This script only works with debug builds.
#
# Operation
# ---------
#
# 1) Find out the IP of your STB
# 2) Navigate to http://tungsten-fileserver.pace.internal/IMAGES_Jenkins/
# 3) Open the B876 folder for iQ3 or E733 for iQ4
# 4) Right click on the software release you want to download
# 5) Select copy link address
# 6) type python stb_upgrade <INSERT YOUR IP> <RIGHT CLICK TO PASTE THE URL LINK>
# =====================================================================================================================

def get_args():
    """Get some basic parameters for the script"""
    parser = argparse.ArgumentParser(description="Update STB's")
    parser.add_argument('IP', help='IP Address of the STB to Update')
    parser.add_argument('URL', help='URL of the file to download')
    parser.add_argument('--delete', action='store_true', help='Mount the USB drive and delete the image, then exit immediately')
    parser.add_argument('--download', action='store_true', help='Just download the image but do not reboot')
    parser.add_argument('--signed', action='store_true', help='Whether the image is signed by foxtel. If so, the '\
                            'file will be renamed to 0.fsi instead of rtimage.bin')
    parser.add_argument('--skip-platform-check', action='store_true', help='Skip Platform Check (IF STB is dead, calljs will not work)')
    parser.add_argument('--debug', action='store_true', help='Debug Printing')
    return parser.parse_args()


def mount_usb():
    # =====================================================================================================================
    # Create Folders
    # =====================================================================================================================
    print("="*80)
    print('MOUNTING USB')
    print("="*80)
    print('1) Creating Folders')
    stdout, stderr = session.send_ssh_command_to_STB('mkdir /mnt/rtimages/', return_all=True)
    stdout = "".join(stdout)
    stderr = "".join(stderr)
    if not stderr:
        print('Done')
    else:
        print(stderr)
        if "File exists" not in stderr:
            sys.exit(1)

    # Mount USB
    # =====================================================================================================================
    print("="*80)
    print('2) Mounting')
    USB_MOUNTED = False
    EXCLUDE = []
    TRY = []

    stdout, stderr = session.send_ssh_command_to_STB('/sbin/fdisk -l | /bin/grep FAT', return_all=True)
    stdout = "".join(stdout)
    stderr = "".join(stderr)

    # The device should be the first line
    print(stdout)

    if not stdout:
        print("No FAT partitions found")
        sys.exit(1)

    # Device should be the first in the list after splitting
    device = stdout.split()[0]

    command = 'mount {} /mnt/rtimages/'.format(device)
    print('Sending: {}'.format(command))
    stdout, stderr = session.send_ssh_command_to_STB(command, return_all=True)
    stdout = "".join(stdout)
    stderr = "".join(stderr)

    if not stderr:
        print('Done')
        USB_MOUNTED = True
        return device
    else:
        print(stderr)
        if "already mounted" in stderr:
            print("USB Stick is already mounted")
            USB_MOUNTED = True
            return device

        if "Device or resource busy" in stderr:
            # Double check to make sure!
            print("Running 'df -h' to see if it is mounted")
            stdout, stderr = session.send_ssh_command_to_STB('df -h', return_all=True)
            stdout = "".join(stdout)
            stderr = "".join(stderr)

            if not stderr and device in stdout and "/mnt/rtimages" in stdout:
                print('Already Mounted!')
                USB_MOUNTED = True
                return device
            else:
                print('Unexpected Response...')
                print(stdout)
                print(stderr)
                sys.exit(1)

    # We should be mounted by now. If not, exit
    if not USB_MOUNTED:
        print('FAILED TO MOUNT DEVICE')
        sys.exit(1)

args = get_args()

# =====================================================================================================================
# CREATE THE CONNECTION
# =====================================================================================================================
session = UseSSH(ipaddr=args.IP, debug=args.debug)
print("="*80)
print('SOFTWARE UPDATE STARTED')
print("="*80)
print('STB: {}'.format(args.IP))
print('IMAGE: {}'.format(args.URL))

if "DEBUG" not in args.URL:
    while True:
        x = input('WARNING: This does not appear to be a DEBUG build - Are you sure you want to continue? [Y/N]')

        if x.upper() == "Y":
            # Continue with the upgrade
            break
        elif x.upper() == "N":
            sys.exit(0)
        else:
            print('Invalid Option. Please Try again...')
            continue

# =====================================================================================================================
# Check Image
# =====================================================================================================================
if not args.skip_platform_check:
    print("="*80)
    print('Checking STB Platform')
    stdout, stderr = session.send_ssh_command_to_STB('calljs "pace.config.getOemModelId()"', return_all=True)
    stdout = "".join(stdout)
    stderr = "".join(stderr)
    response = session.get_API_response()
    print(response)
    if response in ["0A", "2A"]:
        box_type = "iQ4"
        if "E733" not in args.URL:
            print('WARNING! It looks like you are trying to flash the wrong software for this boxtype')
            print('STB = {} but found did not find E733 in URL'.format(box_type))
            sys.exit(1)
    elif response in ["09", "89"]:
        box_type = "iQ3"
        if "B876" not in args.URL:
            print('WARNING! It looks like you are trying to flash the wrong software for this boxtype')
            print('STB = {} but did not find B876 in URL'.format(box_type))
            sys.exit(1)

    elif response in ["0B", "2B"]:
        box_type = "iQ5"
        if "iQ5" not in args.URL:
            print('WARNING! It looks like you are trying to flash the wrong software for this boxtype')
            print('STB = {} but did not find iQ5 in URL'.format(box_type))
            sys.exit(1)

    if box_type == "unknown":
        box_type = box_type + " - " + response
        print('WARNING! Box type unknown. Not safe to flash the software')
        sys.exit(1)

    print('Platform = {}'.format(box_type))

ATTEMPT = 0
MAX_RETRIES = 3
SUCCESS = False
while ATTEMPT < MAX_RETRIES:
    ATTEMPT += 1

    # Mount the USB
    device = mount_usb()

    # DELETE
    if args.delete:
        print("Cleaning USB")
        print("="*80)

        command = "rm -r /mnt/rtimages/*.*"
        print("Sending: {}".format(command))
        stdout, stderr = session.send_ssh_command_to_STB(command, timeout=600, return_all=True)
        stdout = "".join(stdout)
        stderr = "".join(stderr)
        if stderr:
            print('ERROR')
            print(stderr)
            sys.exit(1)
        sys.exit(0)

    # Download
    # =====================================================================================================================
    print("="*80)
    print('Downloading Image')
    print("="*80)

    print("1) Curling Release")

    if args.signed:
        command = "curl -o /mnt/rtimages/0.fsi {}".format(args.URL)
    else:
        command = "curl -o /mnt/rtimages/rtimage.bin {}".format(args.URL)

    print("Sending: {}".format(command))
    stdout, stderr = session.send_ssh_command_to_STB(command, timeout=600, return_all=True)
    stdout = "".join(stdout)
    stderr = "".join(stderr)

    if "Connection timed out" in stderr:
        print(stderr)
        continue

    # CURL Will print the progress to STDERR. So we will add some error checking once we see errors downloading and
    # can extract the error messages.
    print(stderr)
    print('Standard Out')
    print(stdout)
    if "Could not resolve host" in stderr:
        print('Not able to download image!')
        print('Please check you have pasted the URL correctly')
        continue

    if "failed" in stderr or "failed" in stdout:
        print('Failed to download image!')
        continue

    # Double check the exit code was succesfull
    command = "echo $?"
    print("Sending: {}".format(command))
    stdout, stderr = session.send_ssh_command_to_STB(command, timeout=600, return_all=True)
    stdout = "".join(stdout)
    stderr = "".join(stderr)

    print('Exit Code: {}'.format(stdout))
    if int(stdout) != 0:
        print("Curl Exited Abnormally")
        continue

    print('DONE!')

    # Sleep - We are seeing some boxes unable to flash the software and get stuck on the bootloader.
    # Adding a sleep in case the STB has not finished writing to USB before reboot
    time.sleep(2)

    # Also - unmount so we can see if the device is busy
    print('2) Unmounting USB')
    command = 'umount /mnt/rtimages/'
    print('  - Sending: {}'.format(command))
    stdout, stderr = session.send_ssh_command_to_STB(command, return_all=True)
    stdout = "".join(stdout)
    stderr = "".join(stderr)
    if not stderr:
        print('  - Done')
    else:
        print(stderr)

    if args.download:
        print("Download only option given, Exiting")
        sys.exit(0)

    # Reboot
    print('3) rebooting')
    stdout, stderr = session.send_ssh_command_to_STB('/sbin/reboot > /dev/null 2>&1 &', return_all=True)
    stdout = "".join(stdout)
    stderr = "".join(stderr)
    if not stderr:
        print('Done')
    else:
        print(stderr)

    # Verify
    # =====================================================================================================================
    print("="*80)
    print("Verifying Software")
    print("="*80)
    print('1) Waiting for reboot')

    # Wait for STB to wake up
    time.sleep(300) # 5 mins should be enough

    print("2) Checking SW Version")
    command = 'calljs "pace.config.firmwareVersion()"'
    print('  - Sending: {}'.format(command))
    stdout, stderr = session.send_ssh_command_to_STB(command, return_all=True)
    stdout = "".join(stdout)
    stderr = "".join(stderr)

    response = session.get_API_response()
    print('  - Firmware Version: {}'.format(response))

    if response.strip() in args.URL:
        print('  - Upgraded Successfully')
        SUCCESS = True
        # Break the loop when successful
        break
    else:
        print('Unexpected firmware version returned')


if SUCCESS:
    print("="*80)

    device = mount_usb()

    print('9) Cleaning USB')
    command = "rm -r /mnt/rtimages/*.*"
    print("Sending: {}".format(command))
    stdout, stderr = session.send_ssh_command_to_STB(command, timeout=600, return_all=True)
    stdout = "".join(stdout)
    stderr = "".join(stderr)
    if stderr:
        print('ERROR Cleaning USB')
        print(stderr)
        sys.exit(1)

    sys.exit(0)

else:
    print("WARNING ERROR UPGRADING!")
    sys.exit(1)