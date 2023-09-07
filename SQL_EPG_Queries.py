#!/usr/bin/env python3
'''

File:           SQL_Scripts.py
Brief:          Option menu driven SQl query tool 
Author:         James McArthur
Contributors:   N/A7

Copyright
---------
Copyright 2009-2022 Commscope Inc. All rights reserved.
This program is confidential and proprietary to Commscope Inc.
(CommScope), and may not be copied, reproduced, modified, disclosed to
others, published or used, in whole or in part, without the express
prior written permission of CommScope.
'''

import paramiko
import argparse
import sys
from datetime import datetime
import sshCommands

port =22
username ='root'
password = ' '
ssh = paramiko.SSHClient()
cmd = sshCommands

def get_args():
    reporting_parser = argparse.ArgumentParser(description='To configure a STB to connect the required server for XMPP messaging',
                                               epilog='for additional help contact James McArthur')
    reporting_parser.add_argument('ip', action='store',
                                  help='IP Address of the STB to Update (Required)')
    reporting_parser.add_argument('-options', action='store_true',
                                  help='Opens a menu to individually set the main reporting settings')

    return reporting_parser.parse_args()

def main():
    print('main running')
    args = get_args()
    global ip
    ip = args.ip
    options = args.options
    print('ip =', ip)

    if (options == 1):
        print('open')
        cmd.sshConnection(ip)
        try:
            while True:
                options =  """\n      Select a SQL query to run:  \n 
                 1 - Future events
                 2 - Past Events
                 3 - Events by Start Time
                 4 - Series linked events for current/future events
                 5 - Series linked events for past events
                 6 - Rebroadcast times for past events
                 7 - Rebroadcast times for future events
                 8 - Event with no rebroadcasting scheduled search by channel
                 9 - Events with no rebroadcast scheduled  search by Start Time
                 10 - List event with no series and episode number
                 
                 15 - Where Next event parental rating > current event
                 16 - Where Next event parental rating < current event
                 17 - Future instances of rise in parental rating on change of event
                 18 - Future instances of fall in parental rating on change of event
                 19 - Current event with StartOver and following event without StartOver
                 20 - Current event without StartOver and following event with StartOver
                 21 - Future events with Startover and event following that without Startover
                 22 - Future events without Startover and event following that with Startover
                 
                 25 - Custom Field with channel filter
                    
                 q - quit \n    """
                 
                print(options)
                x = input('>: ')

                if x == '1':
                    channel = input('Enter channel number: ')
                    limit = input('Enter number of event to return: ')
                    print('Future event info for channel:' + channel)
                    cmd.sshSQLCommand("""sqlite3 -column -header -separator $'\t' /tmp/cache.db "select a.EvName as '     Programme Title    ',datetime(a.start, 'unixepoch', 'localtime') as StartTime, datetime(a.start + a.duration, 'unixepoch', 'localtime') as Endtime, a.contentProviderID, a.uniqueContentID, b.Service_key as 'Key ', c.value as 'Channel', a.startover,a.series_Id, a.episode_seasonId as Season, a.episode_episodeId as Episode from event_list a inner join service_list b on (a.ContentID_Service=b.ContentID_Service) inner join ServiceCustomFields c on (a.ContentID_Service=c.serviceId)where datetime(a.start + a.duration, 'unixepoch', 'localtime') > datetime('now', 'localtime') and c.key='ChannelTag'and b.ChanNum=%s order by StartTime limit %s" """"" % (channel,limit))
                    continue

                elif x == '2':
                    channel = input('Enter channel number: ')
                    print('Past event info for channel:' + channel)
                    cmd.sshSQLCommand("""sqlite3 -column -header -separator $'\t' /tmp/cache.db "select a.EvName as '   Programme Title  ',datetime(a.start, 'unixepoch', 'localtime') as StartTime, datetime(a.start + a.duration, 'unixepoch', 'localtime') as Endtime, a.contentProviderID, a.uniqueContentID, b.Service_key as 'Service Key', c.value as 'Channel Tag', a.startover,a.series_Id, a.episode_seasonId as Season, a.episode_episodeId as Episode from event_list a inner join service_list b on (a.ContentID_Service=b.ContentID_Service) inner join ServiceCustomFields c on (a.ContentID_Service=c.serviceId)where datetime(a.start, 'unixepoch', 'localtime') < datetime('now', 'localtime') and c.key='ChannelTag'and b.ChanNum=%s order by StartTime desc limit 100" """"" % channel)
                    continue

                elif x == '3':
                    now = datetime.now()
                    date_time_str = now.strftime("%Y-%m-%d %H:%M:%S")
                    print('Current DateTime:', date_time_str)
                    time1 = input('Enter the lower range for Starttime in "YYYY-MM-DD HH:MM:SS" format: ')
                    time2 = input('Enter the upper range for Starttime in "YYYY-MM-DD HH:MM:SS" format: ')
                    print('Events by Start Time')
                    cmd.sshSQLCommand("""sqlite3 -column -header -separator $'\t' /tmp/cache.db "select b.ChanNum,a.EvName as '      Programme Title     ',datetime(a.start, 'unixepoch', 'localtime') as StartTime, datetime(a.start + a.duration, 'unixepoch', 'localtime') as Endtime, a.contentProviderID, a.uniqueContentID, b.Service_key as 'Service Key', c.value as 'Channel Tag', a.startover,a.series_Id, a.episode_seasonId as Season, a.episode_episodeId as Episode from event_list a inner join service_list b on (a.ContentID_Service=b.ContentID_Service) inner join ServiceCustomFields c on (a.ContentID_Service=c.serviceId)where datetime(a.start + a.duration, 'unixepoch', 'localtime') > datetime('now', 'localtime') and c.key='ChannelTag'and StartTime>'%s' and StartTime<'%s'order by StartTime limit 100" """"" % (time1,time2))
                    continue

                elif x == '4':
                    channel = input('Enter channel number: ')
                    print('Events info for channel:' + channel)
                    cmd.sshSQLCommand("""sqlite3 -column -header -separator $'\t' /tmp/cache.db "select a.EvName as '       Programme Title       ',a.series_Id as 'Series Id',datetime(a.start, 'unixepoch', 'localtime') as StartTime, datetime(a.start + a.duration, 'unixepoch', 'localtime') as Endtime, a.contentProviderID, a.uniqueContentID, b.Service_key as 'Service Key', c.value as 'Channel Tag', a.startover, a.episode_seasonId as Season, a.episode_episodeId as Episode from event_list a inner join service_list b on (a.ContentID_Service=b.ContentID_Service) inner join ServiceCustomFields c on (a.ContentID_Service=c.serviceId)where datetime(a.start + a.duration, 'unixepoch', 'localtime') > datetime('now','localtime') and c.key='ChannelTag'and b.ChanNum=%s order by StartTime limit 50" """"" % channel)
                    serid = input('Enter the Series Id from above : ')
                    print('All episodes from the selected Series')
                    cmd.sshSQLCommand("""sqlite3 -column -header -separator $'\t' /tmp/cache.db "select EvName as '      Programme Title       ', datetime(Start,'unixepoch', 'localtime') as starttime, datetime(start + duration, 'unixepoch', 'localtime') as Endtime, episode_title, contentProviderID, uniqueContentID, series_Id, episode_seasonId as Season, episode_episodeId as Episode from event_list where series_Id='%s'"; """"" % serid)
                    continue

                elif x == '5':
                    channel = input('Enter channel number: ')
                    print('Events info for channel:' + channel)
                    cmd.sshSQLCommand("""sqlite3 -column -header -separator $'\t' /tmp/cache.db "select a.EvName as '     Programme Title       ', a.series_Id, datetime(a.start, 'unixepoch', 'localtime') as StartTime, datetime(a.start + a.duration, 'unixepoch', 'localtime') as Endtime, a.contentProviderID, a.uniqueContentID, b.Service_key as 'Service Key', c.value as 'Channel Tag', a.startover, a.episode_seasonId as Season, a.episode_episodeId as Episode from event_list a inner join service_list b on (a.ContentID_Service=b.ContentID_Service) inner join ServiceCustomFields c on (a.ContentID_Service=c.serviceId)where datetime(a.start, 'unixepoch', 'localtime') < datetime('now', 'localtime') and c.key='ChannelTag'and b.ChanNum=%s order by StartTime desc limit 50" """"" % channel)
                    serid = input('Enter the Series Id from above : ')
                    print('All episodes from the selected Series')
                    cmd.sshSQLCommand("""sqlite3 -column -header -separator $'\t' /tmp/cache.db "select EvName as '        Programme Title       ', datetime(Start,'unixepoch', 'localtime') as starttime, datetime(start + duration, 'unixepoch', 'localtime') as Endtime, episode_title, contentProviderID, uniqueContentID, series_Id, episode_seasonId as Season, episode_episodeId as Episode from event_list where series_Id='%s'"; """"" % serid)
                    continue

                elif x == '6':
                    channel = input('Enter channel number: ')
                    order = input('Enter enter list order asc or desc: ')
                    print('Past events info for channel:' + channel)
                    cmd.sshSQLCommand("""sqlite3 -column -header -separator $'\t' /tmp/cache.db "select a.EvName as '      Programme Title      ', a.uniqueContentID,datetime(a.start, 'unixepoch', 'localtime') as StartTime, datetime(a.start + a.duration, 'unixepoch', 'localtime') as Endtime, a.contentProviderID, b.Service_key as 'Service Key', c.value as 'Channel Tag', a.startover,a.series_Id, a.episode_seasonId as Season, a.episode_episodeId as Episode from event_list a inner join service_list b on (a.ContentID_Service=b.ContentID_Service) inner join ServiceCustomFields c on (a.ContentID_Service=c.serviceId)where datetime(a.start, 'unixepoch', 'localtime') < datetime('now', 'localtime') and c.key='ChannelTag'and b.ChanNum=%s order by StartTime %s limit 50" """"" % (channel, order))
                    ucid = input('Enter the Assets UCID from above : ')
                    print('All episodes of the selected Asset: ' + ucid)
                    cmd.sshSQLCommand("""sqlite3 -column -header -separator $'\t' /tmp/cache.db "select a.EvName as '      Programme Title      ',datetime(a.start, 'unixepoch', 'localtime') as StartTime, datetime(a.start + a.duration, 'unixepoch', 'localtime') as Endtime, a.contentProviderID,  a.uniqueContentID, b.Service_key as 'Service Key', c.value as 'Channel Tag', b.ChanNum as 'Channel Number',a.series_Id, a.episode_seasonId as Season, a.episode_episodeId as Episode from event_list a inner join service_list b on (a.ContentID_Service=b.ContentID_Service) inner join ServiceCustomFields c on (a.ContentID_Service=c.serviceId)where c.key='ChannelTag'and a.uniqueContentID='%s' order by StartTime asc limit 50" """"" % ucid)
                    continue

                elif x == '7':
                    channel = input('Enter channel number: ')
                    print('Events information for channel:' + channel)
                    cmd.sshSQLCommand("""sqlite3 -column -header -separator $'\t' /tmp/cache.db "select a.EvName as '      Programme Title      ', a.uniqueContentID,datetime(a.start, 'unixepoch', 'localtime') as StartTime, datetime(a.start + a.duration, 'unixepoch', 'localtime') as Endtime, a.contentProviderID, b.Service_key as 'Service Key', c.value as 'Channel Tag', a.startover,a.series_Id, a.episode_seasonId as Season, a.episode_episodeId as Episode from event_list a inner join service_list b on (a.ContentID_Service=b.ContentID_Service) inner join ServiceCustomFields c on (a.ContentID_Service=c.serviceId)where datetime(a.start + a.duration, 'unixepoch', 'localtime') > datetime('now','localtime') and c.key='ChannelTag'and b.ChanNum=%s order by StartTime limit 50" """"" % channel)
                    ucid = input('Enter the Assets UCID from above : ')
                    print('All episodes of the selected Asset: ' + ucid)
                    cmd.sshSQLCommand("""sqlite3 -column -header -separator $'\t' /tmp/cache.db "select a.EvName as '      Programme Title      ',datetime(a.start, 'unixepoch', 'localtime') as StartTime, datetime(a.start + a.duration, 'unixepoch', 'localtime') as Endtime, a.contentProviderID,  a.uniqueContentID, b.Service_key as 'Service Key', c.value as 'Channel Tag', b.ChanNum as 'Channel Number',a.series_Id, a.episode_seasonId as Season, a.episode_episodeId as Episode from event_list a inner join service_list b on (a.ContentID_Service=b.ContentID_Service) inner join ServiceCustomFields c on (a.ContentID_Service=c.serviceId)where c.key='ChannelTag'and a.uniqueContentID='%s' order by StartTime asc limit 50" """"" % ucid)
                    continue

                elif x == '8':
                    print('Channels with no series and episode numbers')
                    cont = "y"
                    while(cont == "y"):
                        channel = input('Enter channel number: ')
                        print('Event with no rebroadcast scheduled by channel')
                        cmd.sshSQLCommand("""sqlite3 -column -header -separator $'\t' /tmp/cache.db "select a.EvName as '     Programme Title       ',datetime(a.start, 'unixepoch', 'localtime') as StartTime, datetime(a.start + a.duration, 'unixepoch', 'localtime') as Endtime, a.contentProviderID, a.uniqueContentID,b.ChanNum as 'Channel Number',a.series_Id, a.episode_seasonId as Season, a.episode_episodeId as Episode from event_list a inner join service_list b on (a.ContentID_Service=b.ContentID_Service) group by uniqueContentID having count(uniqueContentID)<=1 and datetime(a.start + a.duration, 'unixepoch', 'localtime') > datetime('now', 'localtime') and b.ChanNum=%s order by StartTime limit 100" """ % channel)
                        cont = input('Do you want to run this query for other channel : ')
                    continue

                elif x == '9':
                    now = datetime.now()
                    date_time_str = now.strftime("%Y-%m-%d %H:%M:%S")
                    print('Current DateTime:', date_time_str)
                    time1 = input('Enter the lower range for Starttime, events that start after this time, in "YYYY-MM-DD HH:MM:SS" format: ')
                    time2 = input('Enter the upper range for Endtime, events that finish before this time,  in "YYYY-MM-DD HH:MM:SS" format: ')
                    print('Events with no rebroadcast by Start Time')
                    cmd.sshSQLCommand("""sqlite3 -column -header -separator $'\t' /tmp/cache.db "select a.EvName as '       Programme Title       ',datetime(a.start, 'unixepoch', 'localtime') as StartTime, datetime(a.start + a.duration, 'unixepoch', 'localtime') as Endtime, a.contentProviderID, a.uniqueContentID,b.ChanNum as 'Channel Number',a.series_Id, a.episode_seasonId as Season, a.episode_episodeId as Episode from event_list a inner join service_list b on (a.ContentID_Service=b.ContentID_Service) group by uniqueContentID having count(uniqueContentID)<=1 and StartTime>'%s' and Endtime<'%s'order by StartTime limit 100" """"" % (time1,time2))
                    continue

                elif x == '10':
                    print('Channels with no series and episode numbers')
                    cmd.sshSQLCommand("""sqlite3 /tmp/cache.db "select group_concat(ChanNum, ',') from (select distinct(b.ChanNum) from event_list a inner join service_list b on a.ContentID_Service=b.ContentID_Service where episode_seasonId is null and episode_episodeId is null and a.genre is not 4 and a.genre is not 1024 order by b.ChanNum)" """)
                    cont = "y"
                    while(cont == "y"):
                        channel = input('Enter channel number: ')
                        print('Assets with no series and episode number')
                        cmd.sshSQLCommand("""sqlite3 -column -header -separator $'\t' /tmp/cache.db "Select datetime(a.start, 'unixepoch', 'localtime') as StartTime, datetime(a.start + a.duration, 'unixepoch', 'localtime') as Endtime, a.EvName, a.contentProviderID , b.ChanNum, b.ServiceName from event_list a inner join service_list b on a.ContentID_Service=b.ContentID_Service where episode_episodeId is null and episode_seasonId is null and a.genre is not 4 and a.genre is not 1024 and b.ChanNum=%s order by StartTime" """ % channel)
                        cont = input('Do you want to run this query for other channel : ')
                    continue

                elif x == '15':
                    print('Where Next event parental rating > current event')
                    cmd.sshSQLCommand("""sqlite3 -column -header -separator $'\t' /tmp/cache.db "select b.ChanNum,b.ServiceName,c.EvName as 'Event',(case when c.Parental='4' then 'G' when c.Parental='5' then 'PG' when c.Parental='6' then 'M' when c.Parental='7' then 'MA15+' when c.Parental='9' then 'R18' END) as Rating,datetime(c.start,'unixepoch','localtime') as StartTime,a.EvName as '   Next Event   ',(case when a.Parental='4' then 'G' when a.Parental='5' then 'PG' when a.Parental='6' then 'M' when a.Parental='7' then 'MA15+' when a.Parental='9' then 'R18' END) as Rating,datetime(a.start,'unixepoch','localtime') as StartTime from event_list c inner join service_list b on (a.ContentID_Service=b.ContentID_Service) inner join event_list a on (a.start=(c.start+c.duration) and a.ContentID_Service=c.ContentID_Service) where datetime(c.start,'unixepoch','localtime')<datetime('now','localtime') and datetime(c.start+c.duration,'unixepoch','localtime')>=datetime('now','localtime') and a.parental>c.Parental and b.ChanNum is not 0 order by b.ChanNum asc;" """)
                    continue

                elif x == '16':
                    print('Where Next event parental rating < current event')
                    cmd.sshSQLCommand("""sqlite3 -column -header -separator $'\t' /tmp/cache.db "select b.ChanNum,b.ServiceName,c.EvName as 'Event',(case when c.Parental='4' then 'G' when c.Parental='5' then 'PG' when c.Parental='6' then 'M' when c.Parental='7' then 'MA15+' when c.Parental='9' then 'R18' END) as Rating,datetime(c.start,'unixepoch','localtime') as StartTime,a.EvName as '   Next Event   ',(case when a.Parental='4' then 'G' when a.Parental='5' then 'PG' when a.Parental='6' then 'M' when a.Parental='7' then 'MA15+' when a.Parental='9' then 'R18' END) as Rating,datetime(a.start,'unixepoch','localtime') as StartTime from event_list c inner join service_list b on (a.ContentID_Service=b.ContentID_Service) inner join event_list a on (a.start=(c.start+c.duration) and a.ContentID_Service=c.ContentID_Service) where datetime(c.start,'unixepoch','localtime')<datetime('now','localtime') and datetime(c.start+c.duration,'unixepoch','localtime')>=datetime('now','localtime') and a.parental<c.Parental and b.ChanNum is not 0 order by b.ChanNum asc" """)
                    continue

                elif x == '17':
                    print('Future instances of rise in parental rating on change of event')
                    cmd.sshSQLCommand("""sqlite3 -column -header -separator $'\t' /tmp/cache.db "select b.ChanNum,b.ServiceName,c.EvName,(case when c.Parental='4' then 'G' when c.Parental='5' then 'PG' when c.Parental='6' then 'M' when c.Parental='7' then 'MA15+' when c.Parental='9' then 'R18' END) as Rating,datetime(c.start,'unixepoch','localtime') as StartTime,a.EvName as 'Following Event',(case when a.Parental='4' then 'G' when a.Parental='5' then 'PG' when a.Parental='6' then 'M' when a.Parental='7' then 'MA15+' when a.Parental='9' then 'R18' END) as Rating,datetime(a.start,'unixepoch','localtime') as StartTime from event_list c inner join service_list b on (a.ContentID_Service=b.ContentID_Service) inner join event_list a on (a.start=(c.start+c.duration) and a.ContentID_Service=c.ContentID_Service) where datetime(c.start,'unixepoch','localtime')<datetime(date('now','+1 day'),'localtime') and datetime(c.start+c.duration,'unixepoch','localtime')>=datetime('now','localtime') and a.parental>c.Parental and b.ChanNum is not 0 order by b.ChanNum asc" """)
                    continue

                elif x == '18':
                    print('Future instances of fall in parental rating on change of event')
                    cmd.sshSQLCommand("""sqlite3 -column -header -separator $'\t' /tmp/cache.db "select b.ChanNum,b.ServiceName,c.EvName,(case when c.Parental='4' then 'G' when c.Parental='5' then 'PG' when c.Parental='6' then 'M' when c.Parental='7' then 'MA15+' when c.Parental='9' then 'R18' END) as Rating,datetime(c.start,'unixepoch','localtime') as StartTime,a.EvName as 'Following Event',(case when a.Parental='4' then 'G' when a.Parental='5' then 'PG' when a.Parental='6' then 'M' when a.Parental='7' then 'MA15+' when a.Parental='9' then 'R18' END) as Rating,datetime(a.start,'unixepoch','localtime') as StartTime from event_list c inner join service_list b on (a.ContentID_Service=b.ContentID_Service) inner join event_list a on (a.start=(c.start+c.duration) and a.ContentID_Service=c.ContentID_Service) where datetime(c.start,'unixepoch','localtime')<datetime(date('now','+1 day'),'localtime') and datetime(c.start+c.duration,'unixepoch','localtime')>=datetime('now','localtime') and c.parental>a.Parental and b.ChanNum is not 0 order by b.ChanNum asc" """)
                    continue

                elif x == '19':
                    print('Current event with StartOver and following event without StartOver')
                    cmd.sshSQLCommand("""sqlite3 -column -header -separator $'\t' /tmp/cache.db "select b.ChanNum, b.ServiceName, c.EvName as 'Current Event', c.contentProviderID, c.startover, datetime(c.start, 'unixepoch', 'localtime') as StartTime, a.EvName as 'Next Event', a.contentProviderID, a.startover, datetime(a.start, 'unixepoch', 'localtime') as StartTime from event_list c inner join service_list b on (a.ContentID_Service = b.ContentID_Service) inner join event_list a on (a.start = (c.start + c.duration) and a.ContentID_Service = c.ContentID_Service) where datetime(c.start, 'unixepoch', 'localtime') < datetime('now', 'localtime') and datetime(c.start + c.duration, 'unixepoch', 'localtime') >= datetime('now','localtime') and a.startover = 'false' and c.startover = 'true' and b.ChanNum is not 0 order by b.ChanNum asc;" """)
                    continue

                elif x == '20':
                    print('Current event without StartOver and following event with StartOver')
                    cmd.sshSQLCommand("""sqlite3 -column -header -separator $'\t' /tmp/cache.db "select b.ChanNum, b.ServiceName, c.EvName as 'Current Event', c.contentProviderID, c.startover, datetime(c.start, 'unixepoch', 'localtime') as StartTime, a.EvName as 'Next Event', a.contentProviderID, a.startover, datetime(a.start, 'unixepoch', 'localtime') as StartTime from event_list c inner join service_list b on (a.ContentID_Service = b.ContentID_Service) inner join event_list a on (a.start = (c.start + c.duration) and a.ContentID_Service = c.ContentID_Service) where datetime(c.start, 'unixepoch', 'localtime') < datetime('now', 'localtime') and datetime(c.start + c.duration, 'unixepoch', 'localtime') >= datetime('now','localtime') and c.startover = 'false' and a.startover = 'true' and b.ChanNum is not 0 order by b.ChanNum asc;" """)
                    continue

                elif x == '21':
                    print('Future events with Startover and event following that without Startover')
                    cmd.sshSQLCommand("""sqlite3 -column -header -separator $'\t' /tmp/cache.db "select b.ChanNum, b.ServiceName, c.EvName as 'Event', c.contentProviderID, c.startover, datetime(c.start, 'unixepoch', 'localtime') as StartTime, a.EvName as 'Following Event', a.contentProviderID, a.startover, datetime(a.start, 'unixepoch', 'localtime') as StartTime from event_list c inner join service_list b on (a.ContentID_Service = b.ContentID_Service) inner join event_list a on (a.start = (c.start + c.duration) and a.ContentID_Service = c.ContentID_Service) where datetime(c.start, 'unixepoch', 'localtime') < datetime(date('now', '+1 day'), 'localtime') and datetime(c.start + c.duration, 'unixepoch', 'localtime') >= datetime('now','localtime') and a.startover = 'false' and c.startover = 'true' and b.ChanNum is not 0 order by b.ChanNum asc;" """)
                    continue

                elif x == '22':
                    print('Future events without Startover and event following that with Startover')
                    cmd.sshSQLCommand("""sqlite3 -column -header -separator $'\t' /tmp/cache.db "select b.ChanNum, b.ServiceName, c.EvName as 'Event', c.contentProviderID, c.startover, datetime(c.start, 'unixepoch', 'localtime') as StartTime, a.EvName as 'Following Event', a.contentProviderID, a.startover, datetime(a.start, 'unixepoch', 'localtime') as StartTime from event_list c inner join service_list b on (a.ContentID_Service = b.ContentID_Service) inner join event_list a on (a.start = (c.start + c.duration) and a.ContentID_Service = c.ContentID_Service) where datetime(c.start, 'unixepoch', 'localtime') < datetime(date('now', '+1 day'), 'localtime') and datetime(c.start + c.duration, 'unixepoch', 'localtime') >= datetime('now','localtime') and a.startover = 'true' and c.startover = 'false' and b.ChanNum is not 0 order by b.ChanNum asc;" """)
                    continue

                elif x == '25':
                    custom = input('Enter Custom field search criteria "TV_NO_EPS" "MOVIE": ')
                    channel1 = input('Enter Enter Lower channel number: ')
                    channel2 = input('Enter Enter Lower channel number, enter previous channel number to search on single channel: ')
                    channel_range = (channel1 + ' and ' + channel2)
                    print (channel_range)
                    print (custom)
                    command = (f"""sqlite3 /tmp/cache.db "Select b.ChanNum,  a.EvName, datetime(a.start, 'unixepoch', 'localtime') as StartTime from event_list a inner join service_list b on (a.ContentID_Service = b.ContentID_Service) where datetime(a.start + a.duration, 'unixepoch', 'localtime') > datetime('now', 'localtime') and customFields like '%{custom}%' AND ChanNum between {channel_range} order by StartTime LIMIT 25;" """)
                    print (command)
                    cmd.sshSQLCommand(command)
                    continue

                elif x == 'q':
                    cmd.close()
                    sys.exit(0)

                else:
                    print('WARNING: {} is an unknown option. Try again'.format(x))
                continue

        except KeyboardInterrupt:
            print('CTRL+C Pressed. Shutting Down')
            cmd.close()

    else:
        cmd.sshConnection(ip)
        cmd.getCDSN()
        cmd.close()

if __name__ == '__main__':
    main()