import random, os.path
from math import sin, cos, radians, atan2, fabs
import pygame
from pygame.locals import *

################################################################################################

main_dir = os.path.split(os.path.abspath(__file__))[0]          

# Class for dealing with playing songs
class dummysound:
    def play(self): pass

def load_sound(file):
    if not pygame.mixer: return dummysound()
    file = os.path.join(main_dir, 'data', file)
    try:
        sound = pygame.mixer.Sound(file)
        return sound
    except pygame.error:
        print ('Warning, unable to load, %s' % file)
    return dummysound()

################################################################################################

# Base class for any graphic object in game.
class GraphicObject(object):
    # Constructor method.
    # Parameters:
    #   x : initial integer x coordinate for the object's position.
    #   y : initial integer y coordinate for the object's position.
    def __init__(self, x = 0, y = 0):
        self.drawFlag = True
        self.last_x = x
        self.last_y = y
        self.x = x
        self.y = y
        self.setSpeed(0, 0)

    # Sets object speed.
    # Parameters:
    #   vx : x component of velocity vector.
    #   vy : y component of velocity vector.
    def setSpeed(self, vx, vy):
        self.vx = vx
        self.vy = vy

    # Updates object's position according to its speed.
    # Should be called inside the game's update method.
    def updatePosition(self):
        if self.vx != 0 or self.vy != 0:
            self.last_x = self.x
            self.last_y = self.y
            self.x += int(self.vx)
            self.y += int(self.vy)
            # draws only if needed
            #if self.x != self.last_x or self.y != self.last_y:
            #    self.drawFlag = True
            #else:
            #    self.drawFlag = True

    # Returns the object's (x, y) coordinates.
    def getPosition(self):
        return (self.x, self.y)

    # Return the object's last (x, y) coordinates.
    def getLastPosition(self):
        return (self.last_x, self.last_y)

    # The following are abstract methods to be defined in order to manage collisions and drawing of objects.

    def getCollision(self, x, y):
        return False

    def manageCollision(self, collidingObject):
        pass

    def draw(self, windowSurfaceObj):
        pass

################################################################################################

# Class that describes any ball in the pool game.
class PoolBall(GraphicObject):
    radius = 20                 # All instantiated balls will have 20 pixel sized radius.
    acc_factor = 0.65           # All instantiated balls will be decelerated by the same factor due to friction.
    collision_factor = 0.55     # All instantiated balls will have same elasticity factor when colliding with each other.

    # Constructor method:
    # Parameters:
    #   x : initial integer x coordinate for the object's position.
    #   y : initial integer y coordinate for the object's position.
    #   colour : ball colour in RGB format.
    def __init__(self, x = 0, y = 0, colour = (0, 0, 0)):
        self.colour = colour

        self.collided = False
        self.new_vx = 0
        self.new_vy = 0
        
        self.collidingBallsToBeManaged = []

        super(PoolBall, self).__init__(x, y)
        
        self.hit = load_sound('hit.wav')

    # Updates object's position according to its speed.
    # Should be called inside the game's update method.
    def updatePosition(self, game):
        # updates speed in case of collision
        if (self.collided):
            self.vx = self.new_vx
            self.vy = self.new_vy
            self.collided = False
        
        self.collidingBallsToBeManaged = []

        if self.vx != 0 or self.vy != 0:
            self.last_x = self.x
            self.last_y = self.y
           
            delta_vx = 0
            delta_vy = 0
            if self.vx != 0:
                delta_vx = int(abs(self.vx)/self.vx)
            if self.vy != 0:
                delta_vy = int(abs(self.vy)/self.vy)

            # tracks collisions at every pixel moved
            changedX = 0
            changedY = 0
            while self.x != self.last_x + int(self.vx) or self.y != self.last_y + int(self.vy):
                if self.x != self.last_x + int(self.vx):
                    changedX = abs(self.x - (self.x + delta_vx))
                    self.x += delta_vx
                if self.y != self.last_y + int(self.vy):
                    changedY = abs(self.y - (self.y + delta_vy))
                    self.y += delta_vy
                collidingBalls = game.getBallsCollidingWithThisOne(self)
                if len(collidingBalls) == 0 and not game.graphicObjectsList[0].getCollisionWithTable(self):
                    continue
                else:
                    if changedX:
                        self.x -= delta_vx
                    if changedY:
                        self.y -= delta_vy
                    self.collidingBallsToBeManaged = collidingBalls
                    break

        # updates speed as well
        if self.vx != 0:
            self.vx -= self.vx/abs(self.vx) * PoolBall.acc_factor
                
        if self.vy != 0:
            self.vy -= self.vy/abs(self.vy) * PoolBall.acc_factor

    # Draws coloured ball on screen. Should be called from inside the game's update method.
    # Parameters:
    #   windowSurfaceObj : pygame surface object. Should be passed by the game and represents the "canvas" where the ball is drawn.
    def draw(self, windowSurfaceObj):
        if self.drawFlag:
            pygame.draw.circle(windowSurfaceObj, self.colour, self.getPosition(), PoolBall.radius, 0)

    # Detects if a point of coordinates (x, y) is colliding with instantiated ball object.
    # Parameters:
    #   x : integer x coordinate of the point which will be tested for collision.
    #   y : integer y coordinate of the point which will be tested for collision.
    def getCollision(self, x, y):
        if (x - self.x)**2 + (y - self.y)**2 <= PoolBall.radius**2:
            return True
        else:
            return False

    # Applies the effects of collision.
    # The method currently works only if the colliding object is also a PoolBall object.
    # Implements kinematics for oblique particle collisions.
    # Parameters:
    #   collidingObject : not used.
    def manageCollision(self, collidingObject):
        if self.collided:
            return

        # this is assuming the colliding object is also a circle, so perhaps it should be changed to be more generic
        for collidingBall in self.collidingBallsToBeManaged:
            # for elastic collisions:
            # m v_a' + m v_b' = m v_a + m v_b
            # - v_a + v_b = e (v_a - v_b)
            v_a = self.vx
            v_b = collidingBall.vx
            collidingBall.new_vx = (v_a + v_b + PoolBall.collision_factor * (v_a - v_b))/2.0
            self.new_vx = (v_a + v_b + PoolBall.collision_factor * (v_b - v_a))/2.0

            v_a = self.vy
            v_b = collidingBall.vy
            collidingBall.new_vy = (v_a + v_b + PoolBall.collision_factor * (v_a - v_b))/2.0
            self.new_vy = (v_a + v_b + PoolBall.collision_factor * (v_b - v_a))/2.0

            # after that, we make multiplications by sins and cosines for oblique collisions
            real_dist = ((collidingBall.x - self.x)**2 + (collidingBall.y - self.y)**2)**0.5
            real_dist = 1 if (not real_dist) else real_dist # avoids division by 0
            sin_collision_angle = (collidingBall.y - self.y)/float(real_dist)
            cos_collision_angle = (collidingBall.x - self.x)/float(real_dist)
            self.new_vx = self.new_vx * sin_collision_angle * sin_collision_angle + self.new_vy * cos_collision_angle * sin_collision_angle
            self.new_vy = self.new_vx * sin_collision_angle * cos_collision_angle + self.new_vy * cos_collision_angle * cos_collision_angle
            collidingBall.new_vx = collidingBall.new_vx * cos_collision_angle * cos_collision_angle + collidingBall.new_vy * sin_collision_angle * cos_collision_angle
            collidingBall.new_vy = collidingBall.new_vx * cos_collision_angle * sin_collision_angle + collidingBall.new_vy * sin_collision_angle * sin_collision_angle

            self.collided = True
            collidingBall.collided = True
            
            self.hit.play()

################################################################################################

# Describes the table where the pool game is played.
class PoolTable(GraphicObject):

    # Constructor method:
    # Parameters:
    #   size_x : table integer size across x axis.
    #   size_y : table integer size across y axis.
    def __init__(self, size_x, size_y):
        super(PoolTable, self).__init__()
        self.size_x = size_x
        self.size_y = size_y
        self.pocketRadius = PoolBall.radius + 5
        self.borderSize = self.pocketRadius + 10
        self.pocketOffset = 15
        self.pocketOffsetMiddle = 10
        self.score = Score()

    # Draws the table on the screen.
    # Should be called, before any other object's draw method is called, inside the game's update method.
    # Parameters:
    #   windowSurfaceObj : pygame surface object. Should be passed by the game and represents the "canvas" where the table is drawn.
    def draw(self, windowSurfaceObj):
        colour = {
            'black':(0,0,0),
            'green':(50, 140, 50),
            'brown':(120, 50, 40),
        }

        # draw brown background to make the borders        
        pygame.draw.rect(windowSurfaceObj, colour['brown'], (0, 0, self.size_x, self.size_y), 0)
        
        # draw green rectangle inside
        pygame.draw.rect(windowSurfaceObj, colour['green'], (self.borderSize, self.borderSize, self.size_x - 2*self.borderSize, self.size_y - 2*self.borderSize), 0)

        # draw six pockets
        pygame.draw.circle(windowSurfaceObj, colour['black'], (self.pocketOffset + self.pocketRadius, self.pocketOffset + self.pocketRadius), self.pocketRadius, 0)
        pygame.draw.circle(windowSurfaceObj, colour['black'], (self.size_x - self.pocketOffset - self.pocketRadius, self.pocketOffset + self.pocketRadius), self.pocketRadius, 0)
        pygame.draw.circle(windowSurfaceObj, colour['black'], (self.pocketOffsetMiddle + self.pocketRadius, self.size_y/2), self.pocketRadius, 0)
        pygame.draw.circle(windowSurfaceObj, colour['black'], (self.size_x - self.pocketOffsetMiddle - self.pocketRadius, self.size_y/2), self.pocketRadius, 0)
        pygame.draw.circle(windowSurfaceObj, colour['black'], (self.pocketOffset + self.pocketRadius, self.size_y - self.pocketOffset - self.pocketRadius), self.pocketRadius, 0)
        pygame.draw.circle(windowSurfaceObj, colour['black'], (self.size_x - self.pocketOffset - self.pocketRadius, self.size_y - self.pocketOffset - self.pocketRadius), self.pocketRadius, 0)

        self.score.display(windowSurfaceObj, self.size_x/2, self.size_y/2)

    # Detects if a ball collided with any of the table's corners.
    # Parameters:
    #   ball : ball to be tested for collision.
    def getCollisionWithTable(self, ball):
        # check collision with top of the screen
        if ball.y - PoolBall.radius < self.borderSize:
            return True

        # check collision with bottom of the screen
        if ball.y + PoolBall.radius > self.size_y - self.borderSize:
            return True

        # check collision with left side of the screen
        if ball.x - PoolBall.radius < self.borderSize:
            return True

        # check collision with right side of the screen
        if ball.x + PoolBall.radius > self.size_x - self.borderSize:
            return True

        return False

    # Applies the effects of collision.
    # The method currently works only if the colliding object is a PoolBall object.
    # Basically identify if a ball is colliding with one of the table's corners and changes its course and speed accordingly.
    # Parameters:
    #   collidingObject : ball that will possibly collide with one of the table's corners..
    def manageCollision(self, collidingObject):
        # do not manage collision with object if it already happened this turn
        if collidingObject.collided:
            return

        # check collision with top of the screen
        if collidingObject.getCollision(collidingObject.x, self.borderSize):
            collidingObject.vy = PoolBall.collision_factor * fabs(collidingObject.vy)

        # check collision with bottom of the screen
        if collidingObject.getCollision(collidingObject.x, self.size_y - self.borderSize):
            collidingObject.vy = -1 * PoolBall.collision_factor * fabs(collidingObject.vy)

        # check collision with left side of the screen
        if collidingObject.getCollision(self.borderSize, collidingObject.y):
            collidingObject.vx = PoolBall.collision_factor * fabs(collidingObject.vx)

        # check collision with right side of the screen
        if collidingObject.getCollision(self.size_x - self.borderSize, collidingObject.y):
            collidingObject.vx = -1 * PoolBall.collision_factor * fabs(collidingObject.vx)

        # check if ball should enter in the pocket
        if (self.pocketOffset + self.pocketRadius - collidingObject.x)**2 + (self.pocketOffset + self.pocketRadius - collidingObject.y)**2 <= self.pocketRadius**2:               
            collidingObject.drawFlag = False
            if collidingObject.colour == (255, 255, 255):
                self.score.decreaseScore()
            else:
                self.score.increaseScore()
        if (self.size_x - self.pocketOffset - self.pocketRadius - collidingObject.x)**2 + (self.pocketOffset + self.pocketRadius - collidingObject.y)**2 <= self.pocketRadius**2:               
            collidingObject.drawFlag = False
            if collidingObject.colour == (255, 255, 255):
                self.score.decreaseScore()
            else:
                self.score.increaseScore()
        if (self.pocketOffsetMiddle + self.pocketRadius - collidingObject.x)**2 + (self.size_y/2 - collidingObject.y)**2 <= self.pocketRadius**2:               
            collidingObject.drawFlag = False
            if collidingObject.colour == (255, 255, 255):
                self.score.decreaseScore()
            else:
                self.score.increaseScore()
        if (self.size_x - self.pocketOffsetMiddle - self.pocketRadius - collidingObject.x)**2 + (self.size_y/2 - collidingObject.y)**2 <= self.pocketRadius**2:               
            collidingObject.drawFlag = False
            if collidingObject.colour == (255, 255, 255):
                self.score.decreaseScore()
            else:
                self.score.increaseScore()
        if (self.pocketOffset + self.pocketRadius - collidingObject.x)**2 + (self.size_y - self.pocketOffset - self.pocketRadius - collidingObject.y)**2 <= self.pocketRadius**2:               
            collidingObject.drawFlag = False
            if collidingObject.colour == (255, 255, 255):
                self.score.decreaseScore()
            else:
                self.score.increaseScore()        
        if (self.size_x - self.pocketOffset - self.pocketRadius - collidingObject.x)**2 + (self.size_y - self.pocketOffset - self.pocketRadius - collidingObject.y)**2 <= self.pocketRadius**2:               
            collidingObject.drawFlag = False
            if collidingObject.colour == (255, 255, 255):
                self.score.decreaseScore()
            else:
                self.score.increaseScore()

        if collidingObject.drawFlag == False:
            collidingObject.x = 0
            collidingObject.y = 0
            collidingObject.vx = 0
            collidingObject.vy = 0
        
        # check if white ball is inside the pocket
        if (collidingObject.colour == (255, 255, 255)) and collidingObject.drawFlag == False:
            collidingObject.drawFlag = True
            collidingObject.x = self.size_x / 2
            collidingObject.y = 4 * self.size_y / 5

    # This method should be called every time a new game needs to be configured on the table.
    # It basically instantiates several PoolBall objects of different colours and displays them across the table.
    # Also, it instantiates a white ball, to be used by the player to knock out other balls.
    # Returns the white ball and a list of all of the other balls instantiated.
    def setPoolTable(self):
        initial_pos_x = self.size_x / 2
        initial_pos_y = self.size_y / 5
        radius = PoolBall.radius
        space_between_balls = 4

        # creates each of the pool balls
        balls = []
        #balls.append(PoolBall(initial_pos_x - 4 * radius - int(2.0 * space_between_balls), initial_pos_y - 2 * radius - 1 * space_between_balls, (55, 255, 55)))
        #balls.append(PoolBall(initial_pos_x - 2 * radius - int(1.0 * space_between_balls), initial_pos_y - 2 * radius - 1 * space_between_balls, (255, 55, 55)))
        #balls.append(PoolBall(initial_pos_x - 0 * radius - int(0.0 * space_between_balls), initial_pos_y - 2 * radius - 1 * space_between_balls, (155, 255, 85)))
        #balls.append(PoolBall(initial_pos_x + 2 * radius + int(1.0 * space_between_balls), initial_pos_y - 2 * radius - 1 * space_between_balls, (255, 85, 155)))
        #balls.append(PoolBall(initial_pos_x + 4 * radius + int(2.0 * space_between_balls), initial_pos_y - 2 * radius - 1 * space_between_balls, (55, 55, 255)))

        #balls.append(PoolBall(initial_pos_x - 3 * radius - int(1.5 * space_between_balls), initial_pos_y - 0 * radius + 0 * space_between_balls, (85, 155, 255)))
        #balls.append(PoolBall(initial_pos_x - 1 * radius - int(0.5 * space_between_balls), initial_pos_y - 0 * radius + 0 * space_between_balls, (255, 155, 155)))
        #balls.append(PoolBall(initial_pos_x + 1 * radius + int(0.5 * space_between_balls), initial_pos_y - 0 * radius + 0 * space_between_balls, (155, 255, 155)))
        #balls.append(PoolBall(initial_pos_x + 3 * radius + int(1.5 * space_between_balls), initial_pos_y - 0 * radius + 0 * space_between_balls, (155, 155, 255)))

        balls.append(PoolBall(initial_pos_x - 2 * radius - int(1.0 * space_between_balls), initial_pos_y + 2 * radius + 1 * space_between_balls, (0, 255, 255)))
        balls.append(PoolBall(initial_pos_x - 0 * radius - int(0.0 * space_between_balls), initial_pos_y + 2 * radius + 1 * space_between_balls, (255, 255, 0)))
        balls.append(PoolBall(initial_pos_x + 2 * radius + int(1.0 * space_between_balls), initial_pos_y + 2 * radius + 1 * space_between_balls, (255, 0, 255)))

        balls.append(PoolBall(initial_pos_x - 1 * radius - int(0.5 * space_between_balls), initial_pos_y + 4 * radius + 2 * space_between_balls, (0, 255, 0)))
        balls.append(PoolBall(initial_pos_x + 1 * radius + int(0.5 * space_between_balls), initial_pos_y + 4 * radius + 2 * space_between_balls, (255, 0, 0)))

        balls.append(PoolBall(initial_pos_x - 0 * radius + int(0.0 * space_between_balls), initial_pos_y + 6 * radius + 3 * space_between_balls, (0, 0, 255)))

        # creates white ball
        whiteBall = PoolBall(initial_pos_x, 4 * self.size_y / 5, (255, 255, 255))

        return whiteBall, balls

################################################################################################

# Describes the stick used by the pool game player to hit the white ball.
class PoolStick(GraphicObject):

    # Constructor method:
    # Parameters:
    #   size_x : largest integer size across the x axis.
    #   size_y : largest integer size across the y axis.
    #   colour : currently unused.
    #   angle : initial angle (in degrees) with y axis.
    def __init__(self, size_x = 16, size_y = 400, colour = (142, 101, 64), angle = 270):
        self.colour = colour
        self.size_x = size_x
        self.size_y = size_y
        self.angle = angle
        self.tracking = False
        
        self.baseSurface = pygame.Surface((size_x, size_y), pygame.SRCALPHA, 32)
        self.setCoordinates()

        super(PoolStick, self).__init__()

    # Configures the stick to follow a specific ball.
    # Used in order to make it follow the white ball around.
    # Parameters:
    #   ball : ball to be followed.
    def trackBall(self, ball):
        # only draws 
        self.trackedBall = ball
        self.tracking = True

    # Defines the coordinates for every point that is used to draw the stick.
    def setCoordinates(self):
        self.mainBodyCoordinates = [(-self.size_x / 8, 0),
                                    (self.size_x / 8, 0),
                                    (self.size_x / 2, self.size_y),
                                    (-self.size_x / 2, self.size_y)]

        self.tipCoordinates = [(-self.size_x / 8, 0),
                               (self.size_x / 8, 0),
                               (self.size_x / 8, self.size_y / 16),
                               (-self.size_x / 8, self.size_y / 16)]

        self.handlerCoordinates = [(-self.size_x / 2 + 1, 3 * self.size_y / 4),
                                   (self.size_x / 2 - 1, 3 * self.size_y / 4),
                                   (self.size_x / 2, self.size_y),
                                   (-self.size_x / 2, self.size_y)]

        # translate coordinates so that the object is only in positive quadrant
        self.mainBodyCoordinates = [(coordinate[0] + self.size_x / 2, coordinate[1]) for coordinate in self.mainBodyCoordinates]
        self.tipCoordinates = [(coordinate[0] + self.size_x / 2, coordinate[1]) for coordinate in self.tipCoordinates]
        self.handlerCoordinates = [(coordinate[0] + self.size_x / 2, coordinate[1]) for coordinate in self.handlerCoordinates]

    # Updates object's position according to its speed.
    # Should be called inside the game's update method.
    def updatePosition(self):

        if self.tracking:
            self.x = self.trackedBall.x + (2 * PoolBall.radius + self.size_y / 2) * sin(radians(self.angle))
            self.y = self.trackedBall.y + (2 * PoolBall.radius + self.size_y / 2) * cos(radians(self.angle))
            if int(self.trackedBall.vx) == 0 and int(self.trackedBall.vy) == 0:
                self.drawFlag = True
            else:
                self.drawFlag = False
        else:
            self.drawFlag = True

    # Sets the stick behind the ball it is following.
    def setAfterBall(self):
        if self.tracking:
            self.angle = 0 

    # Rotate the stick around a central point by a determined angle in degrees.
    # Parameters:
    #   angle : rotation angle in degrees.
    def rotate(self, angle):
        self.angle += angle

    # Draws the stick on the screen.
    # Should be called, after all other object's draw method is called, inside the game's update method.
    # Parameters:
    #   windowSurfaceObj : pygame surface object. Should be passed by the game and represents the "canvas" where the stick is drawn.
    def draw(self, windowSurfaceObj):
        if self.drawFlag:
            self.baseSurface = self.baseSurface.convert_alpha()

            # body
            pygame.draw.polygon(self.baseSurface, (190, 150, 140), self.mainBodyCoordinates, 0)
            pygame.draw.polygon(self.baseSurface, (255, 255, 255), self.tipCoordinates, 0)
            pygame.draw.polygon(self.baseSurface, (50, 50, 50), self.handlerCoordinates, 0)
            # contour
            pygame.draw.polygon(self.baseSurface, (30, 30, 30), self.mainBodyCoordinates, 1)
    
            surface = pygame.transform.rotate(self.baseSurface, self.angle)
            surfacePos = surface.get_rect(center = (self.x, self.y))
    
            # merges the surface of drawing on the screen
            windowSurfaceObj.blit(surface, surfacePos)

    # Hits a given ball transmitting to it a certain speed.
    # Speed is transmitted according to the angle in which the stick hits the ball.
    # Parameters:
    #   ball : ball to be hit by the stick.
    #   speed : speed to be transmitted to the ball. 
    def hitBall(self, ball, speed):
        if int(ball.vx) == 0 and int(ball.vy) == 0: 
            ball.vx = - speed * cos(radians(self.angle - 90))
            ball.vy = speed * sin(radians(self.angle - 90))
            ball.new_vx = ball.vx
            ball.new_vy = ball.vy

################################################################################################

# Describes the pool game score.
# Should be an attribute of PoolTable class.
class Score(object):
    
    # Constructor method:
    def __init__(self):
        self.score = 0
        self.displayFlag = 1
        self.yes = load_sound('yes.wav')
        self.no = load_sound('no.wav')        

    # If one ball is pocketed, increases 1 point to the player's score.
    def increaseScore(self):
        ballPoints = 1
        self.yes.play()

        self.score = self.score + ballPoints

    # If the white ball is pocketed, decreases 2 points from the player's score.
    def decreaseScore(self):
        whiteBallPoints = 2
        self.no.play()

        self.score = self.score - whiteBallPoints
    
    # Displays the score.
    # Should be called inside PoolTable class' draw method.
    # Parameters:
    #   windowSurfaceObj : pygame surface object. Should be passed by the game and represents the "canvas" where the score is drawn.
    #   x : integer x coordinate representing where the score should be displayed on screen.
    #   y : integer y coordinate representing where the score should be displayed on screen.
    def display(self, windowSurfaceObj, x, y):
        fontObj = pygame.font.Font('freesansbold.ttf', 32)
        textSurfaceObj = fontObj.render('Score: ' + str(self.score), True, (255,255,255))
        textRectObj = textSurfaceObj.get_rect()
        textRectObj.center = (x, y)

        if self.displayFlag == 1:
            windowSurfaceObj.blit(textSurfaceObj, textRectObj)            

################################################################################################

# Describe the game's internal mechanisms, basically interfaces with pygame library.
class MyGame(object):
    
    # Constructor method:
    # Parameters:
    #   screenRes : dictionary in the format { "x" : integer, "y" : integer } describing the screen resolution.
    def __init__(self, screenRes = {"x" : 640, "y": 1000}):
        pygame.init()
        self.fpsClock = pygame.time.Clock()
        self.screenRes = screenRes
        self.windowSurfaceObj = pygame.display.set_mode((self.screenRes["x"], self.screenRes["y"])) # screen res
        pygame.display.set_caption('Pool Game') # screen title

        self.graphicObjectsList = []

    # Adds a graphic object to the game's control flow.
    # Parameters:
    #   graphicObject : graphic object to be added to the game. Must be an instance of a class that inherits the GraphicObject class.
    def addGraphicObject(self, graphicObject):
        self.graphicObjectsList.append(graphicObject)

    # Finds, among all ball objects currently under control, all those which are colliding with a specific ball.
    # Should be called inside PoolBall updatePosition method, in order to make a list of objects that needs managing related to collisions.
    # Parameters:
    #   ball : ball which will be used as reference during the search.
    def getBallsCollidingWithThisOne(self, ball):
        collisionList = self.graphicObjectsList[1:-1]
        collisionList.remove(ball)
        collidingBalls = []
        for collidingBall in collisionList:
            if ((collidingBall.x - ball.x)**2 + (collidingBall.y - ball.y)**2)**0.5 <= 2 * PoolBall.radius:
                collidingBalls.append(collidingBall)

        return collidingBalls
   
    # Updates the position of all graphic objects, detects and manages collisions and draws each object on the screen.
    def update(self):
        # detects collisions
        collisionList = self.graphicObjectsList[1:-1]

        #for possibleCollidingObject in collisionList:
        #    self.graphicObjectsList[0].manageCollision(possibleCollidingObject)

        for possibleCollidingObject in collisionList:
            possibleCollidingObject.manageCollision(None)

        collisionList = self.graphicObjectsList[1:-1]

        for possibleCollidingObject in collisionList:
            self.graphicObjectsList[0].manageCollision(possibleCollidingObject)

        # erases everything by filling the background with black
        self.windowSurfaceObj.fill((0, 0, 0))

        # updates position of each objects
        for graphicObject in self.graphicObjectsList:
            if isinstance(graphicObject, PoolBall):
                graphicObject.updatePosition(self)
            else:     
                graphicObject.updatePosition()
            
            graphicObject.draw(self.windowSurfaceObj)

        pygame.display.update()
        self.fpsClock.tick(30)

    # Processes inputs from the keyboard.
    # It is here only for debugging purposes, including tests without any other interface except the keyboard.
    # Parameters:
    #   poolStick : PoolStick object that is used in the pool game.
    #   whiteBall : PoolBall object that is being used as the white ball for the pool game.
    def processInput(self, poolStick, whiteBall):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()

            if event.type == KEYDOWN:
                if event.key == K_q:
                    pygame.quit()
                if event.key == K_RIGHT:
                    poolStick.rotate(15)
                if event.key == K_LEFT:
                    poolStick.rotate(-15)
                if event.key == K_SPACE:
                    poolStick.hitBall(whiteBall, 50)
                if event.key == K_m:
                    poolStick.hitBall(whiteBall, 100)
                if event.key == K_l:
                    poolStick.hitBall(whiteBall, 200)
                if event.key == K_s:
                    self.graphicObjectsList[0].score.displayFlag = not self.graphicObjectsList[0].score.displayFlag

###################################################################################################

# High level description of the pool game.
# Instantiates all objects necessary for the pool game and provides simple interface methods in order to abstract the game's behaviour.
class PoolGame(object):

    # Constructor method:
    # Parameters:
    #   screenRes : dictionary in the format { "x" : integer, "y" : integer } describing the screen resolution.
    def __init__(self, screenRes = {"x" : 640, "y": 1000}):

        game = MyGame(screenRes)

        table = PoolTable(game.screenRes["x"], game.screenRes["y"])
        whiteBall, balls = table.setPoolTable()
        poolStick = PoolStick()
    
        poolStick.trackBall(whiteBall)
        poolStick.setAfterBall()

        game.addGraphicObject(table)
        game.addGraphicObject(whiteBall)

        for ball in balls:
            game.addGraphicObject(ball)
        
        game.addGraphicObject(poolStick)

        self.game = game
        self.table = table
        self.whiteBall = whiteBall
        self.poolStick = poolStick

    # Updates the state of all objects in the pool game.
    # Should be called inside a program's main loop, in order to frequently update the game's state.
    def update(self):
        self.game.processInput(self.poolStick, self.whiteBall)
        self.game.update()


###################################################################################################
###################################################################################################

# Example code. Creates a functional pool game with keyboard-only interface.

def main():
    pg = PoolGame()

    while True:
        pg.update()

if __name__ == "__main__":
    main()
