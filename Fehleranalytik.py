import mediapipe as mp
import cv2
import numpy as np
from enum import Enum
import time
import uuid
import os
import sys

from matplotlib import pyplot as plt

from CrawlLeg import CrawlLeg
from CrawlArms import CrawlArms

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

filename = None #Hier Dateipfad des Videos einfuegen

cap = cv2.VideoCapture(filename + ".MP4") #Video

frame_width = int(cap.get(3))
frame_height = int(cap.get(4))

#Deklarierung
phase = None

leg_Error = None
arm_Error = None

gleitPhase_erkannt = False

#Fehler die Analysiert werden:
error_Analysis_Text = ["Links Beine", "Rechts Beine", "Links Arme PullPhase", "Rechts Arme PullPhase"]
error_Analysis_Bool = [True, True, True, True]

#THRESHOLD Fehler - auf 25 Meter Schwimmbahn
THRESHOLD_LEGLONG = 6
THRESHOLD_LEGKINKED = 5
THRESHOLD_ARMSTARTED = 3
THRESHOLD_ARMFLEXED = 4
THRESHOLD_ARMLONG = 2


class ErrorTypes(Enum):
    RIGHT_WRIST = 1
    LEFT_WRIST = 2
    RIGHT_ELBOW = 3
    LEFT_ELBOW = 4
    RIGHT_SHOULDER = 5
    LEFT_SHOULDER = 6
    
    RIGHT_HIP = 7
    LEFT_HIP = 8
    RIGHT_KNEE = 9
    LEFT_KNEE = 10
    RIGHT_ANKLE = 11
    LEFT_ANKLE = 12
    
    LEG_LEFT = ("Beinfehler Links",40,60)
    LEG_RIGHT = ("Beinfehler Rechts", 40,120)
    
    ARM_LEFT_STARTED = ("Armfehler Links Start", 40, 180)
    ARM_LEFT_FLEXED = ("Armfehler Links Gebeugt", 40, 240)
    ARM_LEFT_LONG = ("Armfehler Links Ende Lang", 40, 300)
    
    ARM_RIGHT_STARTED = ("Armfehler Rechts Start", 40, 360)
    ARM_RIGHT_FLEXED = ("Armfehler Rechts Gebeugt", 40, 420)
    ARM_RIGHT_LONG = ("Armfehler Rechts Ende Lang", 40, 480)
    
#überprüft ob Schwimmer in Gleitphase ist oder diese beendet hat
def getSwimPhase(currentPhase, leftArm, rightArm, leftLeg, rightLeg, gleitphase):
    if (rightArm > 160 and leftArm > 160 and leftLeg > 160 and rightLeg > 160 and gleitphase == False):
        return "Gleitphase"
    elif currentPhase == "Gleitphase":
        if (rightArm < 120 or leftArm < 120):
            return "Ende Gleitphase"
        else:
            return currentPhase 
    else:
        return currentPhase
    
#Ausgabe Fehlertext
def visualizeErrorText(image,fehler, anzahl):
    #print(fehler)
    cv2.putText(image, fehler[0] + "  " + str(anzahl), 
                    (fehler[1],fehler[2]), 
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,0), 2, cv2.LINE_AA)
        
    print(fehler[0] + " " + str(anzahl))    
        
    
    #cv2.putText(image, "Beinfehler Links", (40,60),cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2, cv2.LINE_AA)

#Ausgabe Ergebnis
def visualizeResult(image, results):
    y_coordinate = 40
    for result in results:
        cv2.putText(image, result, 
                    (40, y_coordinate), 
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,0), 2, cv2.LINE_AA)
        y_coordinate += 60


#Bestimmt die Ergebnisse mit den Toleranzen
def calculate_result(legError, crawlArm):
    leftLegError = legError.getCountLeftLeg()
    rightLegError = legError.getCountRightLeg()
    
    leftArmError = crawlArm.getCounterLeft()
    rightArmError = crawlArm.getCounterRight()
    
    results =[]
    
    #Beine
    if (error_Analysis_Bool[0] == True):
        if (leftLegError[0] >= THRESHOLD_LEGLONG):
            results.append("Fehler im Linken Bein - nicht lang genug")
        else:
            results.append("Linkes Bein lang genug")
        if (leftLegError[1] >= THRESHOLD_LEGKINKED):
            results.append("Fehler im Linken Bein - zu sehr geknickt")
        else:
            results.append("Linkes Bein gut gebeugt")
    if (error_Analysis_Bool[1] == True):
            
        if rightLegError[0] >= THRESHOLD_LEGLONG:
            results.append("Fehler im Rechten Bein -  nicht lang genug")
        else:
            results.append("Rechtes Bein lang genug")
        if (rightLegError[1] >= THRESHOLD_LEGKINKED):
            results.append("Fehler im Rechts Bein - zu sehr geknickt")
        else:
            results.append("Rechtes Bein gut gebeugt")
    
    #Linker Arm
    if (error_Analysis_Bool[2] == True):
    #Started
        if(leftArmError[0] >= THRESHOLD_ARMSTARTED):
            results.append("Fehler linker Arm - Nicht lang genug")
        else:
            results.append("Linker Arm lang genug")
        #Flexed
        if(leftArmError[1] >= THRESHOLD_ARMFLEXED): #Analysis ist hier Fehleranfälliger
            results.append("Fehler linker Arm - Nicht gebeugt genug")
        else:
            results.append("Linker Arm gebeugt genug")
        #Long
        if(leftArmError[2] >= THRESHOLD_ARMLONG):
            results.append("Fehler linker Arm - Nicht durchgedrueckt")
        else:
            results.append("Linker Arm Druckphase durchgedrueckt") 
    
    #Rechter Arm
    if (error_Analysis_Bool[3] == True):
        #Started
        if(rightArmError[0] >= THRESHOLD_ARMSTARTED):
            results.append("Fehler rechter Arm - Nicht lang genug")
        else:
            results.append("Rechter Arm lang genug")
        #Flexed
        if(rightArmError[1] >= THRESHOLD_ARMFLEXED):#Analysis ist hier Fehleranfälliger
            results.append("Fehler rechter Arm - Nicht gebeugt genug")
        else:
            results.append("Rechter Arm gebeugt genug")
        #Long
        if(rightArmError[2] >= THRESHOLD_ARMLONG):
            results.append("Fehler rechter Arm - Nicht durchgedrueckt")
        else:
            results.append("Rechter Arm Druckphase durchgedrueckt") 
             
    return results

#Winkelbestimmung: Drei 2D Vektoren als Input
def calculate_angle(a,b,c):
    a = np.array(a) # First
    b = np.array(b) # Mid
    c = np.array(c) # End
    
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    
    if angle >180.0:
        angle = 360-angle
        
    return angle

#Setup Image für Fehlerbilder

error_image = np.zeros((720,1280,3), dtype=np.uint8)
error_image.fill(255)

result_image =  np.zeros((720,2000,3), dtype=np.uint8)
result_image.fill(255)


#Fehler die Analysiert werden sollen

for i in range(0, len(error_Analysis_Bool)):
    print(error_Analysis_Text[i])
    input_User = input("y/n")
    if (input_User == "n"):
        error_Analysis_Bool[i] = False
        
print("Folgende Fehler werden ueberprueft:")
for i in range(0,len(error_Analysis_Bool)):
    if error_Analysis_Bool[i] == True:
        print(error_Analysis_Text[i])

## Setup mediapipe instance
with mp_pose.Pose(model_complexity=2,min_detection_confidence=0.5, min_tracking_confidence=0.5, static_image_mode = False) as pose:
    while cap.isOpened():
        ret, frame = cap.read()
        if ret == True:
            b = cv2.resize(frame,(1280,720),fx=0,fy=0, interpolation = cv2.INTER_CUBIC)
        
        # Recolor image to RGB
        image = cv2.cvtColor(b, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
      
        # Make detection
        results = pose.process(image)
    
        # Recolor back to BGR
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        error_image = cv2.cvtColor(error_image, cv2.COLOR_RGB2BGR)
        
    
        # Extract landmarks
        try:
            landmarks = results.pose_landmarks.landmark
            
            # Get coordinates
            #Arm Left
            shoulder_left = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            elbow_left = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
            wrist_left = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
            
            #Arm Right
            shoulder_right = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
            elbow_right = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
            wrist_right = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
            
            #Leg Left
            hip_left = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
            knee_left = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
            ankle_left = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
            
            #Leg Right
            hip_right = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
            knee_right = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
            ankle_right = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]
            
            
            # Calculate angle
            angle_left_elbow = calculate_angle(shoulder_left, elbow_left, wrist_left) #bestimmt den Winkel zwischen dem linken Handgelenk und der linken Schulter - ob das linke Ellbogengelenk gebeugt ist oder nicht
            angle_right_elbow = calculate_angle(shoulder_right,elbow_right,wrist_right) #bestimmt den Winkel zwischen dem rechten Handgelenk und der rechten Schulter - ob das rechte Ellbogengelenk gebeugt ist oder nicht
            
            angle_left_leg = calculate_angle(hip_left, knee_left, ankle_left) #bestimmt den Winkel zwischen dem linken Fußgelenk und der linken Hüfte - ob das linke Kniegelenk gebeugt ist oder nicht
            angle_right_leg = calculate_angle(hip_right, knee_right, ankle_right) #bestimmt den Winkel zwischen dem rechte Fußgelenk und der rechte Hüfte - ob das rechte Kniegelenk gebeugt ist oder nicht
            
            angle_left_shoulderUPDOWN = calculate_angle(hip_left,shoulder_left,elbow_left) #bestimmt den Winkel zwischen der linken Hüfte und dem linken Ellbogen - ob die linke Schulter und damit der linke Arm vor dem Koerper oder am Koerper anliegt
            angle_right_shoulderUPDOWN = calculate_angle(hip_right,shoulder_right,elbow_right) #bestimmt den Winkel zwischen der rechten Hüfte und dem rechten Ellbogen - ob die rechte Schulter und damit der rechte Arm vor dem Koerper oder am Koerper anliegt
            
            angle_left_shoulderLEFTRIGHT = calculate_angle(shoulder_right,shoulder_left,elbow_left) #bestimmt den Winkel zwischen der rechten Schulter und dem linken Ellbogen - ob die linke Schulter und damit der linke Arm weg vom Koeper (in Verlaenerung der Schulterache) oder zur rechten Schulter zeigt
            angle_right_shoulderLEFTRIGHT = calculate_angle(shoulder_left,shoulder_right,elbow_right) ##bestimmt den Winkel zwischen der linken Schulter und dem rechten Ellbogen - ob die rechte Schulter und damit der rechte Arm weg vom Koeper (in Verlaenerung der Schulterache) oder zur linken Schulter zeigt

            
            phase = getSwimPhase(phase,angle_left_shoulderUPDOWN, angle_right_shoulderUPDOWN, angle_left_leg,angle_right_leg, gleitPhase_erkannt)
            if (cv2.waitKey(10) & 0xFF == ord('g')):
                phase = "Gleitphase"
            if(phase == "Gleitphase"):
                gleitPhase_erkannt = True
                leg_Error = CrawlLeg()
                arm_Error = CrawlArms()
            
            if (phase == "Ende Gleitphase"):   
                #crawl_Leg = leg_Error.crawl_leg_kick_error_Long(angle_left_leg,angle_right_leg)
                
                crawl_Leg = leg_Error.crawl_leg_kick_error_WayBack(angle_left_leg,angle_right_leg)
                if (crawl_Leg[0] == False and error_Analysis_Bool[0] == True):
                    #print("Links Fehler")
                    visualizeErrorText(error_image,ErrorTypes.LEG_LEFT.value, leg_Error.getCountLeftLeg())
                if (crawl_Leg[1] == False and error_Analysis_Bool[1] == True):
                    #print("Rechts Fehler")
                    visualizeErrorText(error_image,ErrorTypes.LEG_RIGHT.value, leg_Error.getCountRightLeg())
                
                
                
                if (error_Analysis_Bool[2] == True):
                    crawl_Arm_Left = arm_Error.left_crawl_arm_leg_error_pullPhase(angle_left_elbow, angle_left_shoulderUPDOWN, angle_left_shoulderLEFTRIGHT, wrist_left, shoulder_left)
                    if (crawl_Arm_Left[0] == False):
                        visualizeErrorText(error_image,ErrorTypes.ARM_LEFT_STARTED.value, arm_Error.getCounterLeft()[0])
                    if (crawl_Arm_Left[1] == False):
                        visualizeErrorText(error_image,ErrorTypes.ARM_LEFT_FLEXED.value, arm_Error.getCounterLeft()[1])
                    if (crawl_Arm_Left[2] == False):
                        visualizeErrorText(error_image,ErrorTypes.ARM_LEFT_LONG.value, arm_Error.getCounterLeft()[2])
                
                
                
                if (error_Analysis_Bool[3] == True):
                    crawl_Arm_Right = arm_Error.right_crawl_arm_leg_error_pullPhase(angle_right_elbow, angle_right_shoulderUPDOWN, angle_right_shoulderLEFTRIGHT, wrist_right, shoulder_right)   
                    if (crawl_Arm_Right[0] == False):
                        visualizeErrorText(error_image,ErrorTypes.ARM_RIGHT_STARTED.value, arm_Error.getCounterRight()[0])
                    if (crawl_Arm_Right[1] == False):
                        visualizeErrorText(error_image,ErrorTypes.ARM_RIGHT_FLEXED.value, arm_Error.getCounterRight()[1])
                    if (crawl_Arm_Right[2] == False):
                        visualizeErrorText(error_image,ErrorTypes.ARM_RIGHT_LONG.value, arm_Error.getCounterRight()[2])
                
            # Visualize angle
            """
            cv2.putText(image, str(angle_left_arm), 
                           tuple(np.multiply(elbow_left, [640, 480]).astype(int)), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
                                )
            
            cv2.putText(image, str(angle_right_arm), 
                           tuple(np.multiply(elbow_right, [640, 480]).astype(int)), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
                                )
            """
            cv2.putText(image, str(angle_left_leg), 
                           tuple(np.multiply(knee_left, [640, 480]).astype(int)), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
                                )
            
            cv2.putText(image, str(angle_right_leg), 
                           tuple(np.multiply(knee_right, [640, 480]).astype(int)), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
                                )
            
            
           
                       
        except:
            pass
        
        # Render curl counter
        # Setup status box
        cv2.rectangle(image, (0,0), (225,73), (245,117,16), -1)
        
        # Rep data
        cv2.putText(image, 'Letzte erkannte Phase', (15,12), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)
        cv2.putText(image, str(phase), 
                    (10,60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2, cv2.LINE_AA)
        """
        # Stage data
        cv2.putText(image, 'Phasenbild', (65,12), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)
        cv2.putText(image, stage, 
                    (60,60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2, cv2.LINE_AA)
        """
        
        # Render detections
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2), #Landmarks: blue
                                mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2)  #Connections: purple
                                 )
        
        
        #Versuch einzelne Punkte einzufärben
        """
        if results.pose_landmarks:
            for pose_landmark in results.pose_landmarks:
                print(pose_landmark)
                
                mp_drawing.draw_landmarks(
                    image,
                    pose_landmark,
                    mp_pose.POSE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2),
                    mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2))
        """
        
        cv2.imshow('Mediapipe Feed', image)
        cv2.imshow("Fehler",error_image)
        #out.write(image)

        if ret == False or cv2.waitKey(10) & 0xFF == ord('q'):
            break
        
        if cv2.waitKey(10) & 0xFF == ord("r"):
            gleitPhase_erkannt = False
            
            
results = []
results = results + calculate_result(leg_Error,arm_Error)
            
visualizeResult(result_image,results)
while not (cv2.waitKey(10) & 0xFF == ord('q')):
    cv2.imshow("Result",result_image)


pose.close()
cap.release()
#out.release()
    #cap.release()
    #cv2.destroyAllWindows()