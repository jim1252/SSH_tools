#!/usr/bin/env python3
'''
File:           settings_tool.py
Brief:          Send a series of commands to a STB to provide correct settings
Author:         James McArthur
Contributors:   N/A

Copyright
---------
Copyright 2009-2023 Commscope Inc. All rights reserved.
This program is confidential and proprietary to Commscope Inc.
(CommScope), and may not be copied, reproduced, modified, disclosed to
others, published or used, in whole or in part, without the express
prior written permission of CommScope.
'''

import paramiko
import argparse
import sys
import os
import json
import sshCommands
import time

port =22
username ='root'
password = ' '
ip = ' '
ssh = paramiko.SSHClient()
cmd = sshCommands
url_reporting = 'https://8uc2224o95.execute-api.eu-west-2.amazonaws.com/default/reportingIon'
server = ' '
updateProfile = ' '
updateAlpha = ' '
updateWatermark = ' '
updateAutoTime = ' '
memTotal = ' '
audioDelay = ("0", "10", "20", "30", "40","50", "60", "70", "80", "90","100", "110", "120", "130", "140","150", "160", "170", "180", "190", "200")
audioAtt = ("0dB", "-3dB", "-6dB", "-9dB", "-11dB",)
playbackType = ("download", "stream")
audio = ("Dolby", "Stereo")
classificationAge = ("0", "5", "6", "7", "8", "9",)

stbDetails = {} # Create Dictionary for STB details
stbPrimary = {} # Create Dictionary for Primary Settings

def get_args():
    reporting_parser = argparse.ArgumentParser(description='To set the reporting settings on a STB', epilog='for additional help contact James McArthur')
    reporting_parser.add_argument('ip', action='store', help='IP Address of the STB to Update (Required)')
    reporting_parser.add_argument('-off', action='store_false',
                                  help='Sets "tungsten.ams.enabled" to false to turn off reporting, sets tungsten.ams.enabled" to true if not set')
    reporting_parser.add_argument('-time', action='store', type=int, choices=[5, 10, 15, 20, 30, 45, 60, 120, 240, 300, 600, 900, 1200, 1800, 3600],
                                  help='Sets the reporting time delay, optional argument')
    reporting_parser.add_argument('-config', action='store', type=int, choices=[60, 120, 240, 600, 1800, 3600],
                                  help='Sets the application Configuration time delay, optional argument')
    reporting_parser.add_argument('-URL_RS', action='store', nargs='?', default='"https://8uc2224o95.execute-api.eu-west-2.amazonaws.com/default/reportingIon"', 
                                  help='Set a different URL of the reporting server ')
    reporting_parser.add_argument('-reporting_off', action='store_false',
                                  help='Sets "tungsten.ams.enabled" to false to turn off reporting, sets tungsten.ams.enabled" to true if not set')
    reporting_parser.add_argument('-reporting_config', action='store_true',
                                  help="Set most used reporting settings.  To turn off reporting the arg 'reporting_off' needs to be set in the command line.")
    reporting_parser.add_argument('-rf_connection', action='store_true',
                                  help="simulate disconnection of RF feed.  ")
    reporting_parser.add_argument('-erlang_Connect', action='store_true',
                                  help='Connect to XMPP Erlang server (For access to Pidgin, XMPP remote) the STB reboots after commands have been sent')
    reporting_parser.add_argument('-reboot', action='store_true', help='Reboots STB')
    reporting_parser.add_argument('-read', action='store_true', help="return values for all reporting settings")
    reporting_parser.add_argument('-details', action='store_true', help="returns STB details; CDSN Serial number, mode")
    reporting_parser.add_argument('-options', action='store_true',
                                  help='Opens a menu to individually set the main reporting settings')
   
    return reporting_parser.parse_args()
    #print(vars(args))

def getSTBdetails():
    cmd.getCDSN() 
    cmd.model_type()
    stbDetails.update({"iQ": sshCommands.box_type}) #
    stbPrimary.update({"iQ": sshCommands.box_type})
    stbDetails.update({"CDSN": sshCommands.CDSN}) #add CDSN to stbDetail dictionary
    stbPrimary.update({"CDSN": sshCommands.CDSN})  # add CDSN to stbPrimary dictionary
    stbDetails.update({"IP": ip}) #add IP to stbDetail dictionary
    stbPrimary.update({"IP": ip})  # add IP to stbPrimary dictionary
    cmd.getSerialNumber()
    stbDetails.update({"serial Number": sshCommands.serialNumber}) # add serial number to stbDetail dictionary
    stbPrimary.update({"serial Number": sshCommands.serialNumber})
    cmd.SoftwareDetails()
    stbDetails.update({"software Version": sshCommands.softwareVer}) # add software version to stbDetail dictionary
    stbPrimary.update({"software Version": sshCommands.softwareVer})
    stbDetails.update({"build Number": sshCommands.buildVer}) # add software build number to stbDetail dictionary
    stbPrimary.update({"build Number": sshCommands.buildVer})
    cmd.getMode()
    stbDetails.update({"STB Mode": sshCommands.stbMode}) #add mode to stbDetail dictionary
    stbPrimary.update({"STB Mode": sshCommands.stbMode})

def reportingServer_URL():
    args = get_args()
    global url_reporting
    url_reporting = args.URL_RS
    print('server URL =', url_reporting)
    configCommand = 'settings_cli set "tungsten.reporting_service.uri" '
    global server
    server = configCommand + url_reporting
    print(server)

def reportingSetup():
    print('Will set STB to standard reporting settings to ensure reporting works.\n  If alternate settings are required set them in the command line.  Use --H in command line for help on available settings') 
    confirm = input('Do you wish to continue? enter Y : ')
                    
    if confirm == 'Y':
        args = get_args()
        #ip = args.ip
        reporting_time = args.time
        config = args.config
        reportingEnable = args.reporting_off
        options = args.options
        reportingServer_URL()
        cmd.reporting_enable(reportingEnable) # turn reporting on or off (True/False)
        cmd.reportingDelay(reporting_time) # set value reporting update delay
        cmd.appConfigReportDelay(config) # set value for app config delay
        if options != 1: # If from command line conection to STB needs to be established
            print('Open Connection')
            cmd.sshConnection(ip)
        print('Sending commands to STB')
        cmd.sshSettingsCommand('server')
        #cmd.sshSettingsCommand('settings_cli set "tungsten.reporting_service.uri" "https://8uc2224o95.execute-api.eu-west-2.amazonaws.com/default/reportingIon" ')
        cmd.sshSettingsCommand(cmd.enableCommand)
        cmd.sshSettingsCommand(cmd.updateDelay)
        cmd.sshSettingsCommand(cmd.appConfigDelay)
        
        if options != 1:
            print('Close Connection')
            cmd.close() # Close connection to the STB
                
    else:
        print('Reporting setup canceled')
             
def rf_feed():
    cmd.sshConnection(ip)
    print('Simulate RF feed Disconnect') 
    confirm = input('Enter Y to disconnect RF, anything else to reconnct RF: ')
                    
    if confirm == 'Y':
        cmd.sshSettingsCommand('calljs "pace.test.simulateDisconnectedFeed(true)"')
        print('RF Feeds Disconnected')
        
    else:
        cmd.sshSettingsCommand('calljs "pace.test.simulateDisconnectedFeed(false)"')
        print('RF Feeds Connected')

    print('Close Connection')
    cmd.close() # Close connection to the STB

def settingsRead():
    print('Read Settings')
    cmd.readSettings('settings_cli get "tungsten.ux.DeliveryMode" ')
    ss1 = sshCommands.saveSetting.replace('"tungsten.ux.DeliveryMode" , "', '')
    stbPrimary.update({"STB Mode": ss1})  # add STB auto Standby Time to stbPrimary dictionary
    cmd.readSettings('settings_cli get tungsten.ux.autoStandbyTimeout')
    ss1 = sshCommands.saveSetting.replace('"tungsten.ux.autoStandbyTimeout" , "', '')
    stbPrimary.update({"autoStandbyTimeout": ss1})  # add STB auto Standby Time to stbPrimary dictionary
    cmd.readSettings('settings_cli Get "tungsten.ams.enabled"')
    ss1 = sshCommands.saveSetting.replace('"tungsten.ams.enabled" , "', '')
    stbPrimary.update({"reportingEnabled": ss1})  # add STB ams/reporting enabled to stbPrimary dictionary
    cmd.readSettings('settings_cli Get "tungsten.ams.updateDelay" ')
    ss1 = sshCommands.saveSetting.replace('"tungsten.ams.updateDelay" , "', '')
    stbPrimary.update({"updateDelay": ss1})  # add Reporting message delay to stbPrimary dictionary
    cmd.readSettings('settings_cli Get "tungsten.reporting_service.appConfigReportDelay" ')
    ss1 = sshCommands.saveSetting.replace('"tungsten.reporting_service.appConfigReportDelay" , "', '')
    stbPrimary.update({"appConfigReportDelay": ss1})  # add Reporting Config delay to stbPrimary dictionary
    cmd.readSettings('settings_cli get tungsten.reporting_service.uri')
    ss1 = sshCommands.saveSetting.replace('"tungsten.reporting_service.uri" , "', '')
    stbPrimary.update({"reportinguri": ss1})  # add reporting uri to stbPrimary dictionary
    cmd.readSettings('settings_cli Get "tungsten.reporting_service.sendEventsToLocalFileOnly" ')
    ss1 = sshCommands.saveSetting.replace('"tungsten.reporting_service.sendEventsToLocalFileOnly" , "', '')
    stbPrimary.update({"sendEventsToLocalFileOnly": ss1})  # EventsToLocalFileOnly to stbPrimary dictionary
    cmd.readSettings('settings_cli Get "tungsten.ams.numEventsInBundle" ')
    ss1 = sshCommands.saveSetting.replace('"tungsten.ams.numEventsInBundle" , "', '')
    stbPrimary.update({"ams.numEventsInBundle": ss1})  # add reportingEventsInBundle to stbPrimary dictionary
    cmd.readSettings('settings_cli Get "tungsten.ams.cacheSize" ')
    ss1 = sshCommands.saveSetting.replace('"tungsten.ams.cacheSize" , "', '')
    stbPrimary.update({"ams.CacheSize": ss1})  # add reportingCacheSize to stbPrimary dictionary
    cmd.readSettings('settings_cli Get "tungsten.ams.AmsID"')
    ss1 = sshCommands.saveSetting.replace('"tungsten.ams.AmsID" , "', '')
    stbPrimary.update({"AmsID": ss1})  # add AmsID to stbPrimary dictionary
    cmd.readSettings('settings_cli Get "tungsten.watermark.profile"')
    ss1 = sshCommands.saveSetting.replace('"tungsten.watermark.profile" , "', '')
    stbPrimary.update({"watermark.profile": ss1})  # add STB waterwmark profile to stbPrimary dictionary
    cmd.readSettings('settings_cli Get "tungsten.watermark.alpha"')
    ss1 = sshCommands.saveSetting.replace('"tungsten.watermark.alpha" , "', '')
    stbPrimary.update({"watermark.alpha": ss1})  # add STB watermark alpha to stbPrimary dictionary
    cmd.readSettings('settings_cli Get "tungsten.watermark.enabled"')
    ss1 = sshCommands.saveSetting.replace('"tungsten.watermark.enabled" , "', '')
    stbPrimary.update({"watermark.enabled": ss1})  # add STB auto Standby Time to stbPrimary dictionary
    cmd.readSettings('settings_cli get "tungsten.ux.audioSettingsFormatSpdif"')
    ss1 = sshCommands.saveSetting.replace('"tungsten.ux.audioSettingsFormatSpdif" , "', '')
    stbPrimary.update({"audioSettingsFormatSpdif": ss1})
    cmd.readSettings('settings_cli get "tungsten.ux.audioSettingsFormatHdmi"')
    ss1 = sshCommands.saveSetting.replace('"tungsten.ux.audioSettingsFormatHdmi" , "', '')
    stbPrimary.update({"audioSettingsFormatHdmi": ss1})
    cmd.readSettings('settings_cli get "tungsten.ux.digitalAudioLevel"')
    ss1 = sshCommands.saveSetting.replace('"tungsten.ux.digitalAudioLevel" , "', '')
    stbPrimary.update({"digitalAudioLevel": ss1})
    cmd.readSettings('settings_cli get "tungsten.ux.digitalAudioLevelHdmi"')
    ss1 = sshCommands.saveSetting.replace('"tungsten.ux.digitalAudioLevelHdmi" , "', '')
    stbPrimary.update({"digitalAudioLevelHdmi": ss1})
    cmd.readSettings('settings_cli get "tungsten.ux.audioDelay"')
    ss1 = sshCommands.saveSetting.replace('"tungsten.ux.audioDelay" , "', '')
    stbPrimary.update({"audioDelay": ss1})
    cmd.readSettings('settings_cli get "tungsten.ux.audioDelayHdmi"')
    ss1 = sshCommands.saveSetting.replace('"tungsten.ux.audioDelayHdmi" , "', '')
    stbPrimary.update({"audioDelayHdmi": ss1})
    cmd.readSettings('settings_cli get "tungsten.ux.parentalRating"')
    ss1 = sshCommands.saveSetting.replace('"tungsten.ux.parentalRating" , "', '')
    stbPrimary.update({"parentalRating": ss1})
    cmd.readSettings('settings_cli get "application.mainapp.UI_SETTING_PICTURE_RATING"')
    ss1 = sshCommands.saveSetting.replace('"application.mainapp.UI_SETTING_PICTURE_RATING" , "', '')
    stbPrimary.update({"UI_SETTING_PICTURE_RATING": ss1})
    cmd.readSettings('settings_cli Get "tungsten.ux.nonRatedPC"')
    ss1 = sshCommands.saveSetting.replace('"tungsten.ux.nonRatedPC" , "', '')
    stbPrimary.update({"nonRatedPC": ss1})
    cmd.readSettings('settings_cli get "application.mainapp.UI_SETTING_PIN_PURCHASE"')
    ss1 = sshCommands.saveSetting.replace('"application.mainapp.UI_SETTING_PIN_PURCHASE" , "', '')
    stbPrimary.update({"UI_SETTING_PIN_PURCHASE": ss1})
    cmd.readSettings('settings_cli get "application.mainapp.UI_SETTING_PIN_KEPT_PROGRAMS"')
    ss1 = sshCommands.saveSetting.replace('"application.mainapp.UI_SETTING_PIN_KEPT_PROGRAMS" , "', '')
    stbPrimary.update({"UI_SETTING_PIN_KEPT_PROGRAMS": ss1})
    cmd.readSettings('settings_cli get "application.mainapp.UI_SETTING_PIN_IP_VIDEO"')
    ss1 = sshCommands.saveSetting.replace('"application.mainapp.UI_SETTING_PIN_IP_VIDEO" , "', '')
    stbPrimary.update({"UI_SETTING_PIN_IP_VIDEO": ss1})
    cmd.readSettings('settings_cli get "tungsten.ux.ParentalPincode"')
    ss1 = sshCommands.saveSetting.replace('"tungsten.ux.ParentalPincode" , "', '')
    stbPrimary.update({"ParentalPincode": ss1})
    cmd.readSettings('settings_cli get "application.mainapp.UI_SETTING_BANDWIDTH_QUALITY"')
    ss1 = sshCommands.saveSetting.replace('"application.mainapp.UI_SETTING_BANDWIDTH_QUALITY" , "', '')
    stbPrimary.update({"UI_SETTING_BANDWIDTH_QUALITY": ss1})
    cmd.readSettings('settings_cli get "application.mainapp.UI_SETTING_POSTCARDS_ENABLED"')
    ss1 = sshCommands.saveSetting.replace('"application.mainapp.UI_SETTING_POSTCARDS_ENABLED" , "', '')
    stbPrimary.update({"UI_SETTING_POSTCARDS_ENABLED": ss1})
    cmd.readSettings('settings_cli get "application.mainapp.UI_SETTING_DOWNLOAD_QUALITY"')
    ss1 = sshCommands.saveSetting.replace('"application.mainapp.UI_SETTING_DOWNLOAD_QUALITY" , "', '')
    stbPrimary.update({"UI_SETTING_DOWNLOAD_QUALITY": ss1})
    cmd.readSettings('settings_cli get "application.mainapp.UI_SETTING_PPV_PLAYBACK_TYPE"')
    ss1 = sshCommands.saveSetting.replace('"application.mainapp.UI_SETTING_PPV_PLAYBACK_TYPE" , "', '')
    stbPrimary.update({"UI_SETTING_PPV_PLAYBACK_TYPE": ss1})
    cmd.readSettings('settings_cli get "application.mainapp.UI_SETTING_ON_DEMAND_PLAYBACK_TYPE"')
    ss1 = sshCommands.saveSetting.replace('"application.mainapp.UI_SETTING_ON_DEMAND_PLAYBACK_TYPE" , "', '')
    stbPrimary.update({"UI_SETTING_ON_DEMAND_PLAYBACK_TYPE": ss1})
    cmd.readSettings('settings_cli get "application.mainapp.UI_SETTING_BUFFER_SIZE"')
    ss1 = sshCommands.saveSetting.replace('"application.mainapp.UI_SETTING_BUFFER_SIZE" , "', '')
    stbPrimary.update({"UI_SETTING_BUFFER_SIZE": ss1})
    cmd.readSettings('settings_cli get "application.mainapp.UI_SETTING_VOICE_ENABLED"')
    ss1 = sshCommands.saveSetting.replace('"application.mainapp.UI_SETTING_VOICE_ENABLED" , "', '')
    stbPrimary.update({"UI_SETTING_VOICE_ENABLED": ss1})
    cmd.readSettings('settings_cli get "tungsten.ux.hdmiCecControlSetting"')
    ss1 = sshCommands.saveSetting.replace('"tungsten.ux.hdmiCecControlSetting" , "', '')
    stbPrimary.update({"hdmiCecControlSetting": ss1})
    cmd.readSettings('settings_cli get "tungsten.ux.hdmiCecVolumeControlSetting"')
    ss1 = sshCommands.saveSetting.replace('"tungsten.ux.hdmiCecVolumeControlSetting" , "', '')
    stbPrimary.update({"hdmiCecVolumeControlSetting": ss1})

def stbReboot():
    cmd.sshCmd('/sbin/reboot -d 5') #reboots the STB after a 5 second delay
    print('rebooting STB')
    cmd.close() # Closes SSH
    sys.exit(0) #Exit Settings script

def writeDetailsFile(): #writes STB deatils to a text file called stbDetails
    with open ('stbDetails.txt', 'w', encoding='UTF-8') as f: # Opens file
        for key, value in stbDetails.items(): # stbDetails - dictionary containing info
            f.write('%s:%s\n' % (key, value)) #writes each key on a new line in text file
    #detailsFile.close() #Close file

def writeSettingsFile(): #writes user settings from dict stbPrimary to json file stbSettings.json
    with open('stbSettings.json', 'w', encoding='UTF-8') as write_file:
        json.dump(stbPrimary, write_file)

def readSettingsFile():  #read settings json file shows user the settings values and updates dict stbPrimary
    try:
        with open("stbSettings.json", "r", encoding='UTF-8') as read_file:
            stbPrimary.update (json.load(read_file))
            print(stbPrimary)
            '''
            stbPrimary.update({"CDSN": jsonRead["CDSN"]})
            stbPrimary.update({"updateDelay": jsonRead["updateDelay"]})
            stbPrimary.update({"appConfigReportDelay": jsonRead["appConfigReportDelay"]})
            stbPrimary.update({"autoStandbyTimeout": jsonRead["autoStandbyTimeout"]})
            stbPrimary.update({"reportinguri": jsonRead["reportinguri"]})
            stbPrimary.update({"reportingEnabled": jsonRead["reportingEnabled"]})
            stbPrimary.update({"watermark.profile": jsonRead["watermark.profile"]})
            stbPrimary.update({"watermark.alpha": jsonRead["watermark.alpha"]})
            stbPrimary.update({"watermark.enabled": jsonRead["watermark.enabled"]})
            stbPrimary.update({"ParentalPincode": jsonRead["ParentalPincode"]})
            #stbPrimary.update({"appConfigReportDelay": jsonRead["appConfigReportDelay"]})
            '''
    except FileNotFoundError: # only used if file has not yet been created
        print('User settings file has not yet been created, please create one by running writing settings to file')

def getUserSettings(): # read user settings save in dict stbPrimary and write to file
    settingsRead()
    '''
    cmd.readSettings('settings_cli Get "tungsten.ams.updateDelay" ')
    ss1 = sshCommands.saveSetting.replace('"tungsten.ams.updateDelay" , "', '')
    stbPrimary.update({"updateDelay": ss1})  # add Reporting message delay to stbPrimary dictionary
    
    cmd.readSettings('settings_cli Get "tungsten.reporting_service.appConfigReportDelay" ')
    ss1 = sshCommands.saveSetting.replace('"tungsten.reporting_service.appConfigReportDelay" , "', '')
    stbPrimary.update({"appConfigReportDelay": ss1})  # add Reporting Config delay to stbPrimary dictionary
    
    cmd.readSettings('settings_cli get tungsten.ux.autoStandbyTimeout')
    ss1 = sshCommands.saveSetting.replace('"tungsten.ux.autoStandbyTimeout" , "', '')
    stbPrimary.update({"autoStandbyTimeout": ss1})  # add STB auto Standby Time to stbPrimary dictionary

    cmd.readSettings('settings_cli get tungsten.reporting_service.uri')
    ss1 = sshCommands.saveSetting.replace('"tungsten.reporting_service.uri" , "', '')
    stbPrimary.update({"reportinguri": ss1})  # add reporting uri to stbPrimary dictionary

    cmd.readSettings('settings_cli Get "tungsten.ams.enabled"')
    ss1 = sshCommands.saveSetting.replace('"tungsten.ams.enabled" , "', '')
    stbPrimary.update({"reportingEnabled": ss1})  # add STB ams/reporting enabled to stbPrimary dictionary

    cmd.readSettings('settings_cli Get "tungsten.watermark.profile"')
    ss1 = sshCommands.saveSetting.replace('"tungsten.watermark.profile" , "', '')
    stbPrimary.update({"watermark.profile": ss1})  # add STB waterwmark profile to stbPrimary dictionary
    
    cmd.readSettings('settings_cli Get "tungsten.watermark.alpha"')
    ss1 = sshCommands.saveSetting.replace('"tungsten.watermark.alpha" , "', '')
    stbPrimary.update({"watermark.alpha": ss1})  # add STB watermark alpha to stbPrimary dictionary
    
    cmd.readSettings('settings_cli Get "tungsten.watermark.enabled"')
    ss1 = sshCommands.saveSetting.replace('"tungsten.watermark.enabled" , "', '')
    stbPrimary.update({"watermark.enabled": ss1})  # add STB auto Standby Time to stbPrimary dictionary
    
    cmd.readSettings('settings_cli get "tungsten.ux.ParentalPincode"')
    ss1 = sshCommands.saveSetting.replace('"tungsten.ux.ParentalPincode" , "', '')
    stbPrimary.update({"ParentalPincode": ss1})  # add Reporting message delay to stbPrimary dictionary
    '''
    print(stbPrimary)
    writeSettingsFile() # Write settings to file

def updateUserSettings(): # gets settings from json file puts them in dict stbPrimary and sends them to the STB
    readSettingsFile() # read the json file shows it on screen
    primarySet = stbPrimary['updateDelay']
    cmd.sshCmd("""settings_cli set "tungsten.ams.updateDelay"%s """ % primarySet)
    primarySet = stbPrimary['appConfigReportDelay']
    cmd.sshCmd("""settings_cli set "tungsten.reporting_service.appConfigReportDelay"%s """ % primarySet)
    primarySet = stbPrimary['autoStandbyTimeout']
    cmd.sshCmd("""settings_cli set "tungsten.ux.autoStandbyTimeout"%s """ % primarySet)
    primarySet = stbPrimary['reportingEnabled']
    cmd.sshCmd("""settings_cli set "tungsten.ams.enabled"%s """ % primarySet)
    primarySet = stbPrimary['reportinguri']
    cmd.sshCmd("""settings_cli set "tungsten.reporting_service.uri"%s """ % primarySet)
    primarySet = stbPrimary['watermark.profile']
    cmd.sshCmd("""settings_cli set "tungsten.watermark.profile"%s """ % primarySet)
    primarySet = stbPrimary['watermark.alpha']
    cmd.sshCmd("""settings_cli set "tungsten.watermark.alpha"%s """ % primarySet)
    primarySet = stbPrimary['watermark.enabled']
    cmd.sshCmd("""settings_cli set "tungsten.watermark.enabled"%s """ % primarySet)
    primarySet = stbPrimary['ParentalPincode']
    cmd.sshCmd("""settings_cli set "tungsten.ux.ParentalPincode"%s """ % primarySet)

def sendErlangSetup():
    print('Sending commands to set STB to ejabbered Server')
    erlangSQLite()
    # erlangJid = """sqlite3 /mnt/ffs/settings/active.db 'update active_table set value = "trustedJids=remotedvr@cobalt.pace.com,remotedvr@elements-dev.xyz,remotedvr@elements.commscope.com,automation2.0@elements-dev.xyz,scripts@elements-dev.xyz,human@elements-dev.xyz", modified = "true" where key = "tungsten.provisioning.xmppConfiguration" ' """
    command = """sqlite3 /mnt/ffs/settings/active.db 'update active_table set value = "trustedJids=remotedvr@cobalt.pace.com,remotedvr@elements-dev.xyz,remotedvr@xmpp.connectedhomesolutions.net,remotedvr@elements.commscope.com,scripts@elements-dev.xyz,human@elements-dev.xyz,automation2.0@elements-dev.xyz,remotedvr@xmpp.connectedhomesolutions.net,automation2.0@xmpp.connectedhomesolutions.net,scripts@xmpp.connectedhomesolutions.net,human@xmpp.connectedhomesolutions.net,foxtel_automation@managed.dev-xmpp.foxtel.com.au,foxtel_automation@xmpp.thomasholtdrive.com", modified = "true" where key = "tungsten.provisioning.xmppConfiguration";' """
    cmd.sshCmd(erlangSQLite)
    cmd.sshCmd(command)
    cmd.sshCmd('settings_cli Set "application.mainapp.AUTOMATION_2_0_ENABLED" true')
    cmd.sshCmd('settings_cli Set "application.mainapp.AUTOMATION_2_0_XMPP_DESTINATION" COMMSCOPE_A2.0')
    cmd.sshCmd('/sbin/reboot -d 2') #reboots the STB after a 2 second delay
    print('Commands sent to STB to connect to Erlang Server')

def erlangSQLite():
    start = "sqlite3 /mnt/ffs/settings/active.db 'UPDATE active_table set value="
    end = "'"
    global erlangSQLite
    erlangSQLite = start + '"description=server,user=' + cmd.CDSN + '.iq3,password=' + cmd.CDSN + \
                   '.iq3,domain=xmpp.connectedhomesolutions.net,resource=iq3,auth=digest" where ' \
                   'key like "tungsten.provisioning.xmpp1" '+ end
    print (erlangSQLite)

def main():
    print('main running')
    args = get_args()
    global ip
    ip = args.ip
    details = args.details
    #enable = args.off
    read = args.read
    reboot = args.reboot
    options = args.options
    reporting_config = args.reporting_config
    rf_connection = args.rf_connection
    erlang_Connect = args.erlang_Connect
    print('ip =', ip)
        
    if reboot == 1:
        cmd.sshConnection(ip)
        stbReboot()
    
    elif read == 1:
        #print('read settings')
        cmd.sshConnection(ip)
        settingsRead()
        cmd.close()
        
    elif details == 1:  
        cmd.sshConnection(ip)
        getSTBdetails()
        print('Got')
        
    elif rf_connection == 1:
        print('RF Connected')
        rf_feed()
        
    elif erlang_Connect == 1:
        cmd.sshConnection(ip)
        cmd.getCDSN()
        sendErlangSetup()
        sys.exit(0)

    elif reporting_config == 1:
        print('set reporting')
        reportingSetup()

    else:
        print('open')
        cmd.sshConnection(ip)
        getSTBdetails()
        writeDetailsFile()
        
        try:
            while True:
                print('\n CDSN: ' + stbDetails["CDSN"] + '   IP addr: ' + stbDetails["IP"] + '   Software Version:' + stbDetails["software Version"])
                options =  """    
                Select a setting to change: \n
                *** Main Settings ***
                   1 - Search Settings
                   2 - Send own command, typed in full
                   3 - Set Auto Standby Time
                   4 - Simulate RF Disconnect
                   5 - Change STB Mode IP\Hybrid
                   6 - Connect to XMPP Erlang server (Pidgin, XMPP remote)
                   7 - FSR - Full System Reset
                   8 - Screen Resolution for streaming assets, 8c for continuous
                   9 - Connect to PTS "services.t1.foxtel-iq.com.au"
                   10 - TBC
                   11 - Reset Keep stream as default message  
                   12 - View bookablePromos available \n
                *** Tester Settings ***
                  20 - Application tools 
                  21 - Reporting Settings
                  22 - Watermark Settings
                  23 - Low memory Values
                  24 - Time management Priorities 
                  25 - Point STB at different provisioning service \n                
                *** Developer Settings ***
                  30 - Download in IP mode
                  31 - Disable "reset iQ system" \n
                *** User Settings ***
                  40 - Audio Settings 
                  41 - Parental control Settings
                  42 - Streaming and download settings
                  43 - Remote Control Settings \n
                *** System Information ***
                  50 - System Details
                  51 - Software Details
                  52 - Read all settings \n 
                *** Testers Default Settings ***
                  60 - Write User Settings To File
                  61 - Read User Settings from file
                  62 - Update User settings from File\n
                   r - Reboot STB
                   q - quit \n
                  """
                print(options)
                x = input('>: ')

                if x == '1':
                    userInput = input ('Enter Text such as; Netflix, watermark, audio, PIN, to return all results containing the searched text. \n  Enter text to search STB settings: ')
                    print(userInput)
                    cmd.sshSettingsCommand(f'settings_cli getall | grep {userInput}')
                
                elif x ==  '2':
                    print('Type full command to be sent to STB: ')
                    userInput = input ('Enter Text such as; Netflix, watermark, audio, PIN, to return all results containing the searched text. \n  Enter text to search STB settings: ')
                    print(userInput)
                    cmd.sshSettingsCommand(userInput)
                
                elif x == '3':
                    try:
                        while True:
                            print('current Auto Standby time is: ')
                            cmd.readSettings('settings_cli get tungsten.ux.autoStandbyTimeout')
                            ss1 = sshCommands.saveSetting.replace('"tungsten.ux.autoStandbyTimeout" , "', '')
                            stbPrimary.update({"autoStandbyTimeout": ss1})  # add STB auto Standby Time to stbPrimary dictionary
                            enter = input('Enter Auto Standby time (Default 14400): ')
                            autoTime = str(enter) #autoTime new time to set STB to
                            cmd.readSettings('settings_cli Get "tungsten.ux.autoStandbyWarning"')
                            ss1 = sshCommands.saveSetting.replace('"tungsten.ux.autoStandbyWarning" , "', '')
                            stbPrimary.update({"autoStandbyWarning": ss1})  # add Standby warning to stbPrimary dictionary
                            if autoTime != '60':
                                print ('time' + autoTime)
                                cmd.sshSettingsCommand('settings_cli set tungsten.ux.autoStandbyWarning "60"')
                            command = 'settings_cli set "tungsten.ux.autoStandbyTimeout"  '
                            global updateAutoTime
                            updateAutoTime = command + autoTime
                            print(updateAutoTime)
                            cmd.sshSettingsCommand(updateAutoTime)
                            cmd.readSettings('settings_cli get tungsten.ux.autoStandbyTimeout')
                            ss1 = sshCommands.saveSetting.replace('"tungsten.ux.autoStandbyTimeout" , "', '')
                            stbPrimary.update({"autoStandbyTimeout": ss1})  # add STB auto Standby Time to stbPrimary dictionary
                            break
                    except KeyboardInterrupt:
                        continue
                
                elif x == '4': # Change RF Feed connection
                    try:
                        while True:
                            options = """\n      Simulate RF Disconnection     \n                            
                 1 - Disconnect 
                 2 - Connect
                 q - quit
                 b - back                 """
                            print(options)
                            x = input('>: ')

                            if x== '1':
                                cmd.sshSettingsCommand('calljs "pace.test.simulateDisconnectedFeed(true)"')
                                print('RF Feeds Disconnected')
                                
                            elif x == '2':
                                cmd.sshSettingsCommand('calljs "pace.test.simulateDisconnectedFeed(false)"')
                                print('RF Feeds Connected')
                                
                            elif x == 'q':
                                cmd.close()
                                sys.exit(0)

                            elif x == 'b':
                                break

                            else:
                                print('WARNING: {} is an unknown option. Try again'.format(x))
                            continue

                    except KeyboardInterrupt:
                        print('CTRL+C Pressed. Shutting Down')
                        cmd.close()
                
                elif x == '5': # Switch mode between IP and dsmcc
                    cmd.changeMode() 
                
                elif x == '6': #Connect to XMPP server(Erlang)
                    cmd.getCDSN()
                    sendErlangSetup()
                    sys.exit(0) 
                
                elif x == '7': #FSR
                    confirm = input('Are you sure want to perform a Full system reset on your STB? To continue enter Y : ')
                    
                    if confirm == 'Y':
                        cmd.sshCmd('touch /mnt/ffs/reset')
                        cmd.sshCmd('sync')
                        stbReboot()
                                
                    else:
                        print('FSR canceled')
                        continue
                
                elif x == '8': # Get screen resolution
                    print('Screen Resolution: ')
                    cmd.sshResolution('cat /proc/brcm/video_decoder')
                    continue
                
                elif x == '8c': # Get screen resolution continuous
                    print('Screen Resolution: \n Press CTRL-C to stop')
                    try:
                        while True:
                            cmd.sshResolution('cat /proc/brcm/video_decoder')
                            time.sleep(5)
                            continue
                            
                    except KeyboardInterrupt:
                        print('CTRL+C Pressed. Shutting Down')
                        cmd.close()
                                    
                elif x == '9': # Connect to PTS
                    try:
                        while True:
                            options = """\n      Connect to PTS Enviroment     \n                            
                 1 - Connect to settings_cli Set "application.mainapp.epg.sdp_host" "services.t1.foxtel-iq.com.au" 
                 2 - Disconnect from PTS settings_cli Set "application.mainapp.epg.sdp_host" "services.p1.foxtel-iq.com.au"
                 q - quit
                 b - back                 """
                            print(options)
                            x = input('>: ')

                            if x== '1':
                                cmd.sshSettingsCommand('settings_cli Set "application.mainapp.epg.sdp_host" "services.t1.foxtel-iq.com.au"')
                                print('Connecting to PTS')
                                stbReboot()
                                
                            elif x == '2':
                                cmd.sshSettingsCommand('settings_cli Set "application.mainapp.epg.sdp_host" "services.p1.foxtel-iq.com.au"')
                                print('Disconnecting from PTS')
                                stbReboot()
                                
                            elif x == 'q':
                                cmd.close()
                                sys.exit(0)

                            elif x == 'b':
                                break

                            else:
                                print('WARNING: {} is an unknown option. Try again'.format(x))
                            continue

                    except KeyboardInterrupt:
                        print('CTRL+C Pressed. Shutting Down')
                        cmd.close()
                                
                elif x == '11':
                    cmd.sshSettingsCommand('settings_cli set "application.mainapp.UI_SETTING_OD_PLAYBACK_TYPE_DIALOG_SHOWN" "FALSE"')
                    stbReboot()

                elif x == '12':
                    cmd.sshSettingsCommand('ls -l /tmp/bookablePromos')
                
                elif x == '20':
                    try:
                        while True:
                            options = """\n    Application Tools \n                            
                 1 - Get Application PIDS 
                 2 - Status Netflix
                 3 - Status Amazon
                 4 - Status WPE Browser, FTA, Paramount+ 
                 5 - Status Disney
                 6 - Status YouTube
                 7 - Kill Netflix 
                 8 - Kill Amazon
                 9 - Kill WPE Browser, FTA, Paramount+ 
                 10 - Kill Disney Plus
                 11 - Kill YouTube
                 20 - Memory allocation tool
                 21 - Netflix DRM 
                 r - reboot
                 q - quit
                 b - back
                 """
                            print(options)
                            x = input('>: ')
                            
                            if x== '1':
                                print('Netflix PID:')
                                cmd.readSettings('echo `pidof netflix`')
                                
                                print('Amazon PID:')
                                cmd.readSettings('echo `pidof ignition`')
                                
                                print('WPE Browser, FTA Paramount+ PID:')
                                cmd.readSettings('echo `pidof cog`')
                                
                                print('Disney Plus PID:')
                                cmd.readSettings('echo `pidof merlin`')
                                
                                print('YouTube:')
                                cmd.readSettings('echo `pidof loader_app`')
                                
                            elif x == '2':
                                cmd.sshSettingsCommand('ps aux | grep Netflix')
                                
                            elif x == '3':
                                cmd.sshSettingsCommand('ps aux | grep [i]gnition')
                                
                            elif x == '4':
                                cmd.sshSettingsCommand('ps aux | grep [c]og')
                                
                            elif x == '5':
                                cmd.sshSettingsCommand('ps aux | grep -i [d]isneyplus')
                                
                            elif x == '6':
                                cmd.sshSettingsCommand(' ps aux | grep [c]obalt')
                                
                            elif x == '7':
                                cmd.killApp('netflix')
                                
                            elif x == '8':
                                cmd.killApp('ignition')
                                
                            elif x == '9':
                                cmd.killApp('cog')
                                
                            elif x == '10':
                                cmd.killApp('merlin')
                                
                            elif x == '11':
                                cmd.killApp('loader_app')
                                
                            elif x == '20':
                                global memTotal
                                memTotal = int(0)
                                os.system('cls')
                                try:
                                    while True:
                                        options = """   Memory Setter \n                            
                     1 - Allocate Memory
                     2 - Free up Memory
                     r - Reboot STB
                     b - back
                     """
                                        print(options)
                                        print('Total memory Allocated: ' + str(memTotal))
                                        x = input('>: ')
                                        
                                        if x== '1':
                                            memValue = int(input('Enter value of memory to allocate : '))
                                            memTotal = memTotal + memValue
                                            print('Total memory Allocated: ' + str(memTotal))                                            
                                            commanda = '/usr/bin/allocateAndFreeMemory.sh a '
                                            updateMem = commanda + str(memValue)
                                            print(updateMem)
                                            cmd.sshCmd(updateMem)
                                            os.system('cls')
                                            
                                        elif x == '2':
                                            memValue = int(input('Enter value of memory to free up : '))
                                            memTotal = memTotal - memValue
                                            print('Total memory Allocated: ' + str(memTotal))
                                            commandf = '/usr/bin/allocateAndFreeMemory.sh f '
                                            updateMem = commandf + str(memValue)
                                            print(updateMem)
                                            cmd.sshCmd(updateMem)
                                            os.system('cls')
                                            
                                        elif x == 'r':
                                            stbReboot()
                                        
                                        elif x == 'b':
                                            break
                                          
                                        else:
                                            print('WARNING: {} is an unknown option. Try again'.format(x))
                                        continue
                                        
                                except KeyboardInterrupt:
                                    print('CTRL+C Pressed. Shutting Down')
                                    cmd.close()
                                
                            elif x == '21':
                                try:
                                    while True:
                                        options = """\n    Netflix DRM \n                            
                     1 - Check Netflix DRM 
                     2 - Remove Netflix DRM
                     q - quit
                     b - back
                     """
                                        print(options)
                                        x = input('>: ')
                                        
                                        if x== '1':
                                            cmd.sshSettingsCommand('ls -l /mnt/ffs/permanent/infield_drm/')
                                            continue
                                            
                                        if x == '2':
                                            cmd.sshCmd('rm -rf /mnt/ffs/permanent/infield_drm/')
                                            continue
                                                         
                                        if x == 'q':
                                            cmd.close()
                                            sys.exit(0)
                                 
                                        elif x == 'b':
                                            break
                                          
                                        else:
                                            print('WARNING: {} is an unknown option. Try again'.format(x))
                                        continue
                                        
                                except KeyboardInterrupt:
                                    print('CTRL+C Pressed. Shutting Down')
                                    cmd.close()
                                                                
                            elif x == 'r':
                                stbReboot()
                            
                            elif x == 'q':
                                cmd.close()
                                sys.exit(0)
                     
                            elif x == 'b':
                                break
                              
                            else:
                                print('WARNING: {} is an unknown option. Try again'.format(x))
                            continue
                            
                    except KeyboardInterrupt:
                        print('CTRL+C Pressed. Shutting Down')
                        cmd.close()
                        
                elif x == '21': # Reporting settings
                    try:
                        while True:
                            options = """     Reporting
                 0 - Read settings
                 1 - Set update Delay
                 2 - Set application Config Report Delay
                 3 - Enable Reporting
                 4 - Set URL
                 5 - Send Events to Local File Only
                 6 - Set Event Bundle Size
                 7 - Set Event Cache size
                 8 - Set AmsID
                 9 - Configure STB for Reporting \n
                 q - quit
                 b - back
                 """
                            print(options)
                            x = input('>: ')
                            
                            if x == '0':
                                cmd.readSettings('settings_cli Get "tungsten.ams.enabled" ')
                                cmd.readSettings('settings_cli Get "tungsten.ams.updateDelay" ')
                                cmd.readSettings('settings_cli Get "tungsten.reporting_service.appConfigReportDelay" ')
                                cmd.readSettings('settings_cli Get "tungsten.reporting_service.uri" ')
                                cmd.readSettings('settings_cli Get "tungsten.reporting_service.sendEventsToLocalFileOnly" ')
                                cmd.readSettings('settings_cli Get "tungsten.ams.numEventsInBundle" ')
                                cmd.readSettings('settings_cli Get "tungsten.ams.cacheSize" ')
                                cmd.readSettings('settings_cli Get "tungsten.ams.AmsID" ')
                       
                            elif x == '1': # Reporting Delay
                                timeDelay = 0
                                cmd.reportingDelay(timeDelay)
                                cmd.sshSettingsCommand(cmd.updateDelay)
                                continue

                            elif x == '2': # App Config Delay
                                config = 0
                                cmd.appConfigReportDelay(config)
                                cmd.sshSettingsCommand(cmd.appConfigDelay)
                                continue

                            elif x == '3': # # Enable/Disable reporting
                                enable = input('Enter "True" to enable, or "False" to disable reporting: ')
                                cmd.reporting_enable(enable)
                                cmd.sshSettingsCommand(cmd.enableCommand)
                                continue

                            elif x == '4': # Change reporing URL (Reporting server that the STB sends to)
                                reportingUrl = (input('Enter required URL, leave blank to set default: "hhttps://8uc2224o95.execute-api.eu-west-2.amazonaws.com/default/reportingIon": ')
                                    or "https://8uc2224o95.execute-api.eu-west-2.amazonaws.com/default/reportingIon")
                                cmd.server_URL(reportingUrl)
                                cmd.sshSettingsCommand(cmd.server)
                                continue

                            elif x == '5': #  Enable Disable send reporting to file
                                disable = input('Enter "True" to enable, or "False" to disable, Send Events to Local File Only: ')
                                cmd.send_to_file(disable)
                                cmd.sshSettingsCommand(cmd.fileCommand)
                                continue

                            elif x == '6': # Change amount of events in a bundle
                                bundle = input('Enter Required number of events required in Bundle(default = 500): ')
                                bundleStr = str(bundle)
                                command = 'settings_cli Set "tungsten.ams.numEventsInBundle" '
                                eventBundle = command + bundleStr
                                print(eventBundle)
                                cmd.sshSettingsCommand(eventBundle)
                                continue

                            elif x == '7': # Change Cached memory size
                                cache = input('Enter Required Cache size (default = 1000): ')
                                cacheStr = str(cache)
                                command = 'settings_cli Set "tungsten.ams.cacheSize" '
                                cacheSize = command + cacheStr
                                print(cacheSize)
                                cmd.sshSettingsCommand(cacheSize)
                                continue

                            elif x == '8': #Get AMS ID (used to be used to find STB on reporting server
                                ams = 0
                                cmd.AmsID(ams)
                                print(cmd.AmsID)
                                cmd.sshCommand(cmd.AmsID)
                                continue
                                
                            elif x == '9':
                                reportingSetup()
                                
                            elif x == 'q':
                                cmd.close()
                                sys.exit(0)
                
                            elif x == 'b':
                                break
                            
                            elif x == 'r':
                                stbReboot()
                            
                            else:
                                print('WARNING: {} is an unknown option. Try again'.format(x))
                            continue
                            
                    except KeyboardInterrupt:
                        print('CTRL+C Pressed. Shutting Down')
                        cmd.close()
                                                      

                    
                elif x == '22':
                    try:
                        while True:
                            options = """    watermark
                            
                 0 - read Watermark settings
                 1 - Watermark profile
                 2 - Watermark alpha
                 3 - Watermark Enable \n
                 q - quit
                 b - back
                 """
                            print(options)
                            x = input('>: ')
                            
                            if x== '0':
                                cmd.readSettings('settings_cli get tungsten.watermark.profile')
                                cmd.readSettings('settings_cli get tungsten.watermark.alpha')
                                cmd.readSettings('settings_cli get tungsten.watermark.enabled')
                               
                            elif x == '1':
                                enter = input('Enter require Watermark Profile(2,255): ')
                                profile = str(enter)
                                command = 'settings_cli Set "tungsten.watermark.profile" '
                                global updateProfile
                                updateProfile = command + profile
                                print(updateProfile)
                                cmd.sshSettingsCommand(updateProfile)
                                
                            elif x == '2':
                                enter = input('Enter require Watermark Alpha(1-100): ')
                                alpha = str(enter)
                                command = 'settings_cli Set "tungsten.watermark.alpha" '
                                global updateAlpha
                                updateAlpha = command + alpha
                                print(updateAlpha)
                                cmd.sshSettingsCommand(updateAlpha)
                                
                            elif x == '3':
                                enter = input('Enter "True" to enable, or "False" to disable Watermark: ')
                                watermark = str(enter)
                                command = 'settings_cli Set "tungsten.watermark.enabled" '
                                global updateWatermark
                                updateWatermark = command + watermark
                                cmd.sshSettingsCommand(updateWatermark)
                                
                            elif x == 'q':
                                cmd.close()
                                sys.exit(0)
                            
                            elif x == 'b':
                                break
                              
                            else:
                                print('WARNING: {} is an unknown option. Try again'.format(x))
                            continue
                            
                    except KeyboardInterrupt:
                        print('CTRL+C Pressed. Shutting Down')
                        cmd.close()    

                
                elif x == '23':
                    try:
                        while True:
                            options = """               Low memory value settings \n                            
                 0 - Read all Low Momory Values \n
                    ***NETFLIX*** \n
                 10 - Read Netflix Low Memory settings
                 11 - Netflix free memory low mark
                 12 - Netflix free memory req for foreground
                 13 - Netflix free process memory mark
                 14 - Read Netflix free memory req for suspend \n
                 ***Amazon PV*** \n
                 20 - Amazon Low Memory Settings
                 21 - Amazon free memory low mark
                 22 - Amazon free memory req for foreground
                 23 - Amazon free process memory mark
                 24 - Amazon free memory req for suspend \n
                    ***WPE*** \n
                 30 - WPE Low Memory Settings
                 31 - WPE free memory low mark
                 32 - WPE free memory req for foreground
                 33 - WPE free process memory mark
                 34 - WPE free memory req for suspend \n
                    ***Youtube*** \n
                 40 - Youtube Low Memory Settings
                 41 - Youtube free memory low mark 
                 42 - Netflix free memory req for foreground \n             
                    
                 q - quit
                 b - Back
                 """
                            print(options)
                            x = input('>: ')
                            
                            if x== '0':
                                cmd.readSettings('settings_cli get tungsten.appmanager.netflix_free_memory_low_mark')
                                cmd.readSettings('settings_cli get appmanager.netflix_free_memory_req_for_foreground')
                                cmd.readSettings('settings_cli get appmanager.netflix_process_memory_mark')
                                cmd.readSettings('settings_cli get appmanager.netflix_free_memory_req_for_suspend')
                                cmd.readSettings('settings_cli get tungsten.appmanager.wpe_free_memory_low_mark')
                                cmd.readSettings('settings_cli get tungsten.appmanager.wpe_free_memory_req_for_foreground')
                                cmd.readSettings('settings_cli get tungsten.appmanager.wpe_process_memory_mark')
                                cmd.readSettings('settings_cli get tungsten.appmanager.wpe_free_memory_req_for_suspend')
                                cmd.readSettings('settings_cli get tungsten.appmanager.amazon_free_memory_low_mark')
                                cmd.readSettings('settings_cli get tungsten.appmanager.amazon_free_memory_req_for_foreground')
                                cmd.readSettings('settings_cli get tungsten.appmanager.amazon_free_memory_req_for_suspend')
                                cmd.readSettings('settings_cli get tungsten.appmanager.amazon_process_memory_mark')
                                cmd.readSettings('settings_cli get tungsten.appmanager.cobalt_free_memory_low_mark')
                                cmd.readSettings('settings_cli get tungsten.appmanager.cobalt_free_memory_req_for_foreground')
                                cmd.readSettings('settings_cli get tungsten.appmanager.cobalt_free_memory_req_for_suspend')
                                cmd.readSettings('settings_cli get tungsten.appmanager.cobalt_process_memory_mark')
                                
                            elif x == '10': # Netflix
                                cmd.readSettings('settings_cli get tungsten.appmanager.netflix_free_memory_low_mark')
                                cmd.readSettings('settings_cli get appmanager.netflix_free_memory_req_for_foreground')
                                cmd.readSettings('settings_cli get appmanager.netflix_process_memory_mark')
                                cmd.readSettings('settings_cli get appmanager.netflix_free_memory_req_for_suspend')
                                
                            elif x == '11': # Netflix
                                enter = input('Enter required value for Netflix free memory low mark: ')
                                lowMark = str(enter)
                                command = 'settings_cli set "tungsten.appmanager.netflix_free_memory_low_mark" '
                                netflixLowMark = command + lowMark
                                cmd.sshSettingsCommand(netflixLowMark)
                                
                            elif x == '12': # Netflix
                                enter = input('Enter required value for Netflix free memory req for foreground: ')
                                lowMark = str(enter)
                                command = 'settings_cli set "tungsten.appmanager.netflix_free_memory_req_for_foreground" '
                                netflixForeground = command + lowMark
                                cmd.sshSettingsCommand(netflixForeground)
                                
                            elif x == '13': # Netflix
                                enter = input('Enter required value for Netflix free process memory mark: ')
                                lowMark = str(enter)
                                command = 'settings_cli set "tungsten.appmanager.netflix_process_memory_mark" '
                                netflixProcess = command + lowMark
                                cmd.sshSettingsCommand(netflixProcess)
                                
                            elif x == '14': # Netflix
                                enter = input('Enter required value for Netflix free memory req for suspend: ')
                                lowMark = str(enter)
                                command = 'settings_cli set "tungsten.appmanager.netflix_free_memory_req_for_suspend" '
                                netflixSuspend = command + lowMark
                                cmd.sshSettingsCommand(netflixSuspend)
                                
                            elif x == '20': # Amazon Browser
                                cmd.readSettings('settings_cli get tungsten.appmanager.amazon_free_memory_low_mark')
                                cmd.readSettings('settings_cli get tungsten.appmanager.amazon_free_memory_req_for_foreground')
                                cmd.readSettings('settings_cli get tungsten.appmanager.amazon_free_memory_req_for_suspend')
                                cmd.readSettings('settings_cli get tungsten.appmanager.amazon_process_memory_mark')
                                
                            elif x == '21': # Amazon Browser
                                enter = input('Enter required value for Amazon free memory low mark: ')
                                lowMark = str(enter)
                                command = 'settings_cli set "tungsten.appmanager.amazon_free_memory_low_mark" '
                                amazonLowMark = command + lowMark
                                cmd.sshSettingsCommand(amazonLowMark)
                                
                            elif x == '22': # Amazon Browser
                                enter = input('Enter required value for Amazon free memory req for foreground: ')
                                lowMark = str(enter)
                                command = 'settings_cli set "tungsten.appmanager.amazon_free_memory_req_for_foreground" '
                                amazonForeground = command + lowMark
                                cmd.sshSettingsCommand(amazonForeground)
                                
                            elif x == '23': # Amazon Browser
                                enter = input('Enter required value for Amazon free process memory mark: ')
                                lowMark = str(enter)
                                command = 'settings_cli set "tungsten.appmanager.amazon_process_memory_mark" '
                                amazonProcess = command + lowMark
                                cmd.sshSettingsCommand(amazonProcess)
                                
                            elif x == '24': # Amazon Browser
                                enter = input('Enter required value for Amazon free memory req for suspend: ')
                                lowMark = str(enter)
                                command = 'settings_cli set "tungsten.appmanager.amazon_free_memory_req_for_suspend" '
                                amazonSuspend = command + lowMark
                                cmd.sshSettingsCommand(amazonSuspend)
                                
                            elif x == '30': # WPE Browser
                                cmd.readSettings('settings_cli get tungsten.appmanager.wpe_free_memory_low_mark')
                                cmd.readSettings('settings_cli get tungsten.appmanager.wpe_free_memory_req_for_foreground')
                                cmd.readSettings('settings_cli get tungsten.appmanager.wpe_process_memory_mark')
                                cmd.readSettings('settings_cli get tungsten.appmanager.wpe_free_memory_req_for_suspend')
                                
                            elif x == '31': # WPE Browser
                                enter = input('Enter required value for WPE Browser free memory low mark: ')
                                lowMark = str(enter)
                                command = 'settings_cli set "tungsten.appmanager.wpe_free_memory_low_mark" '
                                wpeLowMark = command + lowMark
                                cmd.sshSettingsCommand(wpeLowMark)
                                
                            elif x == '32': # WPE Browser
                                enter = input('Enter required value for WPE Browser free memory req for foreground: ')
                                lowMark = str(enter)
                                command = 'settings_cli set "tungsten.appmanager.wpe_free_memory_req_for_foreground" '
                                wpeForeground = command + lowMark
                                cmd.sshSettingsCommand(wpeForeground)
                                
                            elif x == '33': # WPE Browser
                                enter = input('Enter required value for WPE Browser free process memory mark: ')
                                lowMark = str(enter)
                                command = 'settings_cli set "tungsten.appmanager.wpe_process_memory_mark" '
                                wpeProcess = command + lowMark
                                cmd.sshSettingsCommand(wpeProcess)
                                
                            elif x == '34': # WPE Browser
                                enter = input('Enter required value for WPE Browser free memory req for suspend: ')
                                lowMark = str(enter)
                                command = 'settings_cli set "tungsten.appmanager.wpe_free_memory_req_for_suspend" '
                                wpeSuspend = command + lowMark
                                cmd.sshSettingsCommand(wpeSuspend)
                                
                            elif x == '40': # Youtube
                                cmd.readSettings('settings_cli get tungsten.appmanager.cobalt_free_memory_low_mark')
                                cmd.readSettings('settings_cli get tungsten.appmanager.cobalt_free_memory_req_for_foreground')
                                cmd.readSettings('settings_cli get tungsten.appmanager.cobalt_free_memory_req_for_suspend')
                                cmd.readSettings('settings_cli get tungsten.appmanager.cobalt_process_memory_mark')
                                
                            elif x == '41': # Youtube
                                enter = input('Enter required value for Youtube free memory low mark (default = 153600): ')
                                lowMark = str(enter)
                                command = 'settings_cli set "tungsten.appmanager.cobalt_free_memory_low_mark" '
                                youtubeLowMark = command + lowMark
                                cmd.sshSettingsCommand(youtubeLowMark)
                                
                            elif x == '42': # Youtube
                                enter = input('Enter required value for Youtube free memory req for foreground (default value = 225280): ')
                                lowMark = str(enter)
                                command = 'settings_cli set "tungsten.appmanager.cobalt_free_memory_req_for_foreground" '
                                youtubeForeground = command + lowMark
                                cmd.sshSettingsCommand(youtubeForeground)
                                
                            elif x == 'q':
                                cmd.close()
                                sys.exit(0)    
                                
                            elif x == 'b':
                                break
                              
                            else:
                                print('WARNING: {} is an unknown option. Try again'.format(x))
                            continue
                            
                    except KeyboardInterrupt:
                        print('CTRL+C Pressed. Shutting Down')
                        cmd.close()
                
                elif x == '24':
                    try:
                        while True:
                            options = """\n    Time Management settings \n                            
                 0 - read time mangement priorities
                 1 - Reset time management priorities to default
                 2 - Set all time management priorities to 0 
                 b - back
                 """
                            print(options)
                            x = input('>: ')
                            
                            if x== '0':
                                cmd.readSettings('settings_cli get tungsten.timemanagement.CablePriority')
                                cmd.readSettings('settings_cli get tungsten.timemanagement.SatellitePriority')
                                cmd.readSettings('settings_cli get tungsten.timemanagement.HTTPSPriority')
                                cmd.readSettings('settings_cli get tungsten.timemanagement.TerrestrialPriority')
                                cmd.readSettings('settings_cli get tungsten.timemanagement.IPPriority')
                                
                            elif x == '1':
                                confirm = input('You are about to reset all time management priorities to default this will also reboot the STB do you want to continue Y : ')
                    
                                if confirm == 'Y':
                                    cmd.sshCmd('settings_cli set tungsten.timemanagement.CablePriority 1')
                                    cmd.sshCmd('settings_cli set tungsten.timemanagement.SatellitePriority 2')
                                    cmd.sshCmd('settings_cli set tungsten.timemanagement.HTTPSPriority 3')
                                    cmd.sshCmd('settings_cli set tungsten.timemanagement.TerrestrialPriority 4')
                                    cmd.sshCmd('settings_cli set tungsten.timemanagement.IPPriority 0')
                                    stbReboot()
                                    
                            elif x == '2':
                                confirm = input('You are about to set all time management priorities to 0 this will also reboot the STB do you want to continue Y : ')
                    
                                if confirm == 'Y':
                                    cmd.sshCmd('settings_cli set tungsten.timemanagement.CablePriority 0')
                                    cmd.sshCmd('settings_cli set tungsten.timemanagement.SatellitePriority 0')
                                    cmd.sshCmd('settings_cli set tungsten.timemanagement.HTTPSPriority 0')
                                    cmd.sshCmd('settings_cli set tungsten.timemanagement.TerrestrialPriority 0')
                                    cmd.sshCmd('settings_cli set tungsten.timemanagement.IPPriority 0')
                                    stbReboot()
                                    
                            elif x == '3':
                                print('enable')
                                
                            elif x == 'q':
                                cmd.close()
                                sys.exit(0)
                     
                            elif x == 'b':
                                break
                              
                            else:
                                print('WARNING: {} is an unknown option. Try again'.format(x))
                            continue
                            
                    except KeyboardInterrupt:
                        print('CTRL+C Pressed. Shutting Down')
                        cmd.close() 
                
                elif x == '25':
                    try:
                        while True:
                            options = """\n    Point STB at different provisioning services \n                            
                 0 - read
                 1 - Set provisioning.play_service to server http://tu-services.arrisi.com:5001
                 2 - Set default provisioning.play_service 
                 3 - Set provisioning.cdn_url_service to server http://tu-services.arrisi.com:5001
                 4 - Set default provisioning.cdn_url_service
                 5 - Set own  provisioning.play_service
                 6 - Set own  provisioning.cdn_url_service
                 q - quit
                 b - back
                 """
                            print(options)
                            x = input('>: ')
                            
                            if x== '0':
                                cmd.readSettings('settings_cli Get "tungsten.provisioning.play_service"')
                                cmd.readSettings('settings_cli get "tungsten.provisioning.cdn_url_service"')
                                                               
                            elif x == '1':
                                cmd.sshSettingsCommand('settings_cli Set "tungsten.provisioning.play_service" "http://tu-services.arrisi.com:5001/queryPlayService"')
                                 
                            elif x == '2':
                                cmd.sshSettingsCommand('settings_cli Set "tungsten.provisioning.play_service" "https://services.p1.foxtel-iq.com.au/fxtl/v1/play"')
                                
                            elif x == '3':
                                cmd.sshSettingsCommand('settings_cli Set "tungsten.provisioning.cdn_url_service" "http://tu-services.arrisi.com:5001/queryPlayService"')
                                
                            elif x == '4':
                                cmd.sshSettingsCommand('settings_cli Set "tungsten.provisioning.cdn_url_service" "https://services.p1.foxtel-iq.com.au/fxtl/v1/cdnUrl"')
                                
                            elif x == '5':
                                enter = input('Enter youe URL of provisioning play Service eg "https://fake-services.catalogue.foxtel.com.au/fxtl/v1/play" : ')
                                playService = str(enter)
                                command = 'settings_cli Set "tungsten.provisioning.play_service" '
                                updatePlayService = command + playService
                                #print (updatePlayService)
                                cmd.sshSettingsCommand(updatePlayService)
                                
                            elif x == '6':
                                enter = input('Enter youe URL of provisioning cdn_url service eg "https://fake-services.catalogue.foxtel.com.au/fxtl/v1/play" : ')
                                cdn_url = str(enter)
                                command = 'settings_cli Set "tungsten.provisioning.cdn_url_service" '
                                update_cdn_url = command + cdn_url
                                #print (update_cdn_url)
                                cmd.sshSettingsCommand(update_cdn_url)
                            
                            elif x == 'q':
                                cmd.close()
                                sys.exit(0)
                     
                            elif x == 'b':
                                break
                              
                            else:
                                print('WARNING: {} is an unknown option. Try again'.format(x))
                            continue
                            
                    except KeyboardInterrupt:
                        print('CTRL+C Pressed. Shutting Down')
                        cmd.close()
                
                elif x == '30': # Download in IP mode
                    try:
                        while True:
                            options = """\n      Set Allow Download in IP Mode      \n                            
                 0 - Check current setting
                 1 - Allow Download in IP mode 
                 2 - Turn off Download in IP Mode
                 3 - When renting from store Download/Stream
                 4 - When watching Foxtel On Demand content Download/Stream
                 q - quit
                 b - back                 """
                            print(options)
                            x = input('>: ')

                            if x== '0':
                                print('Checking Allow Download in IP Mode settings an user download setting values')
                                cmd.sshSettingsCommand('settings_cli Get "application.mainapp.ALLOW_DOWNLOAD_IN_IP_MODE"')
                                cmd.readSettings('settings_cli get "application.mainapp.UI_SETTING_PPV_PLAYBACK_TYPE"')
                                cmd.readSettings('settings_cli get "application.mainapp.UI_SETTING_ON_DEMAND_PLAYBACK_TYPE"')
                                                                                           
                            elif x== '1': #Allow IP download
                                cmd.sshSettingsCommand('settings_cli Set "application.mainapp.ALLOW_DOWNLOAD_IN_IP_MODE" "true"')
                                print('Setting Allow Download in IP Mode to True')
                                                               
                            elif x == '2': #Don't allow IP Download
                                cmd.sshSettingsCommand('settings_cli Set "application.mainapp.ALLOW_DOWNLOAD_IN_IP_MODE" "false"')
                                print('Setting Allow Download in IP Mode to False')
                                                                
                            elif x == '3':  #TVOD playback type
                                pbTypeChoosen = str(input('Enter required mode: stream or download: '))
                                if pbTypeChoosen in playbackType:
                                    print(pbTypeChoosen + ' Selected')
                                    cmd.sshSettingsCommand("""calljs "oxygen.settings.ui.set('UI_SETTING_PPV_PLAYBACK_TYPE','%s')"  """"" % pbTypeChoosen)
                                    
                                else:
                                    print('Audio format not recognised. Try again')
                                
                            elif x == '4':  #SVOD playback type                          
                                pbTypeChoosen = str(input('Enter required mode: stream or download: '))
                                if pbTypeChoosen in playbackType:
                                    print(pbTypeChoosen + ' Selected')
                                    cmd.sshSettingsCommand("""calljs "oxygen.settings.ui.set('UI_SETTING_ON_DEMAND_PLAYBACK_TYPE','%s')"  """"" % pbTypeChoosen)
                                    
                                else:
                                    print('Audio format not recognised. Try again')                      
                            
                            elif x == 'q':
                                cmd.close()
                                sys.exit(0)

                            elif x == 'b':
                                break

                            else:
                                print('WARNING: {} is an unknown option. Try again'.format(x))
                            continue

                    except KeyboardInterrupt:
                        print('CTRL+C Pressed. Shutting Down')
                        cmd.close()
                
                elif x == '31': # Disable Reset iQ system 
                    try:
                        while True:
                            options = """\n      Set Allow Download in IP Mode      \n                            
                 0 - Check current setting
                 1 - Disable "reset iQ System"
                 2 - Enable "reset iQ system"
                 3 - Delete "reset iQ system" setting
                 q - quit
                 b - back                 """
                            print(options)
                            x = input('>: ')

                            if x== '0':
                                print('Checking reset iQ system setting')
                                cmd.sshSettingsCommand('settings_cli Get "application.mainapp.SYSTEM_RESET_DISABLED"')
                                #cmd.readSettings('settings_cli get "application.mainapp.UI_SETTING_PPV_PLAYBACK_TYPE"')
                                 
                            elif x== '1': #Disable
                                cmd.sshSettingsCommand('settings_cli set "application.mainapp.SYSTEM_RESET_DISABLED" "true"')
                                print('Disable "reset iQ System"')
                                stbReboot()
                                                               
                            elif x == '2': #Enable
                                cmd.sshSettingsCommand('settings_cli set "application.mainapp.SYSTEM_RESET_DISABLED" "false"')
                                print('Enable "reset iQ System"')
                                stbReboot()
                                
                            elif x == '3': #Delete
                                cmd.sshSettingsCommand('settings_cli del "application.mainapp.SYSTEM_RESET_DISABLED"')
                                print('Deleting "reset iQ System" setting')
                                            
                            elif x == 'q':
                                cmd.close()
                                sys.exit(0)

                            elif x == 'b':
                                break

                            else:
                                print('WARNING: {} is an unknown option. Try again'.format(x))
                            continue

                    except KeyboardInterrupt:
                        print('CTRL+C Pressed. Shutting Down')
                        cmd.close()
                
                elif x == '40':
                    try:
                        while True:
                            options = """    Audio settings \n                            
                 0 - read Audio Settings 
                 1 - SPDIF Format
                 2 - HDMI Format
                 3 - SPDIF Attenuation
                 4 - HDMI Attenuation
                 5 - SPDIF Delay
                 6 - HDMI Delay
                 q - quit
                 b - back
                 """
                            print(options)
                            x = input('>: ')
                            
                            if x== '0':
                                cmd.readSettings('settings_cli get "tungsten.ux.audioSettingsFormatSpdif"')
                                cmd.readSettings('settings_cli get "tungsten.ux.audioSettingsFormatHdmi"')
                                cmd.readSettings('settings_cli get "tungsten.ux.digitalAudioLevel"')
                                cmd.readSettings('settings_cli get "tungsten.ux.digitalAudioLevelHdmi"')
                                cmd.readSettings('settings_cli get "tungsten.ux.audioDelay"')
                                cmd.readSettings('settings_cli get "tungsten.ux.audioDelayHdmi"')
                                
                            elif x == '1': #SPDIF Format
                                try:
                                    while True:    
                                        a_format = str(input('Enter Spdif Audio format, Dolby or Stereo: '))
                                        if a_format in audio:
                                            print(a_format + ' Selected')
                                            command = 'settings_cli set "tungsten.ux.audioSettingsFormatSpdif" '
                                            spdifFormat = command + a_format
                                            cmd.sshSettingsCommand(spdifFormat)
                                            break
                                             
                                        print('Audio format not recognised. Try again')
                                        continue
                                        
                                except KeyboardInterrupt:
                                    print('CTRL+C Pressed')          
                                
                            elif x == '2': #HDMI Format
                                try:
                                    while True:    
                                        a_format = str(input('Enter HDMI Audio format, Dolby or Stereo: '))
                                        if a_format in audio:
                                            print(a_format + ' Selected')
                                            command = 'settings_cli set "tungsten.ux.audioSettingsFormatHdmi" '
                                            hdmiFormat = command + a_format
                                            cmd.sshSettingsCommand(hdmiFormat)
                                            break
                                            
                                        print('Audio format not recognised. Try again')
                                        
                                except KeyboardInterrupt:
                                    print('CTRL+C Pressed')
                                    
                            elif x == '3': # SPDIF Attenuation
                                try:
                                    while True:    
                                        attenuation = str(input('Enter SPDIF Audio Attenuation, Enter 0dB -3dB -6dB -9dB -11dB: '))
                                        if attenuation in audioAtt:
                                            print(attenuation + ' Selected')
                                            command = 'settings_cli set "tungsten.ux.digitalAudioLevel" '
                                            spdifAtt = command + attenuation
                                            cmd.sshSettingsCommand(spdifAtt)
                                            break
                                            
                                        print('Audio attenuation level not recognised. Try again')
                                        
                                except KeyboardInterrupt:
                                    print('CTRL+C Pressed')
                                        
                            elif x == '4': # HDMI Attenuation
                                try:
                                    while True:    
                                        attenuation = str(input('Enter HDMI Audio Attenuation, Enter 0dB -3dB -6dB -9dB -11dB: '))
                                        if attenuation in audioAtt:
                                            print(attenuation + ' Selected')
                                            command = 'settings_cli set "tungsten.ux.digitalAudioLevelHdmi" '
                                            hdmiAtt = command + attenuation
                                            cmd.sshSettingsCommand(hdmiAtt)
                                            break
                                            
                                        print('Audio attenuation level not recognised. Try again')
                                        
                                except KeyboardInterrupt:
                                    print('CTRL+C Pressed')
                                        
                            elif x == '5': # SPDIF Delay
                                try:
                                    while True:    
                                        spdif_time = str(input('Enter SPDIF Audio Delay, Enter 0 10 20 30 40 50 60 70 80 90 100 110 120 130 150 160 170 180 190 200: '))
                                        if spdif_time in audioDelay:
                                            print(spdif_time + ' Selected')
                                            command = 'settings_cli set "tungsten.ux.audioDelay" '
                                            spdifDelay = command + spdif_time
                                            cmd.sshSettingsCommand(spdifDelay)
                                            break
                                        
                                        print('Audio delay not recognised. Try again')
                                        
                                except KeyboardInterrupt:
                                    print('CTRL+C Pressed')

                            elif x == '6': # HDMI Delay
                                try:
                                    while True:    
                                        hdmi_time = str(input('Enter HDMI Audio Delay, Enter 0 10 20 30 40 50 60 70 80 90 100 110 120 130 150 160 170 180 190 200: '))
                                        if hdmi_time in audioDelay:
                                            print(hdmi_time + ' Selected')
                                            command = 'settings_cli set "tungsten.ux.audioDelayHdmi" '
                                            hdmiDelay = command + hdmi_time
                                            cmd.sshSettingsCommand(hdmiDelay)
                                            break
                                         
                                        print('Audio delay not recognised. Try again')
                                        
                                except KeyboardInterrupt:
                                    print('CTRL+C Pressed')
                                
                            elif x == 'q':
                                cmd.close()
                                sys.exit(0)
                     
                            elif x == 'b':
                                break
                              
                            else: 
                                print('WARNING: {} is an unknown option. Try again'.format(x))
                            continue
                            
                    except KeyboardInterrupt:
                        print('CTRL+C Pressed. Shutting Down')
                        cmd.close()
                
                elif x == '41':
                    try:
                        while True:
                            options = """\n    PIN and parental controls \n                            
                 0 - read settings
                 1 - PIN entry required for programs classified
                 2 - Hide info and posters for programs classified
                 3 - PIN Entry required (for Non Classified programs)
                 4 - PIN to Purchase
                 5 - PIN Protect Kept Programs
                 6 - PIN for Foxtel IP Video
                 7 - Change iQ Name
                 8 - Change Parental PIN Number
                 q - quit
                 b - back
                 """
                            print(options)
                            x = input('>: ')
                            
                            if x== '0':
                                cmd.readSettings('settings_cli get tungsten.ux.parentalRating')
                                print('0 = None 5 = PG and above 6 = M and above 7 = MA15+ and above 8 = AV15+ and above 9 = R18+')
                                cmd.readSettings('settings_cli get application.mainapp.UI_SETTING_PICTURE_RATING')
                                print('0 = None 5 = PG and above 6 = M and above 7 = MA15+ and above 8 = AV15+ and above 9 = R18+')
                                cmd.readSettings('settings_cli Get "tungsten.ux.nonRatedPC"')
                                cmd.readSettings('settings_cli get application.mainapp.UI_SETTING_PIN_PURCHASE')
                                cmd.readSettings('settings_cli get application.mainapp.UI_SETTING_PIN_KEPT_PROGRAMS')
                                cmd.readSettings('settings_cli get application.mainapp.UI_SETTING_PIN_IP_VIDEO')
                                cmd.readSettings('settings_cli get "tungsten.ux.ParentalPincode"')
                                
                            elif x == '1':
                                try:
                                    while True:
                                        pinEntry = str(input('Enter one of the following classifications, Enter \n 0 = None \n 5 = PG and above \n 6 = M and above \n 7 = MA15+ and above \n 8 = AV15+ and above \n 9 = R18+ \n: '))
                                        if pinEntry in classificationAge:
                                            print(pinEntry + ' Selected')
                                            command = 'settings_cli set "tungsten.ux.parentalRating" '
                                            pinEntryClass = command + pinEntry
                                            cmd.sshSettingsCommand(pinEntryClass)
                                            break
                                     
                                        print('PIN classification code is not recognised. Try again')
                                         
                                except KeyboardInterrupt:
                                    print('CTRL+C Pressed')
                                    
                            elif x == '2':
                                try:
                                    while True:
                                        pictureRating = str(input('Enter one of the following classifications, Enter \n 0 = None \n 5 = PG and above \n 6 = M and above \n 7 = MA15+ and above \n 8 = AV15+ and above \n 9 = R18+ \n: '))
                                        if pictureRating in classificationAge:
                                            print(pictureRating + ' Selected')
                                            cmd.sshSettingsCommand("""calljs "oxygen.settings.ui.set('UI_SETTING_PICTURE_RATING','%s')"  """"" % pictureRating)
                                            break
                                            
                                        print('Hide picture classification code is not recognised. Try again')
                                        
                                except KeyboardInterrupt:
                                    print('CTRL+C Pressed')
                             
                            elif x == '3':
                                enter = input('Enter "TRUE" to enable, or "FALSE" to disable PIN Entry required for Non Classified programs: ')
                                nonRatedPC = str(enter)
                                command = 'settings_cli Set "tungsten.ux.nonRatedPC" '
                                updateNonRatedPC = command + nonRatedPC
                                cmd.sshSettingsCommand(updateNonRatedPC)
                                
                            elif x == '4':
                                enter = input('Enter "TRUE" to enable, or "FALSE" to disable PIN to Purchase: ')
                                PINPurchase = str(enter)
                                cmd.sshSettingsCommand("""calljs "oxygen.settings.ui.set('UI_SETTING_PIN_PURCHASE','%s')"  """"" % PINPurchase)
                                
                            elif x == '5':
                                enter = input('Enter "TRUE" to enable, or "FALSE" to disable PIN Protect Kept Programs: ')
                                PINKept = str(enter)
                                cmd.sshSettingsCommand("""calljs "oxygen.settings.ui.set('UI_SETTING_PIN_KEPT_PROGRAMS','%s')"  """"" % PINKept)
                                
                            elif x == '6':
                                enter = input('Enter "TRUE" to enable, or "FALSE" to disable PIN for Foxtel IP Video: ')
                                ipVideo = str(enter)
                                cmd.sshSettingsCommand("""calljs "oxygen.settings.ui.set('UI_SETTING_PIN_IP_VIDEO','%s')"  """"" % ipVideo)
                                
                            elif x == '7':
                                enter = input('Enter New Name for STB: ')
                                iQName = str(enter)
                                cmd.sshSettingsCommand("""calljs "oxygen.settings.ui.set('UI_SETTING_STB_NAME','%s')"  """"" % iQName)
                                print('STB name changed to ' + iQName)
                                confirm = input('This requres a reboot of the STB to take effect, do you want to reboot now Y : ')
                                
                                if confirm == 'Y':
                                    stbReboot()
                                
                                else:
                                    print('change to STB name will take effect on next reboot')
                                    continue 
                                
                            elif x == '8':
                                enter = input('Enter New PIN: ')
                                changePIN = str(enter)
                                command = 'settings_cli Set "tungsten.ux.ParentalPincode" '
                                updateParentalPIN = command + changePIN
                                cmd.sshSettingsCommand(updateParentalPIN)
                                                           
                            elif x == 'q':
                                cmd.close()
                                sys.exit(0)
                     
                            elif x == 'b':
                                break
                              
                            else:
                                print('WARNING: {} is an unknown option. Try again'.format(x))
                            continue
                            
                    except KeyboardInterrupt:
                        print('CTRL+C Pressed.')
                        cmd.close()
                
                elif x == '42':
                    try:
                        while True:
                            options = """ \n   Streaming and Download Settings \n                            
                 0 - read Settings
                 1 - Streaming quality
                 2 - When fast forwarding or rewinding a stream, always show
                 3 - When Downloading to Library save as
                 4 - When renting from store Download/Stream
                 5 - When watching Foxtel On Demand content Download/Stream
                 6 - Download buffer size
                 q - quit
                 b - back
                 """
                            print(options)
                            x = input('>: ')
                            
                            if x== '0':
                                cmd.readSettings('settings_cli get "application.mainapp.UI_SETTING_BANDWIDTH_QUALITY"')
                                cmd.readSettings('settings_cli get "application.mainapp.UI_SETTING_POSTCARDS_ENABLED"')
                                cmd.readSettings('settings_cli get "application.mainapp.UI_SETTING_DOWNLOAD_QUALITY"')
                                cmd.readSettings('settings_cli get "application.mainapp.UI_SETTING_PPV_PLAYBACK_TYPE"')
                                cmd.readSettings('settings_cli get "application.mainapp.UI_SETTING_ON_DEMAND_PLAYBACK_TYPE"')
                                cmd.readSettings('settings_cli get "application.mainapp.UI_SETTING_BUFFER_SIZE"')
                                print('          0 = Auto 1 = Small 3 = Medium 10 = Large \n' )
                                
                            elif x == '1': #Streaming Quality
                                try:
                                    while True:    
                                        StreamingQuality = ("best", "low")
                                        spdif_format = str(input('Enter Spdif Audio format, best or low: '))
                                        if spdif_format in StreamingQuality:
                                            print(spdif_format + ' Selected')
                                            cmd.sshSettingsCommand("""calljs "oxygen.settings.ui.set('UI_SETTING_BANDWIDTH_QUALITY','%s')"  """"" % spdif_format)
                                            break   

                                        print('Audio format not recognised. Try again')
                                        
                                except KeyboardInterrupt:
                                    print('CTRL+C Pressed') 
                            
                            elif x == '2':                            
                                enter = input('When fast forwarding or rewinding a stream, always show: \n Enter "true" to for postcard enable or "false" for Full Screen View: ')
                                postcardEnabled = str(enter)
                                cmd.sshSettingsCommand("""calljs "oxygen.settings.ui.set('UI_SETTING_POSTCARDS_ENABLED','%s')"  """"" % postcardEnabled)
                                                                
                            elif x == '3': #Downloading to library 
                                print ('STB can only download in http - Current STM Mode:  ' + stbDetails["STB Mode"])
                                modeCheck = 'dsmcc'
                                if modeCheck in stbDetails.values():
                                    try:
                                        while True:    
                                            libraryQuality = ("uhd", "hd", "sd")
                                            library_format = str(input('Enter Format for downloading to Library, uhd or hd or sd: '))
                                            if library_format in libraryQuality:
                                                print(library_format + ' Selected')
                                                cmd.sshSettingsCommand("""calljs "oxygen.settings.ui.set('UI_SETTING_DOWNLOAD_QUALITY','%s')"  """"" % library_format)
                                                break
                                            
                                            print('Audio format not recognised. Try again')
                                                                                
                                    except KeyboardInterrupt:
                                        print('CTRL+C Pressed')
                                        
                                else:
                                    print ('STB is in IP Mode this setting is not available')
                                
                            elif x == '4':
                                print ('STB can only download in http - Current STM Mode:  ' + stbDetails["STB Mode"])
                                modeCheck = 'dsmcc'
                                if modeCheck in stbDetails.values():
                                    try:
                                        while True:     
                                            pbTypeChoosen = str(input('Enter required mode: stream or download: '))
                                            if pbTypeChoosen in playbackType:
                                                print(pbTypeChoosen + ' Selected')
                                                cmd.sshSettingsCommand("""calljs "oxygen.settings.ui.set('UI_SETTING_PPV_PLAYBACK_TYPE','%s')"  """"" % pbTypeChoosen)
                                                break
                                                
                                            print('Playback Type  not recognised. Try again')
                                
                                    except KeyboardInterrupt:
                                        print('CTRL+C Pressed')                                
                                
                                else:
                                    print ('STB is in IP Mode this setting is not available')
                                
                            elif x == '5':
                                print ('STB can only download in http - Current STM Mode:  ' + stbDetails["STB Mode"])
                                modeCheck = 'dsmcc'
                                if modeCheck in stbDetails.values():
                                    try:
                                        while True:     
                                            pbTypeChoosen = str(input('Enter required mode: stream or download: '))
                                            if pbTypeChoosen in playbackType:
                                                print(pbTypeChoosen + ' Selected')
                                                cmd.sshSettingsCommand("""calljs "oxygen.settings.ui.set('UI_SETTING_ON_DEMAND_PLAYBACK_TYPE','%s')"  """"" % pbTypeChoosen)
                                                break
                                                
                                            print('Playback Type  not recognised. Try again')
                                                                    
                                    except KeyboardInterrupt:
                                        print('CTRL+C Pressed')
                                
                                else:
                                    print ('STB is in IP Mode this setting is not available')
                                
                            elif x == '6':
                                print ('Current STM Mode:  ' + stbDetails["STB Mode"])
                                modeCheck = 'dsmcc'
                                if modeCheck in stbDetails.values():
                                    bufferSize = ("0", "1", "3", "10",)
                                    try:
                                        while True:     
                                            bufferChoosen = str(input('Enter the required buffer size: 0 = Auto 1 = Small 3 = Medium 10 = Large: '))
                                            if bufferChoosen in bufferSize:
                                                print(bufferChoosen + ' Selected')
                                                cmd.sshSettingsCommand("""calljs "oxygen.settings.ui.set('UI_SETTING_BUFFER_SIZE','%s')"  """"" % bufferChoosen)
                                                break
                                                
                                            print('Playback Type  not recognised. Try again')
                                                                    
                                    except KeyboardInterrupt:
                                        print('CTRL+C Pressed')
                                
                                else:
                                    print ('STB is in IP Mode this setting is not available')
                            
                            elif x == 'q':
                                cmd.close()
                                sys.exit(0)
                     
                            elif x == 'b':
                                break
                              
                            else:
                                print('WARNING: {} is an unknown option. Try again'.format(x))
                            continue
                            
                    except KeyboardInterrupt:
                        print('CTRL+C Pressed. Shutting Down')
                        cmd.close()     
                
                elif x == '43':
                    try:
                        while True:
                            options = """    Remote Control Settings \n                            
                 0 - read 
                 1 - Voice Setting
                 2 - HDMI-CEC Control
                 3 - HDMI-CEC Volume Control
                 q - quit
                 b - back
                 """
                            print(options)
                            x = input('>: ')
                            
                            if x== '0':
                                cmd.readSettings('settings_cli get application.mainapp.UI_SETTING_VOICE_ENABLED')
                                cmd.readSettings('settings_cli get tungsten.ux.hdmiCecControlSetting')
                                cmd.readSettings('settings_cli get tungsten.ux.hdmiCecVolumeControlSetting')
                                
                            elif x == '1':
                                enter = input('Enter "TRUE" to enable, or "FALSE" to disable Voice Control:  ')
                                voiceEnable = str(enter)
                                cmd.sshSettingsCommand("""calljs "oxygen.settings.ui.set('UI_SETTING_VOICE_ENABLED','%s')"  """"" % voiceEnable)
                                
                            elif x == '2':
                                enter = input('Enter "True" to enable, or "False" to disable HDMI-CEC Control: ')
                                cecControl = str(enter)
                                command = 'settings_cli Set "tungsten.ux.hdmiCecControlSetting" '
                                updatehdmiCecControl = command + cecControl
                                cmd.sshSettingsCommand(updatehdmiCecControl)
                                
                            elif x == '3':
                                enter = input('Enter "True" to enable, or "False" to disable HDMI-CEC Volume Control: ')
                                cecVolume = str(enter)
                                command = 'settings_cli Set "tungsten.ux.hdmiCecVolumeControlSetting" '
                                hdmiCecVolume = command + cecVolume
                                cmd.sshSettingsCommand(hdmiCecVolume)
                                
                            elif x == 'q':
                                cmd.close()
                                sys.exit(0)
                     
                            elif x == 'b':
                                break
                              
                            else:
                                print('WARNING: {} is an unknown option. Try again'.format(x))
                            continue
                            
                    except KeyboardInterrupt:
                        print('CTRL+C Pressed. Shutting Down')
                        cmd.close() 
                        
                elif x == '50': # System details
                    cmd.sshRespCommand('date')
                    cmd.model_type()
                    cmd.getCDSN()
                    print('IP Address: ' + ip)
                    cmd.stbMacAddr()
                    cmd.getSerialNumber()
                    cmd.getMode()
                    continue
                    
                elif x == '51': # software Details
                    cmd.sshRespCommand('date')                
                    cmd.SoftwareDetails()
                    print('Software Version:' + sshCommands.softwareVer + '    Build Version:' + sshCommands.buildVer)
                    print('EPG Software Version')
                    cmd.readSettings('settings_cli get tungsten.reporting_service.applicationVersion')
                    continue

                elif x == '52':
                    settingsRead()

                elif x == '53':
                    print (stbDetails)
            
                elif x == '54':
                    print (stbPrimary)

                elif x == '55':
                    print(stbDetails)
                    print(stbPrimary)

                elif x == '60':
                    getUserSettings()
                    continue

                elif x == '61':
                    readSettingsFile()
                    continue

                elif x == '62':
                    with open("stbSettings.json", "r", encoding='UTF-8') as read_file:
                        jsonRead = json.load(read_file)
                        stbPrimary.update({"CDSN": jsonRead["CDSN"]}) # Update stbPrimary dictionary with the CDSN from the file  
                        print('CDSN from file: ' + stbPrimary['CDSN'])
                        print('CDSN of the STB: ' + stbDetails['CDSN'])
                        
                        if stbPrimary['CDSN'] == stbDetails['CDSN']: # Compares CDSN values of from the file and of the STB
                            updateUserSettings()
                            
                        else: # if CDSN's don't match request confirmation to continue
                            confirm = input('These settings were saved from another STB do you want to continue? To continue enter Y : ')
                            if confirm == 'Y':
                                updateUserSettings()
                                
                            else:
                                print('canceled')
                                continue
                                
                        stbPrimary.update({"CDSN": sshCommands.CDSN})  # reverts CDSN of stbPrimary dictionary to the STB's CDSN
  
                elif x == '200':
                    try:
                        while True:
                            options = """   Title Blank TBC \n                            
                 0 - read 
                 1 - Enable
                 q - quit
                 b - back
                 """
                            print(options)
                            x = input('>: ')
                            
                            if x== '0':
                                cmd.sshCommand('settings_cli get tungsten.watermark.profile')
                                
                            elif x == '1':
                                cmd.sshCmd('settings_cli get tungsten.watermark.profile')
                                print('enable')
                                
                            elif x == 'q':
                                cmd.close()
                                sys.exit(0)
                     
                            elif x == 'b':
                                break
                              
                            else:
                                print('WARNING: {} is an unknown option. Try again'.format(x))
                            continue
                            
                    except KeyboardInterrupt:
                        print('CTRL+C Pressed. Shutting Down')
                        cmd.close() 
                
                elif x == '201': 
                    continue
     
                elif x == 'q':
                    cmd.close()
                    sys.exit(0)
                    
                elif x == 'r':
                    stbReboot()

                else:
                    print('WARNING: {} is an unknown option. Try again'.format(x))
                continue

        except KeyboardInterrupt:
            print('CTRL+C Pressed. Shutting Down')
            cmd.close()

if __name__ == '__main__':
    main()
    