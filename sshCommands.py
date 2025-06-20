#!/usr/bin/env python3
'''
File:           sshCommands.py
Brief:          Send a series of commands to a STB to provide correct settings
Author:         James McArthur
Contributors:   N/A

Copyright
---------
Copyright 2009-2024 Commscope Inc. All rights reserved.
This program is confidential and proprietary to Commscope Inc.
(CommScope), and may not be copied, reproduced, modified, disclosed to
others, published or used, in whole or in part, without the express
prior written permission of CommScope.
'''

import paramiko
#import time
import argparse
import sys

port =22
username ='root'
password = ' '
ssh = paramiko.SSHClient()
#ip = ' '
lines = ' '
err = ' ' 
cmdIn = ' '
serialNumber = ' '
softwareVer = ' '
buildVer = ' '
macaddr = ' '
stbMode = ' '
updateDelay  = ' '
appConfigDelay  = ' '
savedDelay = ' '
CDSN = ' '
stbReadSetting = ' '
saveSetting = ' '
stbModeCommand = ' '
enableCommand = ' '
fileCommand = ' '
server = ' '
userIp = ' '
box_type = ' '
#modelType = ' '

print ('sshcommands open')

def get_args():
    reporting_parser = argparse.ArgumentParser(description='To configure a STB to connect the required server for XMPP messaging',
                                               epilog='for additional help contact James McArthur')
    reporting_parser.add_argument('ip', action='store',
                                  help='IP Address of the STB to Update (Required)')
    reporting_parser.add_argument('-rf_connection', action='store_true',
                                  help="simulate disconnection of RF feed.  ")
    reporting_parser.add_argument('-erlang_Connect', action='store_true',
                                  help='Connect to XMPP Erlang server (For access to Pidgin, XMPP remote) the STB reboots after commands have been sent.  If build is very old and script does not run because of new additions this should connect STB to Erlang server regardless')
    reporting_parser.add_argument('-reboot', action='store_true', help='Reboots STB')
    reporting_parser.add_argument('-read', action='store_true', help="return values for all reporting settings")
    reporting_parser.add_argument('-details', action='store_true', help="returns STB details; CDSN Serial number, mode")
    reporting_parser.add_argument('-options', action='store_true',
                                  help='Opens a menu to individually set the main reporting settings')
    reporting_parser.add_argument('--debug', action='store_true', help='Debug Printing')

    return reporting_parser.parse_args()

def sshConnection(ip): #Create SSH connection to STB
    args = get_args()
    if args.debug:
        print ('Using paramiko to create SSH shell')
    print('calling paramiko')
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print ('Trying to connect to', ip)
    ssh.connect(ip, port, username, password)
    print ('Connected to', ip)
 
def sshSendCommand(command):
    stdin, stdout, stderr = ssh.exec_command(command, timeout=5)
    stdin.close()
    args = get_args()
    if args.debug:
        print ('command sent,  Stdout is variable lines err is variable err')
    global lines
    lines = stdout.readlines()
    global err
    err = stderr.readlines()
    
def sshCommand(command): #Send command to STB and return stdout and stderr, only for developing new areas
    args = get_args()
    if args.debug:
        print ('sshCommand prints stdout, stderr')
    print ('sending Command: ' + command)
    sshSendCommand(command)
    print(*lines, sep = ",")
    print('stderr', err)

def sshSQLCommand(command): #Send SQL commands to STB and return stdout printing results on seperate lines
                            #Timout - if timeout is breached, 5 seconds, it considereds the connection to be lost
                            #and attempts to reconnect to STB followed by sending the command 
    #global lines
    try:
        sshSendCommand(command)
        print(*lines)
        return True

    except Exception as e:
        print("Connection lost : %s" %e)
        print('trying to reconnect')
        args = get_args()
        ip = args.ip
        sshConnection(ip)
        sshSendCommand(command)
        print(*lines)
        return False

def sshCmd(command): #Send command to STB no confirmation no STB response required
    try:
        sshSendCommand(command)
        print ('Command Sent:  ' + command)
        return True

    except Exception as e:
        print("Connection lost : %s" %e)
        print('trying to reconnect')
        args = get_args()
        ip = args.ip
        sshConnection(ip)
        sshSendCommand(command)
        print ('Command Sent:  ' + command)
        return False
    
def sshRespCommand(command, debug): #Send command to STB confirmation only no command sent shown
    
    try:
        if debug == True:
            print ('sending Command: ' + command)
        sshSendCommand(command)
        print(*lines)
        return True

    except Exception as e:
        print("Connection lost : %s" %e)
        print('trying to reconnect')
        args = get_args()
        ip = args.ip
        sshConnection(ip)
        sshSendCommand(command)
        print(*lines)
        return False
    
def sshSettingsCommand(command): #Send a settings command to STB and return stdout only
    #global lines
    try:
        print ('sending Command: ' + command)
        sshSendCommand(command)
        print(*lines)
        return True

    except Exception as e:
        print("Connection lost : %s" %e)
        print('trying to reconnect')
        args = get_args()
        ip = args.ip
        sshConnection(ip)
        sshSendCommand(command)
        print ('sending Command: ' + command)
        print(*lines)
        return False
    
def readSettings(command): # Send comand and print setting with a lot of the extra characters removed for ease of reading
    global stbReadSetting
    #stbSetting = ()
    global saveSetting
    try:
        sshSendCommand(command)
        settingsRead = lines[0]
        settingsRead = settingsRead.replace('OK:key', '')
        stbReadSetting = settingsRead.rstrip(' \r\n')
        print(stbReadSetting)
        saveSetting = stbReadSetting.rstrip('"\n')
        #print('Setting: ' + saveSetting)
        return True

    except Exception as e:
        print("Connection lost : %s" %e)
        print('trying to reconnect')
        args = get_args()
        ip = args.ip
        sshConnection(ip)
        print ('sending Command')
        sshSendCommand(command)
        settingsRead = lines[0]
        settingsRead = settingsRead.replace('OK:key', '')
        stbReadSetting = settingsRead.rstrip(' \r\n')
        print(stbReadSetting)
        saveSetting = stbReadSetting.rstrip('\n')
        #print('Setting: ' + saveSetting)
        return False
    
def close(): #To end the SSH connection 
    ssh.close()
    print ('Connection Closed')
    
def sshResolution(command): #Send command to STB to get the current screen resolution
    stdin, stdout, stderr = ssh.exec_command(command, timeout=5)
    stdin, stdout, stderr = ssh.exec_command(command)
    stdin.close()
    stderr.close()
    global lines
    lines = stdout.readlines()
    lines = lines.pop(9)
    lines = lines.rstrip('\n')
    print(lines)
    return True

def killApp(application):
    getpid = f'echo `pidof {application}`'
    readSettings(getpid)
    print(application + ' pid ' + stbReadSetting[:5])
    sshCmd(f'kill -9 {stbReadSetting[:5]}')
    readSettings(getpid)

def appConfigReportDelay(config): #Set Application Configuration, user input
    if config:
        print('config set')
        timeDelay = config

    else:
        timeDelay = input ('Enter Application Configuration time delay(default 86400): ')

    timeDelayStr = str(timeDelay)
    configCommand = 'settings_cli Set "tungsten.reporting_service.appConfigReportDelay" '
    global appConfigDelay
    appConfigDelay = configCommand + timeDelayStr
    print (appConfigDelay)

def model_type(): # get model type from the STB
    sshSendCommand('calljs "pace.config.getOemModelId()"')
    global box_type
    if len(lines) > 1 and lines[1]:
        mt_resp = lines[1]
        mt_resp1 = mt_resp.replace('   string ""', '')
        modelType = mt_resp1.rstrip('""\n')
        #print ('Model Type: ' + modelType)
        
        if modelType in ["0A", "2A"]:
            box_type = "iQ4"
            print('STB Type: ' + box_type)
            
        elif modelType in ["09", "89"]:
            box_type = "iQ3"
            print('STB Type: ' + box_type)
            
        elif modelType in ["0B", "2B"]:
            box_type = "iQ5"
            print('STB Type: ' + box_type)
    else:
        print ("'===ERROR RETURNING Model Type==='\n'" + ' try rebooting STB and try again' )
        close()
        
def getCDSN(): # Gets the STB's CDSN and sets it global as CDSN
    cdsn_cmd ='calljs "pace.CA.getSerialNumber(1)"'
    sshSendCommand(cdsn_cmd)
    if len(lines) > 1 and lines[1]:
        cdsn_resp = lines[1]
        cdsn_resp1 = cdsn_resp.replace('   string ""', '')
        global CDSN
        CDSN = cdsn_resp1.rstrip('""\n')
        print ('CDSN: ' + CDSN)
    else:
        print ("'===ERROR RETURNING SERIAL NUMBER==='\n'" + ' try rebooting STB and try again' )
        close()
        #exit(0)
        
def getSerialNumber():
    get_serial_cmd ='dbus-send --system --type=method_call --print-reply --dest=org.pace.s_man /s_man org.pace.s_man.get_serialisation_element_as_string string:"STB_SERIAL_NUMBER" '
    sshSendCommand(get_serial_cmd)
    stbSerialN = lines[1]
    stbSerialN = stbSerialN.replace('   string "', '')
    global serialNumber
    serialNumber = stbSerialN.rstrip('""\n')
    print('Serial Number:' + serialNumber)
        
def getVersion(): #Get STB current software version
    get_version_cmd ='calljs "pace.config.softwareVersion()" '
    sshSendCommand(get_version_cmd)
    stbSoftwareV = lines[1]
    stbSoftwareV = stbSoftwareV.replace('  string ""', '')
    global softwareVer
    softwareVer = stbSoftwareV.rstrip('""\n')
        
def getBuild():
    get_build_cmd ='calljs "pace.config.firmwareVersion()" '
    sshSendCommand(get_build_cmd)
    stbBuild = lines[1]
    stbBuild = stbBuild.replace('  string ""', '')
    global buildVer
    buildVer = stbBuild.rstrip('""\n')
        
def SoftwareDetails():
    getVersion()
    getBuild()
    print('Software Version:' + softwareVer + '    Build Version:' + buildVer)
    
def stbMacAddr(): # gets the STB's ethernet MAC address and sets it global as macaddr
    ifconfig ='/sbin/ifconfig'
    stdin, stdout, stderr = ssh.exec_command(ifconfig)
    stdin.close()
    stderr.close()
    global lines
    lines = stdout.readlines()
    eth0 = lines[0]
    macaddr1 = eth0.replace('eth0      Link encap:Ethernet  HWaddr ', '')
    global macaddr
    macaddr = macaddr1.rstrip(' \r\n')
    print ('MAC Address: ' + macaddr)
    
def getMode():
    stdin, stdout, stderr = ssh.exec_command('settings_cli get "tungsten.ux.DeliveryMode" ')
    print ('Sending Command: settings_cli get "tungsten.ux.DeliveryMode" ')
    stdin.close()
    stderr.close()
    global lines
    lines = stdout.readlines()
    settingsRead = lines[0]
    settingsRead = settingsRead.replace('OK:key "tungsten.ux.DeliveryMode" , "', '')
    global stbMode
    stbMode = settingsRead.rstrip('" \r\n')   
    print ('STB mode: ' + stbMode)
    
def changeMode(): # To change the STB's mode between IP and DSMCC
    getMode()
    confirm = input('Current STB mode is ' + stbMode + ' Are you sure want to continue enter Y : ')
                    
    if confirm == 'Y':
        try:
            while True:     
                modes = ("http", "dsmcc")
                modeChoosen = str(input('Enter required mode: http or dsmcc: '))
                if modeChoosen in modes:
                #if modeChoosen == modes[0] or modeChoosen == modes[1]:
                    print(modeChoosen + ' Selected')
                    command = 'settings_cli Set "tungsten.ux.DeliveryMode" '
                    global stbModeCommand
                    stbModeCommand = command + modeChoosen
                    sshSettingsCommand(stbModeCommand)
                    sshCmd('/sbin/reboot -d 5') #reboots the STB after a 5 second delay
                    print('rebooting STB')
                    close() # Closes SSH
                    sys.exit(0)
                                                            
                else:
                    print('Mode not recognised. Try again')
                continue
                                        
        except KeyboardInterrupt:
            print('CTRL+C Pressed')        
                
    else:
        print('Canceled')
          
def reporting_enable(enable):
    #print(enable)
    enableStr = str(enable)
    command = 'settings_cli Set "tungsten.ams.enabled" '
    global enableCommand
    enableCommand = command + enableStr
    print (enableCommand)

def server_URL(url):
    print('server URL =', url)
    configCommand = 'settings_cli set "tungsten.reporting_service.uri" '
    global server
    server = configCommand + url
    print(server)

def AmsID(ams):
    if ams:
        print('updateDelay time set')

    else:
        ams = input('Enter AmsID: ')

    command = 'settings_cli Set "tungsten.ams.AmsID" '
    global AmsID
    AmsID = command + ams
    print(AmsID)

def stbIP(): # User enters IP address for STB
    global userIp
    userIp = input ('Enter STB IP address: ')
    print (userIp)

def main():

    stbIP()
    sshConnection(userIp)
    sshSettingsCommand(updateDelay)
    sshSettingsCommand(appConfigDelay)
    close()

if __name__ == '__main__':
    main()
    