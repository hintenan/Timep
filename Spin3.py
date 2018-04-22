# -*- coding: utf-8 -*-
"""
Created on Fri Jul  20 16:34:51 2017
@author: hintenan
"""

import RPi.GPIO as GPIO
import time, random, pygame, csv
import numpy as np
from rc3 import uwaterPos, det_triple, rc_time, data_structure
import os
import pyrebase

#**************************************************** 
# Set Firebase Config                                                
#**************************************************** 
email = 'lacerise07@gmail.com'
password = '1qaz2wsx'
config = {
  "apiKey": "AIzaSyBZNr2WLux1sRow4HlomgszU02C-y8Vgjw",
  "authDomain": "playratblue.firebaseapp.com",
  "databaseURL": "https://playratblue.firebaseio.com",
  "storageBucket": "playratblue.appspot.com"
}

firebase = pyrebase.initialize_app(config)

# Get a reference to the auth service
auth = firebase.auth()

# Log the user in
user = auth.sign_in_with_email_and_password(email, password)

# Get a reference to the database service
db = firebase.database()

#**************************************************** 
# End of Set Firebase Config                                                
#**************************************************** 

#open a data file
block = 16
print("If sound dose not work properly while using 3.5 mm analog output, input \"amixer cset numid=3 1\" in command line.")

subName = input("Subject name: ")
sub_conf = './Fan_data/conf/' + subName + '.conf'

# Loading data structure
beh = data_structure(sub_conf, block)
# print(beh.posRand)
# print(beh.duRand)
# print(beh.leaving)

day = input("Session NO.: ")
fm = './Fan_data/' + subName + day + '.csv'

# Time limit
brTime = input("Session Duration(default is 90 mins): ")
if brTime == "":
    breakTime = 90*60
else:
    breakTime = int(brTime)*60

# write file list
refData = {'Session': day,
            'Subject': subName
            }
results = db.child('available_ref').push(refData, user['idToken'])

# pygame mixer init
pygame.mixer.init()
# Fix the "first sound missing" problem
pygame.mixer.Sound("./wave/Square7000_015s.wav").play()

#**************************************************** 
# GPIO initiation
#**************************************************** 
GPIO.setmode(GPIO.BOARD)

# Buzzer initiation
pin2buzzer = 19
GPIO.setup(pin2buzzer, GPIO.OUT)
GPIO.output(pin2buzzer, GPIO.LOW)

# Sensor pin initiation
str2lr = [["CENTER", "LEFT"], ["CENTER", "RIGHT"]]

# Water pin initiation
pin_water_left = 36
pin_water_mid = 38
pin_water_right = 40
GPIO.setup(pin_water_left, GPIO.OUT)
GPIO.setup(pin_water_mid, GPIO.OUT)
GPIO.setup(pin_water_right, GPIO.OUT)
GPIO.output(pin_water_left, True)
GPIO.output(pin_water_mid, True)
GPIO.output(pin_water_right, True)

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
# usage
# print bcolors.WARNING + "Warning: No active frommets remain. Continue?" 
#      + bcolors.ENDC

# Experimental Parameters
# Seperation of sound
###################################
#SL_sound = [0.6, 2.4, 1.05 , 1.26 , 1.38 , 1.62 , 1.74 , 1.95]
###################################

# du pos init
du = beh.duRand[0]
pos = beh.posRand[0]
insightTime = [time.time(), time.time(), False]
holding = 1

anHour = 60*60
halfAnHour = 90*60
updating_trial = 0
currentCon = {'curCon': -1, 'du': 0.6}
currentCon['curCon'] = beh.curCon['First_trial']
total_trial = 400
tt = 0.04

try:
    Session_init_time = time.time()
    token_updating_timer = time.time()
    ppoked_time = Session_init_time
    
    # each trial
    while True:
        # time
        trial_init_time = ppoked_time

        # updating du, pos
        du, pos = beh.du_pos(updating_trial, du, pos)
        currentCon['du'] = round(du, 2)
            
        print(bcolors.HEADER + 'Trial NO. '+ str(updating_trial + 1) 
            + bcolors.ENDC)
        print('Holding Duration:', round(du, 2), 's')
        
        # detection
        while True:
            # detection
            poked = det_triple(pos)
            # poked = int(input("Response?")) # [0, 1, 2, 10]

            # center_poking
            if poked == beh.curCon['Center_poked']:
                # regular
                # {'First_trial': -1, 'Misplace': 0, 'Center_pending': 10}
                if (currentCon['curCon'] != beh.curCon['Center_poked']):
                    # time
                    if beh.leaving[updating_trial] == 0:
                        cpoked_base_time = time.time()
                        cpoked_time = cpoked_base_time
                    else:
                        cpoked_time = time.time()
                    
                    # reset insight time
                    if holding == 0:
                        print('insightful')
                    insightTime[0] = -1
                    
                    # beep -> Holding -> beep
                    # Holding = beh.nose_holding(updating_trial) # keyboard input
                    holding = beh.nose_holding(cpoked_time + 0.15, du)
                    
                    if (holding | (beh.leaving[updating_trial] > 14)):
                        # Update progress
                        currentCon['curCon'] = beh.curCon['Center_poked']
                        # Notification
                        print('GO', str2lr[pos][1])
                        
                        # bonus
                        if ((beh.level == beh.curLear['Hab']) | (updating_trial < 10)):
                            # uwater
                            time.sleep(0.5)
                            uwaterPos(pos, tt)

                    # Holding Fail
                    else:
                        # Update progress
                        currentCon['curCon'] = beh.curCon['Center_pending']
                        
                        # para
                        beh.leaving[updating_trial] += 1
                        
                        # Punishment
                        print('Punishment ' + str(beh.punishment_center) + 's')
                        time.sleep(0.5)

                else:
                    pass

            # good mice
            elif poked == beh.curCon['Correct_Respose']:
                if (currentCon['curCon'] == beh.curCon['Center_poked']):
                    # time
                    ppoked_time = time.time()

                    # uwater
                    time.sleep(0.5)
                    uwaterPos(pos, tt)

                    # stack
                    beh.strike += 1

                    # Updating progress
                    currentCon['curCon'] = beh.curCon['Trial_responded']
                    print('Correct Response')
                    
                    # Trial Responded
                    break

                # first trial handle
                elif (currentCon['curCon'] == beh.curCon['First_trial']):
                    
                    # Updating progress
                    currentCon['curCon'] = beh.curCon['Center_pending']

                    # uwater
                    time.sleep(0.5)
                    uwaterPos(pos, tt)

                # insight calculation
                elif (currentCon['curCon'] == beh.curCon['Center_pending']):
                    uniTime = time.time()
                    insightTime = beh.insight_test(updating_trial, uniTime, insightTime)
                    if ((not holding) & bool(int(insightTime[2]))):
                        print('Paired Uninsight')
                        holding = 1

            # bad mice
            elif poked == beh.curCon['Misplace']:
                if currentCon['curCon'] == beh.curCon['Center_poked']:
                    # time
                    ppoked_time = time.time()

                    # stack
                    beh.strike = 0

                    # Wrong: white noise
                    ws = './wave/White_' + str(beh.punishment_peri * 100) + 's.wav'
                    pygame.mixer.Sound(ws).play()
                    # Punishment
                    print('Punishment ' + str(beh.punishment_peri) + 's')
                    time.sleep(beh.punishment_peri + 1)

                    if (beh.level > beh.curLear['Guilded']):

                        # Updating progress
                        currentCon['curCon'] = beh.curCon['Trial_responded']
                        print('Wrong Response')
                    
                        # Trial Responded
                        break
                    else:
                        # Updating progress
                        currentCon['curCon'] = beh.curCon['Misplace']
                        print('Wrong Response')

                        # tender mode
                        beh.tenderCount[updating_trial] += 1

                elif (currentCon['curCon'] == beh.curCon['First_trial']):
                
                    # Updating progress
                    currentCon['curCon'] = beh.curCon['Center_pending']

                    # uwater
                    time.sleep(0.5)
                    uwaterPos(pos, tt)   
                
                else:
                    uniTime = time.time()
                    insightTime = beh.insight_test(updating_trial, uniTime, insightTime)
                    if ((not holding) & bool(int(insightTime[2]))):
                        print('paired uninsight')
                        holding = 1
                        
        ### end of detection

        # Recording Data
        if currentCon['curCon'] == beh.curCon['Trial_responded']:
            print("End of trial NO." + str(updating_trial + 1))
            currentCon['curCon'] = beh.curCon['Center_pending']

            # recording data            
            leavingCount = beh.leaving[updating_trial]
            insight = beh.insight[updating_trial]
            data = [updating_trial + 1, poked, int(pos), trial_init_time, cpoked_base_time, cpoked_time, ppoked_time, round(du, 2), beh.leaving[updating_trial], beh.level, beh.sdr, beh.ldr, beh.insight[updating_trial], int(beh.tenderCount[updating_trial])]
            beh.pre_data(data)
            

            beh.sdr = beh.shortDuRate(updating_trial, 20)
            beh.ldr = beh.longDuRate(updating_trial, 20)
            data = [updating_trial + 1, poked, int(pos), trial_init_time, cpoked_base_time, cpoked_time, ppoked_time, round(du, 2), beh.leaving[updating_trial], beh.level, beh.sdr, beh.ldr, beh.insight[updating_trial], int(beh.tenderCount[updating_trial])]
            
            beh.record_data(fm, data, updating_trial)
            objData = {'TrialNO': updating_trial + 1,
                'Correction': poked,
                'Position': int(pos),
                'TrialBT': trial_init_time,
                'CPT': cpoked_base_time,
                'HoldingT': cpoked_time,
                'TrialET': ppoked_time,
                'HoldingDu': round(float(du), 2),
                'LeavingCount': int(leavingCount),
                'LearningLevel': int(beh.level),
                'ShortDuRate': float(beh.sdr),
                'LongDuRate': float(beh.ldr),
                'Insight': int(insight),
                'TenderCount': int(beh.tenderCount[updating_trial])
                }
            results = db.child(subName).child(day).push(objData, user['idToken'])
            
            
            # learning level updating
            beh.level_crite(updating_trial)
            print('Level:', beh.level, 'Sensitivity:', beh.short_leaving, beh.long_leaving)
            print('Time elaspe:', round((time.time() - Session_init_time) / 60), 'minutes', round((time.time() - Session_init_time) % 60), 'seconds')

            # next trial num
            updating_trial += 1

        if updating_trial == total_trial:
            break
            
        # refresh token
        if (ppoked_time > (token_updating_timer + 50*60)):
            user = auth.sign_in_with_email_and_password(email, password)
            # before the 1 hour expiry:
            user = auth.refresh(user['refreshToken'])
            # now we have a fresh token
            user['idToken']
            token_updating_timer = time.time()

        if (ppoked_time > (Session_init_time + breakTime)):
            break

    # record conf file
    beh.write_conf_file(sub_conf)
    print('Time elaspe:', round((time.time() - Session_init_time) / 60), 'minutes', round((time.time() - Session_init_time) % 60), 'seconds')

except KeyboardInterrupt:
    beh.write_conf_file(sub_conf)
    print('Time elaspe:', round((time.time() - Session_init_time) / 60), 'minutes', round((time.time() - Session_init_time) % 60), 'seconds')
finally:
    
    GPIO.cleanup()
    pygame.mixer.quit()