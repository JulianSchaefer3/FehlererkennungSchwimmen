import math

class CrawlLeg(object):
    

    #Init Fehlerzähler
    __countLeftLegLong = 0
    __countLeftLegKinked = 0
    __countRightLegLong = 0
    __countRightLegKinked = 0
    
    #Init Betrachtung der Winkel vorher/spaeter. Array mit 180 initialisiert, da aus Gleitphase kommt und die Beine daher einen optimalen Winkel von 180 Grad haben sollten
    __rightAngleArray = [180,180,180]
    __leftAngleArray = [180,180,180]
    
    #Schwellenwerte
    __THRESHOLD = 5
    __WERTLEGLONG = 150
    __WERTLEGKINKED = 90
    
    def __init__(self):
        None

    def getCountLeftLeg(self):
        return self.__countLeftLegLong, self.__countLeftLegKinked
    
    def getCountRightLeg(self):
        return self.__countRightLegLong, self.__countRightLegKinked

    #ueberprueft nur, ob Beine lang sind:
    #Funktion benötigt Winkel der Kniegelenke
    def crawl_leg_kick_error_Long(self,left_leg, right_leg):
        
        
        #überprüft ob Bein lang ist
            
            if left_leg >= 130:
                leftLegCorrect = True
            else: 
                leftLegCorrect = False
                self.__countLeftLegLong += 1

            if right_leg >= 130:
                rightLegCorrect = True
            else:
                rightLegCorrect = False
                self.__countRightLegLong += 1
             
            return (leftLegCorrect,rightLegCorrect)
    
    #ueberprueft ob Beine lang und nicht zu weit angewinkelt sind
    #Funktion benoetigt Winkel der Kniegelenkte
    def crawl_leg_kick_error_WayBack(self,left_leg, right_leg):
        
        #Zwischenspeichern der Winkel der vergangenen Analysen
        temp = self.__leftAngleArray[0]
        temp2 = self.__leftAngleArray[1]
        
        self.__leftAngleArray = [left_leg,temp,temp2]
        
        #ueberprueft ob ein "Knick" da ist --> groß-klein-groß von den Winkeln her - wenn ja überprüfe kleinestmoeglichen und gebe Feedback
        if (math.ceil(self.__leftAngleArray[1]) + self.__THRESHOLD < self.__leftAngleArray[0] and math.ceil(self.__leftAngleArray[1]) + self.__THRESHOLD < self.__leftAngleArray[2] ):
            if (self.__leftAngleArray[1] < self.__WERTLEGKINKED):
                leftLegCorrect = False
                self.__countLeftLegKinked += 1
                    
            else:
                leftLegCorrect = True
        
         #ueberprueft ob ein Bein lang ist --> klein-groß-klein von den Winkeln her - wenn ja überprüfe groesstmoeglichen und gebe Feedback
        elif (int(self.__leftAngleArray[1]) - self.__THRESHOLD > self.__leftAngleArray[0] and int(self.__leftAngleArray[1]) - self.__THRESHOLD > self.__leftAngleArray[2] ):
            if (self.__leftAngleArray[1] < self.__WERTLEGLONG):
                leftLegCorrect = False
                self.__countLeftLegLong += 1
           
            else:
                leftLegCorrect = True
        else:
            leftLegCorrect = True
            
        temp = self.__rightAngleArray[0]
        temp2 = self.__rightAngleArray[1]
        self.__rightAngleArray = [right_leg,temp,temp2]   
         
        #ueberprueft ob ein "Knick" da ist --> groß-klein-groß von den Winkeln her - wenn ja überprüfe kleinestmoeglichen und gebe Feedback
        if (math.ceil(self.__rightAngleArray[1]) +self.__THRESHOLD < self.__rightAngleArray[0] and math.ceil(self.__rightAngleArray[1]) + self.__THRESHOLD < self.__rightAngleArray[2] ):
            if (self.__rightAngleArray[1] <self.__WERTLEGKINKED):
                rightLegCorrect = False
                self.__countRightLegKinked += 1
           
            else:
                rightLegCorrect = True
        
       #ueberprueft ob ein Bein lang ist --> klein-groß-klein von den Winkeln her - wenn ja überprüfe groesstmoeglichen und gebe Feedback
        elif (int(self.__rightAngleArray[1]) - self.__THRESHOLD > self.__rightAngleArray[0] and int(self.__rightAngleArray[1]) - self.__THRESHOLD > self.__rightAngleArray[2] ):
                
            if (self.__rightAngleArray[1] < self.__WERTLEGLONG and self.__rightAngleArray[1] > self.__WERTLEGKINKED ):
                rightLegCorrect = False
                self.__countRightLegLong += 1
                   
            else:
                rightLegCorrect = True
        else:
                rightLegCorrect = True
                
        return (leftLegCorrect, rightLegCorrect)