# -*- coding: utf-8 -*-
"""
Created on Fri Jul  20 16:34:51 2016

@author: hintenan
"""

import RPi.GPIO as GPIO
import time, pygame, csv, random
import numpy as np
from typing import Tuple
sensors = [11, 15, 13]
pin_water = [36, 38, 40]
pin2lr = [[13, 11], [13, 15]]
upper = 20
upper_re = 150
lower = 17
sensi = 17

# interruption
def rc_time_bar (pin_to_infra):
    count = 0
    #Output on the pin for
    GPIO.setup(pin_to_infra, GPIO.OUT)
    GPIO.output(pin_to_infra, GPIO.LOW)
    #Change the pin back to input
    GPIO.setup(pin_to_infra, GPIO.IN)
    #Count until the pin goes high
    while (GPIO.input(pin_to_infra) == GPIO.HIGH):
        count += 1
        if count > upper:
            break
    #if count < lower:
    #    print(str(pin_to_infra) + " " + str(count)+" Something happened")
    return count

def rc_time_re (pin_to_infra):
    count = 0
    #Output on the pin for
    GPIO.setup(pin_to_infra, GPIO.OUT)
    GPIO.output(pin_to_infra, GPIO.LOW)
    #Change the pin back to input
    GPIO.setup(pin_to_infra, GPIO.IN)
    #Count until the pin goes high
    while (GPIO.input(pin_to_infra) == GPIO.LOW):
        count += 1
        if count == upper_re:
            break
    #if count < lower:
    #    print(str(pin_to_infra) + " " + str(count)+" Something happened")
    return count

# reflection & bar
def rc_time (pin_to_infra):
    count = 0
    #Output on the pin for
    GPIO.setup(pin_to_infra, GPIO.OUT)
    GPIO.output(pin_to_infra, GPIO.LOW)
    #Change the pin back to input
    GPIO.setup(pin_to_infra, GPIO.IN)
    #Count until the pin goes high
    while (GPIO.input(pin_to_infra) == GPIO.LOW):
        count += 1
        if count > upper:
            break
    #if count < lower:
    #    print(str(pin_to_infra) + " " + str(count)+" Something happened")
    return count

def det_both(pos):
    cp = rc_time(pin2lr[pos][0])
    rp = rc_time(pin2lr[pos][1])
    # triple check
    if cp < sensi:
        if rc_time(pin2lr[pos][0]) > sensi:
            return 2
        if rc_time(pin2lr[pos][0]) > sensi:
            return 2
        return 0

    elif rp < 5:
        if rc_time(pin2lr[pos][1]) > sensi:
            return 2
        if rc_time(pin2lr[pos][1]) > sensi:
            return 2 
        return 1
    return 2

# {'First_trial': -1, 'Correct_Respose': 1, 'Misplace': 0, 'Double_mis': -5, 'Center_pending':10, 'Center_poked': 2, 'Trial_responded': 100}
def det_triple(pos):
    cp = rc_time(pin2lr[pos][0])
    rp = rc_time(pin2lr[pos][1])
    wp = rc_time(pin2lr[not pos][1])
    #print(rp, cp, wp)
    # triple check
    if cp > sensi:
        if rc_time(pin2lr[pos][0]) < sensi:
            return 3
        if rc_time(pin2lr[pos][0]) < sensi:
            return 3
        return 2

    elif rp > sensi:
        if rc_time(pin2lr[pos][1]) < sensi:
            return 3
        if rc_time(pin2lr[pos][1]) < sensi:
            return 3 
        return 1
    

    elif wp > sensi:
        if rc_time(pin2lr[not pos][1]) < sensi:
            return 3
        if rc_time(pin2lr[not pos][1]) < sensi:
            return 3 
        return 0
    return 3


def det_one(pos, val):
    cp = rc_time(pin2lr[pos][val])
    # triple check
    if cp < sensi:
        if rc_time(pin2lr[pos][val]) > sensi:
            return 2
        if rc_time(pin2lr[pos][val]) > sensi:
            return 2
        return 0
    return 2


def uwater (pin_to_water):
    GPIO.output(pin_to_water, False)
    time.sleep(0.05)
    GPIO.output(pin_to_water, True)

def memory_check(count_down, last_memory):
    trigger_time = 0
    count = np.array([7, 7, 7])
    tri_side = 10
    for i in range(3):
        if sum(last_memory) == 5:
            last_memory = (last_memory==3)*3
        if last_memory[i] == 0:
            count[i] = rc_time(sensors[i])
            
            if count[i] < lower:
                if rc_time(sensors[i]) < lower:
                    count_down += 1
                    trigger_time = time.time()
                    tri_side = i
                    if sum(last_memory) == 2:
                        last_memory[i] = 3
                    elif sum(last_memory) < 2:
                        last_memory[i] = 1
                    elif sum(last_memory) == 3:
                        last_memory *= 0
                        last_memory[i] = 1
                    #w.writerow(last_memory)
                    print("trigger something")
                    uwater(pin_water[i])
    #print count[0], count[1], count[2]            
    #print '||  ', count[0], '  ||  ', count[1], '  ||  ', count[1], '  ||'    
    return tri_side, trigger_time, count_down, last_memory


def memory_longcheck(count_down, wrong_count, last_memory):
    trigger_time = 0
    count = np.array([7, 7, 7])
    tri_side = 10
    hold_check = 1
    max_holding = 10
    time_hoding = 2.4
    


    for i in range(3):
        if sum(last_memory) == 5:
            last_memory = (last_memory==3)*3
        if last_memory[i] == 0:
            count[i] = rc_time(sensors[i])
     
            if count [i] < lower:
                holding_time = time.time()
                hold_counter = 0 # counter
                hold_pos1 = rc_time(sensors[i])
                hold_pos2 = rc_time(sensors[i])
                while ((time.time() - holding_time) < time_hoding):
                    hold_pos1 = hold_pos2
                    hold_pos2 = rc_time(sensors[i])
                    if ((hold_pos1 > sensi) & (hold_pos2 > sensi)) :
                        hold_counter += 1
                    else:
                        hold_counter = 0


                        
                    if hold_counter > max_holding:
                        hold_check = 0
                        wrong_count += 1
                        
                
                        #pygame.mixer.Sound("./wave/White_015s.wav").play()
                        break
                        

                if hold_check == 1:   
                    count_down += 1
                    trigger_time = time.time()
                    tri_side = i
                    if sum(last_memory) == 2:
                        last_memory[i] = 3
                    elif sum(last_memory) < 2:
                        last_memory[i] = 1
                    elif sum(last_memory) == 3:
                        last_memory *= 0
                        last_memory[i] = 1
                    #w.writerow(last_memory)
                    print("trigger something")
                    uwater(pin_water[i])

                    

                    
    #print count[0], count[1], count[2]            
    #print '||  ', count[0], '  ||  ', count[1], '  ||  ', count[1], '  ||'    
    return tri_side, trigger_time, count_down, wrong_count, last_memory

class data_structure:
    
    def __init__(self, sub_conf, block):

        self.level, self.short_pos, self.sig, self.tender = self.read_conf_file(sub_conf)
        self.leaving_recount(self.level)
        #if self.sig == 3:
        #    self.sig = 2
        
        self.curCon = {'First_trial': -1, 'Misplace': 0, 'Correct_Respose': 1, 'Center_poked': 2, 'Center_pending':10, 'Trial_responded': 100}
        self.curLear = {'Guilded': 0, 'Strict_holding':5, 'Cwater_removal': 6, 'Well_Trained':10, 'Full_DM': 14,  'Full_punishment':18}
        self.data = []
        
        # posRand
        self.block = block
        self.duRand, self.duRandBool, self.duRandDuo, self.posRand, self.leaving, self.insight, self.choiceWaterRate, self.tenderCount = self.addPosRand(block, self.short_pos) 

        # learning_criteria
        self.lvl = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
        self.lvlt = [32, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16]
        self.lvlp = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.8, 0.6, 0.3, 0.125, 0, 0, 0, 0, 0, 0, 0, 0]
        self.lvlf = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0]
        
        self.culmu_trial = self.lvlt[self.level] # culmulative trials
        self.culmu_tranLen = 0 # culmulative transition length
        self.culmu_sigLen = 0 # culmulative sig length
        self.culmu_sigTrial = self.lvlt[self.tender] # culmulative sig trial
        self.culmu_tender = self.lvlt[self.tender] # culmulative tender trials
        
        self.punishment_center = 3 # 3 sec
        self.punishment_peri = 3 # 3 sec
        self.count = 0 # free var
        self.sdr = 0.0
        self.ldr = 0.0
        self.strike = 0

    def leaving_recount(self, level):
        self.long_leaving = 200100 - level * 40000
        self.short_leaving = 100100 - level * 40000
        if self.long_leaving < 10:
            self.long_leaving = 10
        if self.short_leaving < 10:
            self.short_leaving = 10

    # def hadd(self, data):
    #     self.data = np.hstack((self.data, data))

    def vadd(self, data):
        if len(self.data):
            self.data = np.vstack((self.data, data))
        else:
            self.data = data
            
    
    def addPosRand(self, block, short_pos):
        SL_sound = [0.6, 2.4, 1.05 , 1.26 , 1.38 , 1.62 , 1.74 , 1.95]
        multipler = 30

        duRand = []

        if ((block % 2) == 0):
            half = int(block/2)

            for i in range(multipler):

                new = np.random.permutation([0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7])
                dus = np.array([SL_sound[i] for i in new])
                
                if len(duRand):
                    duRand = np.hstack((duRand, dus))
                else:
                    duRand = np.copy(dus)
                
            duRandBool = np.copy((duRand > 1.5)*1)
            duRandDuo = np.copy((duRand > 1.5)*1)
            duRandDuo = (duRandDuo == 1)*2.4 + (duRandDuo == 0)*0.6

            if short_pos:
                posRand = np.copy(np.logical_not(duRandBool)*1)
            else:
                posRand = np.copy(duRandBool)
           
            leaving = np.zeros(block * multipler , dtype = np.int)
            insight = np.zeros(block * multipler , dtype = np.int)
            tenderCount = np.zeros(block * multipler , dtype = np.int)
            choiceWaterRate = np.random.rand(block * multipler)
            if self.level < (self.curLear['Well_Trained']):
                choiceWaterRate[0:5] = 0.0
            
            self.randDuoShortPool = duRandDuo[duRandDuo < 1.5]
            self.randDuoLongPool = duRandDuo[duRandDuo > 1.5]
            self.randShortPool = duRand[duRand < 1.5]
            self.randLongPool = duRand[duRand > 1.5]


            return duRand, duRandBool, duRandDuo, posRand, leaving, insight, choiceWaterRate, tenderCount
        else:
            print("Odd block checking point.")
            
    def du_pos(self, tnum: int, du: float, pos: int) -> Tuple[float, int]:
        
        # always start from longdu side
        if tnum == 0:
            du = 2.4
            pos = not self.short_pos
        
        if (self.sig < 2) & (tnum == 0):
            self.shortPool = 0
            self.longPool = 0
            self.lvlstrike = [4, 4]
                        
        if self.sig == 0:
            if ((self.strike >= self.lvlstrike[self.sig]) | (((self.culmu_sigLen + 1) % 4) == 0)):
                self.strike = 0
                self.culmu_sigLen = 0
                pos = not pos
                if du < 1.5:
                    du = self.randDuoLongPool[self.longPool]
                    self.longPool += 1
                else:
                    du = self.randDuoShortPool[self.shortPool]
                    self.shortPool += 1

            else:
                self.culmu_sigLen += 1
                if du < 1.5:
                    du = self.randDuoShortPool[self.shortPool]
                    self.shortPool += 1
                else:
                    du = self.randDuoLongPool[self.longPool]
                    self.longPool += 1

        if self.sig == 1:
            if ((self.strike >= self.lvlstrike[self.sig]) | (((self.culmu_sigLen + 1) % 4) == 0)):
                self.strike = 0
                self.culmu_sigLen = 0
                pos = not pos
                if du < 1.5:
                    du = self.randLongPool[self.longPool]
                    self.longPool += 1
                else:
                    du = self.randShortPool[self.shortPool]
                    self.shortPool += 1

            else:
                self.culmu_sigLen += 1
                if du < 1.5:
                    du = self.randShortPool[self.shortPool]
                    self.shortPool += 1
                else:
                    du = self.randLongPool[self.longPool]
                    self.longPool += 1

        elif self.sig == 2:
            du = self.duRand[tnum]
            pos = self.posRand[tnum]

        
        
        # print('self.culmu_sigLen:', self.culmu_sigLen)
        return du, pos

    def nose_holding(self, ctime, du):
    
        leaving_counter = 0
        holding = 1
        le_btime = ctime
        if du > 1.5:
            max_leaving = self.long_leaving
        else:
            max_leaving = self.short_leaving
        
        while ((time.time() - ctime) < du):
            hold_pos = rc_time(13)
            hold_pos_re = rc_time_re(7)
            if ((hold_pos < sensi) & (hold_pos_re > (upper_re - 10))):
                leaving_counter += 1
                if leaving_counter == 1:
                    le_btime = time.time()
            else :
                leaving_counter = 0
            
            if leaving_counter > max_leaving:
                le_etime = time.time()
                print("hold_du:", round(le_btime - ctime, 2), "leaving_du:", round(le_etime - le_btime, 2), "counter:", leaving_counter)
                holding = 0
                break
        if holding == 1:
            le_etime = time.time()
            print("hold_du:", round(le_btime - ctime, 2), "leaving_du:", round(le_etime - le_btime, 2), "counter:", leaving_counter)
        return holding
    # end of nose_holding
    def nose_holding_p(self, ctime, du):
        holding = 1
        holding_counter = 0
        leaving_counter = 0
        pre_time = time.time()
        while ((time.time() - ctime) < du):
            hold_pos = rc_time(13)
            if (hold_pos > sensi):
                if (time.time() < (pre_time + 0.08)):
                    pre_time = time.time()
                    holding_counter += 1
                else:
                    holding = 0
                    break
            else:
                if (time.time() > (pre_time + 0.08)):
                    holding = 0
                    break
                else:
                    leaving_counter += 1
        print(holding_counter, leaving_counter)
        return holding, holding_counter, leaving_counter

    def insight_test(self, tnum, uniTime, insightTime):
        # bumble = 0
        if insightTime[0] == 0:
            insightTime = np.array([uniTime, uniTime])
        else:
            if (uniTime > (insightTime[1] + 0.5)):
                self.insight[tnum] -= 1
                insightTime = np.array([uniTime, uniTime])
                # bumble = 1
                print('short uninsight')
            else:
                if (uniTime < (insightTime[0] + 2)):
                    insightTime[1] = uniTime
                else:
                    if self.insight[tnum] == 0:
                        return np.array([uniTime, uniTime])
                    else:
                        self.insight[tnum] -= 1
                        insightTime = np.array([uniTime, uniTime])
                        # bumble = 1
                        print('long insight')
        return insightTime

    def pass_holding(self, ctime, du):
        holding = 1
        while ((time.time() - ctime) < du):
            time.sleep(0.001)
        print("hold_du:", "pass", "le_du:", "pass", "leaving_counter:", "pass")
        return holding

    def shortDuLen(self):
        sduLen = self.data[self.data[:, 7] < 1.5, 1]
        return len(sduLen)

    def shortDuRate(self, tnum, consecu):
        # print(self.data)
        # print(self.data[:, 7])
        # print(self.data[self.data[:, 7] == 0, 8])
        if tnum :
            sduList = self.data[self.data[:, 7] < 1.5, 8:9] + 1
            sduLevel = self.data[self.data[:, 7] < 1.5, 9] == self.level
            sdr = sduList[sduLevel, 0]
            print(sdr[-10:])
            if len(sdr[-consecu:]):
                return len(sdr[-consecu:])/sum(sdr[-consecu:])
            else:
                return 0
        else:
            if (self.data[7] < 1.5): 
                sdr = self.data[8] + 1
                return 1 / sdr
            else:
                return 0

    def longDuLen(self):
        lduLen = self.data[self.data[:, 7] > 1.5, 1]
        return len(lduLen)

    def longDuRate(self, tnum, consecu):
        # print(self.data)
        # print(self.data[:, 7])
        # print(self.data[self.data[:, 7] == 0, 8])
        if tnum :
            lduList = self.data[self.data[:, 7] > 1.5, 8:9] + 1
            lduLevel = self.data[self.data[:, 7] > 1.5, 9] == self.level
            ldr = lduList[lduLevel, 0]
            print(ldr[-10:])
            if len(ldr[-consecu:]):
                return len(ldr[-consecu:])/sum(ldr[-consecu:])
            else:
                return 0
        else:
            if (self.data[7] > 1.5): 
                ldr = self.data[8] + 1
                return 1 / ldr
            else:
                return 0
    
    def choiceRate(self, tnum):
        crList = [0, 0, 0, 0, 0, 0, 0, 0]
        if tnum :
            SL_list = [0.6, 1.05 , 1.26 , 1.38 , 1.62 , 1.74 , 1.95, 2.4]
            for i in range(8):
                choice_array = self.data[self.data[:, 7] == SL_list[i], 1]
                if len(choice_array):
                    crList[i] = np.mean(choice_array[-20:])
                else:
                    crList[i] = 0
                
            return crList 

        return [0, 0, 0, 0, 0, 0, 0, 0]

    def tenderRate(self, tnum):
        crList = [0, 0, 0, 0, 0, 0, 0, 0]
        if tnum :
            SL_list = [0.6, 1.05 , 1.26 , 1.38 , 1.62 , 1.74 , 1.95, 2.4]
            for i in range(8):
                choice_array = self.data[self.data[:, 7] == SL_list[i], 13]
                if len(choice_array):
                    crList[i] = np.mean(choice_array[-20:])
                else:
                    crList[i] = 0
                
            return crList 

        return [0, 0, 0, 0, 0, 0, 0, 0]

    def tenderChoiceRate(self, tnum):
        crList = [0, 0, 0, 0, 0, 0, 0, 0]
        if tnum :
            SL_list = [0.6, 1.05 , 1.26 , 1.38 , 1.62 , 1.74 , 1.95, 2.4]
            for i in range(8):
                choice_array = self.data[self.data[:, 7] == SL_list[i], 13]
                if len(choice_array):
                    crList[i] = np.mean(choice_array[-10:] == 0)
                else:
                    crList[i] = 0
                
            return crList 

        return [0, 0, 0, 0, 0, 0, 0, 0]

    



    
    def pre_data(self, list):
        self.vadd(list)

    def record_data(self, fm, list, tnum):

        if tnum :
            self.data[-1, :] = list
        else:
            self.data = list

        with open(fm, 'a') as f:
            writer = csv.writer(f)
            if list[0]:
                writer.writerow(list)
            else:
                writer.writerow(list)

    
    def level_crite(self, tnum):
        
        cr = self.choiceRate(tnum)
        tr = self.tenderRate(tnum)
        
        if tnum:
            tranLen, tran = self.trans()
        else:
            tranLen = 0
            tran = 0
        
        if self.leaving[tnum] > 14:
            self.level -= 1
            if self.level < 0:
                self.level = 0
            self.leaving_recount(self.level)
        
        if self.leaving[tnum] > 0:
            self.leaving_recount(self.level)

        if self.level == self.curLear['Guilded']: # level 0
            
            if tnum == (self.culmu_trial - 1):
                
                self.level += 1
                self.culmu_trial += self.lvlt[self.level]
                
                self.leaving_recount(self.level)
                
                print('Remove Glid!')
        elif (self.level > self.curLear['Guilded']) & (self.level < self.curLear['Cwater_removal']): # level 1~5 -> 6

            if tnum == (self.culmu_trial - 1):

                if ((self.sdr > 0.89) & (self.ldr > 0.84)):
                
                    self.level += 1
                    self.culmu_trial += self.lvlt[self.level]

                    self.leaving_recount(self.level)
                   
                else:
                    self.culmu_trial += 1
                    print('self.culmu_trial =', self.culmu_trial)
        
        elif ((self.level >= self.curLear['Cwater_removal']) & (self.level < self.curLear['Well_Trained'])): # level 6 ~ 9-> 10
            if ((self.leaving[tnum] > 4) & (self.level <= (self.curLear['Cwater_removal'] + 2))):
                self.choiceWaterRate[tnum] = 0.0
            if tnum == (self.culmu_trial - 1):

                if ((self.sdr > 0.89) & (self.ldr > 0.79)):
                    
                    self.level += 1
                    self.culmu_trial += self.lvlt[self.level]
                    self.culmu_tranLen += tranLen
                    
                else:
                    self.culmu_trial += 1
                    print('self.culmu_trial =', self.culmu_trial)

         
        """
        elif ((self.level >= self.curLear['Well_Trained']) & (self.level < self.curLear['Full_punishment'])): # level 10 -> 14
            if tnum == (self.culmu_trial - 1):
                
                if ((self.sdr > 0.89) & (self.ldr > 0.74) & (tranLen >= (self.level - 4 + self.culmu_tranLen)) & (self.sig > 2)):
                    self.punishment += 2
                    self.level += 1
                    self.culmu_trial += self.lvlt[self.level]
                    
                else:
                    self.culmu_trial += 1
                    print('self.culmu_trial =', self.culmu_trial)

        """
        print('ShortHoldingRate:', round(self.sdr, 4))
        print('LongHoldingRate:', round(self.ldr, 4))
        print('ShortChoiceRate:', round(cr[0], 4))
        print('LongChoiceRate:', round(cr[-1], 4))
        print('Choice rate:', np.round(cr, 4))
        print('Choice rate (tender):', np.round(self.tenderChoiceRate(tnum), 4))
        print('tender rate:', np.round(tr, 4))

        print('Transition:', round(tran, 4))
        print('tranLen:', tranLen, '>', (4 * (self.sig + 1) + self.culmu_tranLen))
        
        # sig level
        if (self.sig < 3):
            if (tnum == (self.culmu_sigTrial - 1)):
                if ((cr[0] >= 0.8) & (cr[-1] >= 0.8) & (tr[0] <= 0.3) & (tr[-1] <= 0.3) & (tran >= 0.7) & (tranLen >= (4 * (self.sig + 1) + self.culmu_tranLen))):
                    print('sig up!!!!!!!!!!!!!!!!!')
                    self.sig += 1 # sig
                    self.culmu_tranLen += tranLen
                    self.culmu_sigTrial += self.lvlt[self.sig]
                else:
                    self.culmu_sigTrial += 1
        print('sig =', self.sig)
    # end of level_crite

    def trans(self):
        zero = 0
        tran = np.hstack((np.zeros(1), np.diff(self.data[:, 7] > 1.5)))
        tran = (self.data[tran != 0, 13] == 0)
        
        if len(tran):
            return len(tran), np.mean(tran[-5:])
        else:
            return zero, zero
    # end of trans()    
    
    def read_conf_file(self, sub_conf):
        try:
            with open(sub_conf) as csvFile:
                print('reading conf')
                reader = csv.DictReader(csvFile)
                for row in reader:
                    print(row['val'] + ', ' + row['description'])
                    if row['description'] == 'short position':
                        short_pos = int(row['val'])
                    elif row['description'] == 'p1 stages':
                        learning_level = int(row['val'])
                    elif row['description'] == 'sig':
                        sig = int(row['val'])
                    elif row['description'] == 'tender':
                        tender = int(row['val'])

        except IOError as e:
            print("Unable to open configure file") #Does not exist OR no reading permissions
            exit()
        return learning_level, short_pos, sig, tender
    # end of read_conf_file(sub_conf)

    def write_conf_file(self, sub_conf):
        try:
            with open(sub_conf, 'w') as csvFile:
                fieldnames = ['val', 'description']
                writer = csv.DictWriter(csvFile, fieldnames=fieldnames)

                writer.writeheader()
                writer.writerow({'val': self.short_pos, 'description': 'short position'})
                writer.writerow({'val': self.level, 'description': 'p1 stages'})
                writer.writerow({'val': self.sig, 'description': 'sig'})
                writer.writerow({'val': self.tender, 'description': 'tender'})
                # writer.writerow({'val', 'description')
        except IOError as e:
            print("Unable to write configure file") #Does not exist OR no reading permissions
            exit()
    # end of write_conf_file(sub_conf)

    def errorBuzzer(self, pin2buzzer):
        errEnd = time.time()
        while ((time.time() - errEnd) < self.punishment_center):
            GPIO.output(pin2buzzer, GPIO.HIGH)
            time.sleep(0.005)
            GPIO.output(pin2buzzer, GPIO.LOW)
            time.sleep(random.random()/20)


