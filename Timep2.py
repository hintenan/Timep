# -*- coding: utf-8 -*-
"""
Created on Fri Jul  20 16:34:51 2017

@author: hintenan
"""

import RPi.GPIO as GPIO
import time, random, pygame, csv
import numpy as np
from rc2 import uwater, det_triple, rc_time, data_structure
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
beh = data_structure(sub_conf, block)

print(beh.posRand)
print(beh.duRand)
print(beh.choiceWaterRate)
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

# pygame mixer parameters
pygame.init()
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
# Servo initiation
pin2servo = 21 # servo pin
servo2lr = [11, 4]
GPIO.setup(pin2servo, GPIO.OUT)
servoSpin = GPIO.PWM(21, 50)        #sets pin 21 to PWM and sends 50 signals per second
servoSpin.start(7.5)          #starts by sending a pulse at 7.5% to center the servo

# Sensor pin initiation
pin2response = [11, 15]
pin2center = [13]
pin2lr = [[13, 11], [13, 15]]
str2lr = [["CENTER", "LEFT"], ["CENTER", "RIGHT"]]
pin3lr = {'CENTER': 13, 'LEFT': 11, 'RIGHT': 15}
code2lr = [[2, 0], [2, 1]]
code3lr = {'CENTER': 2, 'LEFT': 0, 'RIGHT': 1}
water2lr = [[38, 36], [38, 40]]
water3lr = {'CENTER': 38, 'LEFT': 36, 'RIGHT': 40}

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
SL_sound = [0.6, 2.4, 1.05 , 1.26 , 1.38 , 1.62 , 1.74 , 1.95]
###################################

# init
du = beh.duRand[0]
pos = beh.posRand[0]
insightTime = np.array([time.time(), time.time()])
holding_fail = False
holding = 1

anHour = 60*60
halfAnHour = 90*60
updating_trial = 0
currentCon = {'Spin_pos': 0, 'curCon': -1, 'du': 0.6}
currentCon['curCon'] = beh.curCon['First_trial']
total_trial = 400

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
        
        # First Spin
        if beh.level == beh.curLear['Guilded']:
            if updating_trial == 0:
                currentCon['Spin_pos'] = pos
                servoSpin.start(servo2lr[pos])
            
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
                    insightTime[0] = 0
                    # Sound module
                    # pygame.mixer.Sound("./wave/Square7000_015s.wav").play()
                    GPIO.output(pin2buzzer, GPIO.HIGH)
                    while (time.time() < (cpoked_time + 0.15)):
                        continue
                    GPIO.output(pin2buzzer, GPIO.LOW)
                    
                    # Holding checking
                    # Holding = beh.nose_holding(updating_trial) # keyboard input
                    holding = beh.nose_holding(cpoked_time + 0.15, du)
                    
                    if (holding | (beh.leaving[updating_trial] > 14)):
                        # Hoding: beep
                        # pygame.mixer.Sound("./wave/Square7000_015s.wav").play()
                        # time.sleep(1.5)
                        while (time.time() < (cpoked_time + du + 0.15)):
                            continue
                        GPIO.output(pin2buzzer, GPIO.HIGH)
                        time.sleep(0.10)
                        while (time.time() < (cpoked_time + du + 0.3)):
                            continue
                        GPIO.output(pin2buzzer, GPIO.LOW)
                        time.sleep(0.5)

                        # uwater
                        if beh.level < beh.curLear['Cwater_removal']:
                            uwater(water3lr['CENTER'])
                        elif (beh.level < beh.curLear['Well_Trained']):
                            if ((beh.choiceWaterRate[updating_trial] < beh.lvlp[beh.level]) | (beh.leaving[updating_trial] > 9)):
                                uwater(water3lr['CENTER'])

                        #Spin
                        if beh.level == beh.curLear['Guilded']:
                            if currentCon['Spin_pos'] != pos:
                                currentCon['Spin_pos'] = pos
                                servoSpin.ChangeDutyCycle(servo2lr[pos])

                        holding_fail = False
                        # Update progress
                        currentCon['curCon'] = beh.curCon['Center_poked']
                        # print(currentCon)
                        print('GO', str2lr[pos][1])
                        # log
                        # bah.record_log([updating_trial + 1, currentCon, trial_init_time - cpoked_time, 1])

                    # Holding Fail
                    else:
                        # Leaving: white noise
                        #ws = './wave/White_' + str(beh.punishment * 100) + 's.wav'
                        #pygame.mixer.Sound(ws).play()
                        beh.errorBuzzer(pin2buzzer)
						
                        # Update progress
                        currentCon['curCon'] = beh.curCon['Center_pending']
						
                        beh.leaving[updating_trial] += 1
                        holding_fail = True
                        
                        # lower sensitivity
                        if beh.leaving[updating_trial] < 5:
                            if du < 1.5:
                                beh.short_leaving += 0
                            else:
                                beh.long_leaving += 0

                        if beh.leaving[updating_trial] == 10:
                            print(bcolors.HEADER + '100% water.' 
                                    + bcolors.ENDC)
                        elif beh.leaving[updating_trial] == 15:
                                print(bcolors.HEADER + 'LEVEL DOWN!' 
                                    + bcolors.ENDC)
                        # Punishment
                        print('Punishment ' + str(beh.punishment_center) + 's')
                        time.sleep(0.5)
						
                        # log
                        # bah.record_log([updating_trial + 1, currentCon, trial_init_time - cpoked_time, leaving])
                            
            # good mice
            # priority: 
            elif poked == beh.curCon['Correct_Respose']:
                if (currentCon['curCon'] == beh.curCon['Center_poked']):
                    # time
                    ppoked_time = time.time()

                    # uwater
                    time.sleep(0.5)
                    uwater(water2lr[pos][poked])

                    # progress
                    currentCon['curCon'] = beh.curCon['Trial_responded']
                    print('Correct Response')
                    # print(currentCon)
                    beh.strike += 1
                    # log
                    # bah.record_log([updating_trial + 1, currentCon, trial_init_time - cpoked_time, 1])
                    # Trial Responded
                    break

                # first trial handle
                # retain current trial with water
                elif (currentCon['curCon'] == beh.curCon['First_trial']):
                    # Updating progress
                    currentCon['curCon'] = beh.curCon['Center_pending']
                    # print(currentCon)

                    # uwater
                    time.sleep(0.5)
                    uwater(water2lr[pos][poked])

                    # log
                    # bah.record_log([updating_trial + 1, currentCon, trial_init_time - cpoked_time, 0])
				
                elif (currentCon['curCon'] == beh.curCon['Misplace']):
                    # double misplace handle
                    # updating progress
                    currentCon['curCon'] = beh.curCon['Misplace']
                    
                    #Spin
                    if currentCon['Spin_pos'] != pos:
                        currentCon['Spin_pos'] = pos
                        servoSpin.start(servo2lr[pos])
                    # print(currentCon)

                    # insight count
                    beh.insight[updating_trial] -= 1
                    print('NOT insightful.')
                    # sleep
                    time.sleep(2)

                    # log
                    # bah.record_log([updating_trial + 1, 0, pin, ppoked_time - cpoked_time, 0])
                # insight calculation
                elif (currentCon['curCon'] == beh.curCon['Center_pending']):
                    uniTime = time.time()
                    insightTime = beh.insight_test(updating_trial, uniTime, insightTime)
                    #if (holding_fail & int(bumble)):
                    #    print('paired uninsight')
                    #    holding_fail = False

            # bad mice
            # Priority: Unguided
            # miplace : spin
            elif poked == beh.curCon['Misplace']:
                if (beh.level > beh.curLear['Guilded']):
                    if currentCon['curCon'] == beh.curCon['Center_poked']:
                        ppoked_time = time.time()

                        print('Wrong Response')
                        beh.strike = 0
                        beh.tenderCount[updating_trial] += 1

                        # Wrong: white noise
                        ws = './wave/White_' + str(beh.punishment_peri * 100) + 's.wav'
                        pygame.mixer.Sound(ws).play()
                        # beh.errorBuzzer(pin2buzzer)

                        # Punishment
                        print('Punishment ' + str(beh.punishment_peri) + 's')
                        time.sleep(beh.punishment_peri + 1)
                        # Trial Responded
                        if beh.tender:
                            # progress
                            currentCon['curCon'] = beh.curCon['Trial_responded']
                            # print(currentCon)
                            break
                    else:
                        uniTime = time.time()
                        insightTime = beh.insight_test(updating_trial, uniTime, insightTime)
                        #if (holding_fail & int(bumble)):
                        #    print('paired uninsight')
                        #    holding_fail = False
                
                else:
                    # Updating progress
                    currentCon['curCon'] = beh.curCon['Misplace']
                    
                    #Spin
                    if currentCon['Spin_pos'] == pos:
                        currentCon['Spin_pos'] = int(not pos)
                        servoSpin.ChangeDutyCycle(servo2lr[not pos])
                    print('Wrong Respose')
                    # print(currentCon)
                    
                    # Wrong: white noise
                    ws = './wave/White_' + str(beh.punishment_peri * 100) + 's.wav'
                    pygame.mixer.Sound(ws).play()
                    # beh.errorBuzzer(pin2buzzer)

                    # Punishment
                    print('Punishment ' + str(beh.punishment_peri) + 's')
                    time.sleep(beh.punishment_peri + 1)

                    # insight count
                    beh.insight[updating_trial] -= 1
                    print('NOT insightful.')
                    
                    # time.sleep(2)
            
        ### end of detection

        # Recording Data
        if currentCon['curCon'] == beh.curCon['Trial_responded']:
            print("End of trial NO." + str(updating_trial + 1))
            currentCon['curCon'] = beh.curCon['Center_pending']

            # recording data            
            leavingCount = beh.leaving[updating_trial]
            insight = beh.insight[updating_trial]
            data = [updating_trial + 1, poked, int(pos), trial_init_time, cpoked_base_time, cpoked_time, ppoked_time, round(du, 2), beh.leaving[updating_trial], beh.level, beh.sdr, beh.ldr, beh.insight[updating_trial], beh.tenderCount[updating_trial], beh.tender, beh.sig]
            beh.pre_data(data)
            tcr = beh.tenderChoiceRate(updating_trial)

            beh.sdr = beh.shortDuRate(updating_trial, 20)
            beh.ldr = beh.longDuRate(updating_trial, 20)
            data = [updating_trial + 1, poked, int(pos), trial_init_time, cpoked_base_time, cpoked_time, ppoked_time, round(du, 2), beh.leaving[updating_trial], beh.level, beh.sdr, beh.ldr, beh.insight[updating_trial], beh.tenderCount[updating_trial], beh.tender, beh.sig]
            
            beh.record_data(fm, data, updating_trial)
            objData = {'TrialNO': updating_trial + 1,
                'Correction': poked,
                'Position': int(pos),
                'CPT': cpoked_base_time,
                'HoldingT': cpoked_time,
                'TrialET': ppoked_time,
                'TrialBT': trial_init_time,
                'HoldingDu': round(float(du), 2),
                'LeavingCount': int(leavingCount),
                'LearningLevel': int(beh.level),
                'ShortDuRate': float(beh.sdr),
                'LongDuRate': float(beh.ldr),
                'Insight': int(insight),
                'TenderCount': int(beh.tenderCount[updating_trial]),
                'TenderLevel': int(beh.tender),
                'TenderChoiceRate': str(tcr[0]) + ',' + str(tcr[1]) + ',' + str(tcr[2]) + ',' + str(tcr[3]) + ',' + str(tcr[4]) + ',' + str(tcr[5]) + ',' + str(tcr[6]) + ',' + str(tcr[7]),
                'SigLevel': int(beh.sig)
                }
            results = db.child(subName).child(day).push(objData, user['idToken'])
            # next trial num
            updating_trial += 1
            
            # learning level updating
            beh.level_crite(updating_trial - 1)
            print('Level:', beh.level, 'Sensitivity:', beh.short_leaving, beh.long_leaving)
            print('Time elaspe:', round((time.time() - Session_init_time) / 60), 'minutes', round((time.time() - Session_init_time) % 60), 'seconds')

        
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
    pygame.quit()



