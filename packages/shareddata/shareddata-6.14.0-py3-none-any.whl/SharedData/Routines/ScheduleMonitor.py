import os
import sys
import time
from datetime import datetime
import pytz
from tzlocal import get_localzone
local_tz = pytz.timezone(str(get_localzone()))

# PROPRIETARY LIBS
from SharedData.Routines.Schedule import Schedule
from SharedData.Logger import Logger
from SharedData.SharedData import SharedData
shdata = SharedData('SharedData.Routines.ScheduleMonitor', user='master')

if len(sys.argv) >= 2:
    ARGS = str(sys.argv[1])
else:
    Logger.log.error('Schedules not provided, please specify!')
    raise Exception('Schedules not provided, please specify!')

Logger.log.info(
    'SharedData Routines Schedule Monitor starting for %s...' % (ARGS))

schedule_names = ARGS.split(',')
schedules = {}
for schedule_name in schedule_names:
    schedules[schedule_name] = Schedule(schedule_name)
    schedules[schedule_name].update()
    schedules[schedule_name].save()

lastheartbeat = time.time()
Logger.log.info('ROUTINE STARTED!')
while (True):
    if time.time()-lastheartbeat>15:
        lastheartbeat=time.time()
        Logger.log.debug('#heartbeat#schedule:%s' % (ARGS))

    now = datetime.now().astimezone(tz=local_tz)
    for s in schedules:
        sched = schedules[s]
        if now.date() > sched.schedule['runtimes'][0].date():            
            Logger.log.info('Reloading Schedule %s' % (str(datetime.now())))            
            sched.load()
            
        sched.update()        
        sched.save()

    time.sleep(5)
