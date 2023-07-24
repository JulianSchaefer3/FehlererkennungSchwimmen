
class CrawlArms(object):
    
    #Fehlercounter init
    __countLeftArmLong = 0
    __countLeftArmFlexed = 0
    __countLeftArmStarted = 0
    
    __countRightArmStarted = 0
    __countRightArmLong = 0
    __countRightArmFlexed = 0
    
    #Links
    __leftArmStarted = False #Arm korrekt vorne
    __leftArmFlexed = False #Arm korrekt gebeugt
    __leftArmLong = False #Arm korrekt lang hinten
    __leftArmFlexedView = False #Arm war gebeugt
    
    #Rechts
    __rightArmStarted = False #Arm korrekt vorne
    __rightArmFlexed = False #Arm korrekt gebeugt
    __rightArmLong = False #Arm korrekt lang hinten
    __rightArmFlexedView = False #Arm war gebeugt
    __THRESHOLD = 5
    
    #Werte ueberpruefung Arm zu Beginn lang: Gut 
    __WERT_ARMS_STARTED = 150
    __SHOULDER_LEFTRIGHT_STARTED_MIN = 75
    __SHOULDER_LEFTRIGHT_STARTED_MAX = 130

    #Werte ueberpruefung Arm zu Beginn lang: erkannt
    __WERT_ARMS_STARTED_OKAY = 90  
    __SHOULDER_LEFTRIGHT_STARTED_OKAY = 155
    __SHOULDER_UPDOWN_STARTED_OKAY = 150 #hinzugefuegt 13.06.2023 im Rahmen Hand Vorne Erkennen
    
    #Werte ueberpruefung Arm gebeugt: Gut
    __WERT_ARM_FLEXED_MIN = 80
    __WERT_ARM_FLEXED_MAX = 120
    __SHOULDER_ARM_FLEXED_MIN = 80
    __SHOULDER_ARM_FLEXED_MAX = 120
    
    #Werte ueberpruefung Arm gebeugt: erkannt
    __WERT_ARM_FLEXED_OKAY = 140
    
    #Werte ueberpruefung Arm zu Ende lang: Gut
    __WERT_ARM_LONG = 150
    __SHOULDER_UPDOWN_LONG = 35

    #Koordinaten Toleranz
    __TRESHOULD_KOORDINATEN_Y_ACHSE = 0.01
    
    
    def __init__(self):
        None
    
    #Reset Attributs    
    def __setAttributeLeft(self, started, flexed, long):
        self.__leftArmStarted = started
        self.__leftArmFlexed = flexed
        self.__leftArmLong = long
        
    def __setAttributeRight(self, started, flexed, long):
        self.__rightArmStarted = started
        self.__rightArmFlexed = flexed
        self.__rightArmLong = long    
    
    #Incr. Counter
    def __setCounterLeft(self, started, flexed, long):
        if started == False:
            self.__countLeftArmStarted += 1
        if flexed == False:
            self.__countLeftArmFlexed += 1
        if long == False:
            self.__countLeftArmLong += 1    
            
    def __setCounterRight(self, started, flexed, long):
        if started == False:
            self.__countRightArmStarted += 1
        if flexed == False:
            self.__countRightArmFlexed += 1
        if long == False:
            self.__countRightArmLong += 1
    
    def getCounterLeft(self):
        return self.__countLeftArmStarted, self.__countLeftArmFlexed, self.__countLeftArmLong
    
    def getCounterRight(self):
        return self.__countRightArmStarted, self.__countRightArmFlexed, self.__countRightArmLong
    
    #Bestimmung ob beim linken Arm in Eintauch-, Zug-, Druckphase Fehler vorliegen.
    #Benoetigt Winkel linker Ellbogen, linke Schulter UPDOWN, linke Schulter LEFTRIGHT, Koordinaten Handgelenk links, Koordinaten Schulter linke
    def left_crawl_arm_leg_error_pullPhase(self, left_arm, left_shoulderUpDown, left_shoulderLeftRight, left_wrist_coordinates, left_shoulder_coordinates):
        
        #erkennt ob Arm vorne war, aber nicht in Ordnung
        if (left_arm >= self.__WERT_ARMS_STARTED_OKAY and left_shoulderLeftRight <= self.__SHOULDER_LEFTRIGHT_STARTED_OKAY and left_shoulderUpDown >= self.__SHOULDER_UPDOWN_STARTED_OKAY): #13.06.2023 22:50 Dritter Param: Ueberpruefung ob Schulter vorne, damit nicht Hand hinten erkannt wird
            leftArmFront = True  #Arm war vorne - nur temp, da bei jedem Mal neu entschieden werden muss
        else:
            leftArmFront = False
        
        if (left_wrist_coordinates[1] + self.__TRESHOULD_KOORDINATEN_Y_ACHSE  <= left_shoulder_coordinates[1]): # 13.06.2023 Vergleich Koordinaten, da Spieglung erkannt
                returnResult = (None, None, None)
        else:
            #ueberprueft ob LETZTE Bewegung richtig abgelaufen ist, daher immer Kontrolle ob Arm vorne. Wenn nicht Arm vorne Long von letzter Bewegung als erkannt
            #Einfachster Fall: Arm am Ende lang: Rest wird ueberprueft und kann einfach ausgegeben werden. Deckt 4 Faelle ab - siehe Fehlermatrix (1,3,4,7)
            if (leftArmFront == True):
                if (self.__leftArmLong == True):
                    resultLeftArmStarted = self.__leftArmStarted
                    resultLeftArmFlexed= self.__leftArmFlexed
                    resultLeftArmLong = self.__leftArmLong
                    self.__setCounterLeft(self.__leftArmStarted, self.__leftArmFlexed, True)
                    self.__setAttributeLeft(False, False, False) #geaendert [0] zu False statt resultLeftArmStarted 13.06.23 
                    returnResult = (resultLeftArmStarted, resultLeftArmFlexed, True)
                
                #Arm am Ende nicht lang, vorne/seitlich erkannt (Fall 2)
                elif (self.__leftArmFlexed == True and self.__leftArmLong):
                    self.__setCounterLeft(True, True, False)
                    self.__setAttributeLeft(False, False, False)
                    returnResult = (True, True, False)
                
                #Arm am Ende nicht lang und seitlich nicht gebeugt, vorne erkannt (Fall 5)
                elif (self.__leftArmLong == True and self.__leftArmFlexedView == True):
                    self.__setCounterLeft(True, False, False)
                    self.__leftArmFlexedView = False
                    self.__setAttributeLeft(False, False, False)
                    returnResult = (True, False, False)
                
                #Arm am Anfang und Ende nicht lang, seitlich erkannt (Fall 6)
                elif (self.__leftArmFlexed == True):
                    self.__leftArmFlexedView = False
                    self.__setCounterLeft(False, True, False)
                    self.__setAttributeLeft(False, False, False)
                    returnResult = (False, True, False) 
                
                #Alles nicht erkannt (Fall 8)
                elif (self.__leftArmFlexedView == True):
                    self.__leftArmFlexedView = False
                    self.__setCounterLeft(False, False, False)
                    self.__setAttributeLeft(False, False, False)
                    returnResult = (False, False, False) 
                    
                #Analyse nicht erfolgreich
                else:
                    returnResult = (None, None, None)
            else:
                returnResult = (None, None, None)
        
        
        #Arm lang vorne
        if (left_arm >= self.__WERT_ARMS_STARTED and left_shoulderLeftRight <= self.__SHOULDER_LEFTRIGHT_STARTED_MAX and left_shoulderLeftRight >= self.__SHOULDER_LEFTRIGHT_STARTED_MIN):
            self.__leftArmStarted = True
        
        #Arm gewinkelt
        if (left_arm <= self.__WERT_ARM_FLEXED_MAX and left_arm >= self.__WERT_ARM_FLEXED_MIN):
            self.__leftArmFlexed = True
         
        #erkennt ob Arm in Zugphase war
        if(left_arm <= self.__WERT_ARM_FLEXED_OKAY): 
            self.__leftArmFlexedView = True
        
        #Arm lang zurueck (Ende Druckphase)                    
        if (left_shoulderUpDown <= self.__SHOULDER_UPDOWN_LONG and left_arm >= self.__WERT_ARM_LONG):
            self.__leftArmLong = True
        
        return returnResult

        
    #Bestimmung ob beim rechten Arm in Eintauch-, Zug-, Druckphase Fehler vorliegen.
    #Benoetigt Winkel rechter Ellbogen, rechte Schulter UPDOWN, rechte Schulter LEFTRIGHT, Koordinaten Handgelenk rechts, Koordinaten Schulter rechts
    def right_crawl_arm_leg_error_pullPhase(self, right_arm, right_shoulderUpDown, right_shoulderLeftRight, wrist_right_coordinates, right_shoulder_coordinates):
        
        #erkennt ob Arm vorne war, aber nicht in Ordnung
        if (right_arm >= self.__WERT_ARMS_STARTED_OKAY and right_shoulderLeftRight <= self.__SHOULDER_LEFTRIGHT_STARTED_OKAY and right_shoulderUpDown >= self.__SHOULDER_UPDOWN_STARTED_OKAY):
            rightArmFront = True
        else:
            rightArmFront = False 
        
        if (wrist_right_coordinates[1] + self.__TRESHOULD_KOORDINATEN_Y_ACHSE  <= right_shoulder_coordinates[1]): # 13.06.2023 0:20 Vergleich Koordinaten, da Spieglung erkannt
                returnResult =  (None, None, None)
                 
        #ueberprueft ob LETZTE Bewegung richtig abgelaufen ist, daher immer Kontrolle ob Arm vorne. Wenn nicht Arm vorne Long von letzter Bewegung als erkannt
        #Einfachster Fall: Arm am Ende lang: Rest wird ueberprueft und kann einfach ausgegeben werden. Deckt 4 Faelle ab - siehe Fehlermatrix (1,3,4,7)
        else:
            if (rightArmFront == True):
                    
                if (self.__rightArmLong == True):
                    resultRightArmStarted = self.__rightArmStarted
                    resultRightArmFlexed= self.__rightArmFlexed
                    resultRightArmLong = self.__rightArmLong
                    self.__setCounterRight(resultRightArmStarted, resultRightArmFlexed, resultRightArmLong)
                    self.__setAttributeRight(False, False, False) # 13.06. 22:15 auf False
                    returnResult =  (resultRightArmStarted, resultRightArmFlexed, resultRightArmLong)
                
                #Arm am Ende nicht lang, vorne/seitlich erkannt (Fall 2)
                elif (self.__rightArmFlexed == True and self.__rightArmLong):
                    self.__setCounterRight(True, True, False)
                    self.__setAttributeRight(False, False, False)
                    returnResult =  (True, True, False)
                
                #Arm am Ende nicht lang und seitlich nicht gebeugt, vorne erkannt (Fall 5)
                elif (self.__rightArmLong == True and self.__rightArmFlexedView == True):
                    self.__rightArmFlexedView = False
                    self.__setCounterRight(True, False, False)
                    self.__setAttributeRight(False, False, False)
                    returnResult =  (True, False, False)
                
                #Arm am Anfang und Ende nicht lang, seitlich erkannt (Fall 6)
                elif (self.__rightArmFlexed == True):
                    self.__rightArmFlexedView = False
                    self.__setCounterRight(False, True, False)
                    self.__setAttributeRight(False, False, False)
                    returnResult =  (False, True, False) 
                
                #Alles nicht erkannt (Fall 8)
                elif (self.__rightArmFlexedView == True):
                    self.__rightArmFlexedView = False
                    self.__setCounterRight(False, False, False)
                    self.__setAttributeRight(False, False, False)
                    returnResult =  (False, False, False) 
                    
                #Analyse nicht erfolgreich
                else:
                    returnResult =  (None, None, None)
            else:
                returnResult =  (None, None, None)  
        
        
        #Arm lang vorne
        if (right_arm >= self.__WERT_ARMS_STARTED and right_shoulderLeftRight <= self.__SHOULDER_LEFTRIGHT_STARTED_MAX and right_shoulderLeftRight >= self.__SHOULDER_LEFTRIGHT_STARTED_MIN):
            self.__rightArmStarted = True
        
        #Arm gewinkelt
        if (right_arm <= self.__WERT_ARM_FLEXED_MAX and right_arm >= self.__WERT_ARM_FLEXED_MIN):
            self.__rightArmFlexed = True
         
        #erkennt ob Arm in Zugphase war
        if(right_arm <= self.__WERT_ARM_FLEXED_OKAY): 
            self.__rightArmFlexedView = True
        
        #Arm lang zurueck (Ende Druckphase)                    
        if (right_shoulderUpDown <= self.__SHOULDER_UPDOWN_LONG and right_arm >= self.__WERT_ARM_LONG):
            self.__rightArmLong = True
        
        return returnResult
            
            
       
        
         