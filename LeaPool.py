
import Leap, sys
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture
from PoolGame import *
from time import *
import math
import easygui 

# MENU #
def gamemenu():
    resolution = [640,480]
    mode = 0
    msg = "Welcome player! Choose an option:"
    buttons = ["Finger", "Tool"]
    picture = None # gif file
    while True: #endless loop
        title = "Menu"
        selection = easygui.buttonbox(msg, title, buttons, picture)

        if selection == "Finger":
            mode=1
            print "mode interno %d" % (mode)
            easygui.msgbox("Make a L with your thumb and index finger to hold the pool stick. Circle your finger CW or CCW to rotate the pool stick.  Swipe to hit the ball. Show 5 fingers to start")  
            break
        elif selection == "Tool":
            mode=2
            print "mode interno %d" % (mode)
            easygui.msgbox("Hold a pen or pencil to rotate the pool stick. Move the tool fast to hit or open your hand. Show 5 fingers to start")
            break
        
    return mode # returns how many times the screensaver was watched (if anybody ask)

class SampleListener(Leap.Listener):
    def on_init(self, controller):
        print "Initialized"

    def on_connect(self, controller):
        print "Connected"

        # Enable gestures Circle and Swipe
        controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE);
        controller.enable_gesture(Leap.Gesture.TYPE_SWIPE);

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print "Disconnected"

    def on_exit(self, controller):
        print "Exited"

    def getMovement(self, controller):
        # Get the most recent frame and report some basic information
        frame = controller.frame()
        interactionBox = frame.interaction_box

        
        if not frame.hands.is_empty:
            # Get the first hand
            hand = frame.hands[0]
            pointable = frame.pointables[0]
            fingers = hand.fingers
            points = hand.pointables
            
            
            
            tools = frame.tools
            direction = pointable.direction  # it will track the direction which the pointable (in this case, tool) is pointing in mode 2 in order to place the stick in the appropriate position
            stabilizedPosition = pointable.stabilized_tip_position # it will track the pointable position in mode 2 in order to place the stick in the appropriate position
            velocity = pointable.tip_velocity #it will track the velocity of the pointable in mode 2 in order to set the                    condition to make a hit to occur
            
            if len(frame.hands)>=1:
                hand2 = frame.hands[1]
                fingers2 = hand2.fingers
                numFingers = len(fingers) + len(fingers2)
            else:
                numFingers = len(fingers)
        # To quit the game, the player must show more than 8 fingers
            if numFingers>8:
                action = "quit"
                speed = 0
                return action, speed, []
        # To initialize the game, the player must show more than 8 fingers    
            if numFingers>=4:
                action = "start"
                speed = 0
                return action, speed, []
        
        
        
        
               
                #------------------------------------------------------------------#
                # ------------------  MODE 1  - Using the finger ------------------#
                #------------------------------------------------------------------#
                
# The player should use 2 fingers to hold the stick, if s/he is not holding the stick, s/he can't rotate the stick, neither hit. To adjust the angle of the stick, the player should rotate the finger in clockwise direction to rotate to left and counterclockwise to rotate to the right. To hit, the player should move the finger fast (swipe gesture). The velocity of the hit is proportional to the velocity of the swipe gesture #



            if len(points) == 2:
                vector1 = points.leftmost.direction #tracks direction of the finger that it's in the left most position (extreme x)
                vector2 = points.frontmost.direction  #tracks direction of the finger that it's in the front most position (extreme z)
           
                angleInRadians = vector1.angle_to(vector2)
                if abs(angleInRadians) >= (3/2):
                    action = "stick"
                    speed = 0
                    return action, speed, []
             
             # Gestures
            for gesture in frame.gestures():
                if gesture.type == Leap.Gesture.TYPE_CIRCLE:
                    circle = CircleGesture(gesture)
                     # Determine clock direction using the angle between the pointable and the circle normal
                    if circle.pointable.direction.angle_to(circle.normal) <= Leap.PI/4:
                        action = "right"
                        speed = 0
                        return action, speed,[]
                    else:
                        action = "left"
                        speed = 0
                        return action, speed,[]

                if gesture.type == Leap.Gesture.TYPE_SWIPE:
                    swipe = SwipeGesture(gesture)
                    action = "hit"
                    speed = swipe.speed
                    return action, speed, []
             
             
             
               
               #------------------------------------------------------------------#
               # ----------  MODE 2  - Using  a tool (pen or pencil) -------------#
               #------------------------------------------------------------------#
# The player should use a tool to simulate the position and rotation of the stick. To hit, the player should move the tool fast. The velocity of the hit is proportional to the velocity of the tool #               
                    
            if len(tools) == 1: #condition to track the tool, it should be only one
            #if len(frame.fingers) == 1:
               tool = tools[0]
               #tool = frame.fingers[0]
               normalizedPosition = interactionBox.normalize_point(tool.tip_position) #tracks the tip position of the tool and normalizes it
               
               # The direction of the tool is used to calculate the angle between the stick should form with the vertical axis in the game
               dir_x= tool.direction.x 
               dir_z= -tool.direction.z
               angle = math.atan2(-dir_x,dir_z)
               print (" TRACKING TOOL %f") %(dir_x)
               action = "stick2"
               speed = 0
               aux = [normalizedPosition.x, normalizedPosition.z,angle]
               return action, speed, aux
               
           
            for pointable in frame.pointables:
                speed = math.sqrt(velocity.x**2+velocity.z**2+ velocity.y**2)
                if(speed > 600): #condition to the hit occur -> the magnitude of velocity should be greater than 600
                
                #if(math.fabs(velocity.x)> 600 or math.fabs(velocity.y)> 600 or math.fabs(velocity.z)> 600): #condition to the hit occur -> the magnitude of velocity should be greater than 600
                    action = "hit2"
                    print "speed = %f" %(speed)
                    #speed = math.sqrt(velocity.x**2+velocity.z**2+ velocity.y**2)
                    return action, speed, []
           
            
        return "", 0, 0

    def state_string(self, state):
        if state == Leap.Gesture.STATE_START:
            return "STATE_START"

        if state == Leap.Gesture.STATE_UPDATE:
            return "STATE_UPDATE"

        if state == Leap.Gesture.STATE_STOP:
            return "STATE_STOP"

        if state == Leap.Gesture.STATE_INVALID:
            return "STATE_INVALID"

def main(mode=1):
    mode = gamemenu()
    #mode=1
    sleep(2) #Delay to make the window pop up properly
    print "mode %d" % (mode)
    Flag=1
    
    pygame.init()
    # Create a sample listener and controller
    listener = SampleListener()
    controller = Leap.Controller()
    

    # Have the sample listener receive events from the controller
    controller.add_listener(listener)
    
    action = ""
    holdStick = 0
    
    while action!= "start":
        action, speed, aux = listener.getMovement(controller)
        if action != "":
            print action, speed
        sleep(1)

    #Initializing game

    game = PoolGame({'x' : 520, 'y' : 800})
    hit = False
    action = ""
    
    while action != "quit":
        action, speed, aux = listener.getMovement(controller)
        #if action != "":
        #    print action, speed
        
        #########################################################
        #-------------------------------------------------------#
        # ----------------- MODE 1 -----------------------------#
        #-------------------------------------------------------#
        #########################################################
        
        
        if action == "stick" and not hit and mode == 1:
            holdStick = 1
            screen = pygame.display.get_surface()
            myfont = pygame.font.SysFont("Comic Sans MS", 40)
            label = myfont.render("Hold Stick", 3, (255, 255, 255))
            screen.blit(label, (260, 650))
            pygame.display.flip()
            sleep(1)
            print "Hold Stick!"
            
        if action == "start" and mode == 1:
            holdStick = 0
            screen = pygame.display.get_surface()
            myfont = pygame.font.SysFont("Comic Sans MS", 40)
            label = myfont.render("Drop Stick", 3, (255, 255, 255))
            screen.blit(label, (260, 650))
            pygame.display.flip()
            sleep(1)
            print "Drop Stick!"   

        if action == "left" and holdStick:
            game.poolStick.rotate(1)
        
        if action == "right" and holdStick:
            game.poolStick.rotate(-1)
        
        if not hit and action == "hit" and holdStick and mode == 1:
            game.poolStick.hitBall(game.whiteBall, speed/15)
            hit = True
            holdStick = 0

        if int(game.whiteBall.vx) == 0 and int(game.whiteBall.vy) == 0:
            hit = False
            
            #########################################################
            #-------------------------------------------------------#
            # ----------------- MODE 2 -----------------------------#
            #-------------------------------------------------------#
            #########################################################
            
        if action == "stick2" and not hit and mode == 2:
            holdStick = 1
            x, z ,angle = aux 
            game.poolStick.x = x*520
            game.poolStick.y = z*800
            game.poolStick.angle = angle*(180/3.14159265359)
            
            
        
        if action == "hit2" and mode == 2:
            game.poolStick.hitBall(game.whiteBall, speed/15)
            hit = True
            holdStick = 0
            
            
            
        while mode == 2 and Flag==1:
            screen = pygame.display.get_surface()
            myfont = pygame.font.SysFont("Comic Sans MS", 40)
            label = myfont.render("Mode Tool", 3, (255, 255, 255))
            screen.blit(label, (260, 650))
            pygame.display.flip()
            sleep(1.5)
            Flag = 0
        
        while mode == 1 and Flag==1:
            screen = pygame.display.get_surface()
            myfont = pygame.font.SysFont("Comic Sans MS", 40)
            label = myfont.render("Mode Finger", 3, (255, 255, 255))
            screen.blit(label, (260, 650))
            pygame.display.flip()
            sleep(1.5)
            Flag = 0
            
        #get input
        for event in pygame.event.get():
            if event.type == QUIT or \
                (event.type == KEYDOWN and event.key == K_ESCAPE):
                    return
            if event.type == KEYDOWN:
                if event.key == K_RIGHT:
                    mode=2
                    Flag=1
                    print "Entrou mode 2"

                if event.key == K_LEFT:
                    mode=1
                    Flag=1
                    print "Entrou mode 1"

        keystate = pygame.key.get_pressed()
        
        game.update()
        sleep(0.05)

     
    # Remove the sample listener when done
    controller.remove_listener(listener)
    
if __name__ == "__main__":
    main()
    
    
    
