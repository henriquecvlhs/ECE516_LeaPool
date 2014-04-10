README

LeaPool is a pool game application developed using the pygames library to be interacted with through the leap motion device. The project was created for the ECE516 - Intelligent Image Processing course at the University of Toronto, winter 2014. 

The game runs in Python 2.7 using the pygames library, so this is must be installed in order for the game to work. The project also uses the leap motion API, which makes necessary to have leap motion API for python installed. Python time and easygui libraries are other requisites.

The project includes the following files:
    PoolGame.py : file containing the bulk of the pool game, including all graphical objects and game mechanics.
    LeaPool.py : file that both runs the pool game and contains the leap motion interface for it.
    hit.wav : sound file for hitting animation.
    yes.wav : sound file for cheers animation.
    no.wav : sound file for hoot animation.
To run the game, simply run:
    # python LeaPool.py

Notes about the interface:
How to start and finish the game:
    1) Player must display five fingers in order to the pool table to appear and the game to start.
    2) Player must display ten fingers in order to close the application.
The player has, as options, two available interfaces for playing through the leap motion:
    1) Finger mode: Use finger to manipulate the pool cue: 
        - Make an angle larger than 90 degrees between thumb and index finger in order to pick up the pool cue.
        - Show five fingers in order to drop the cue.
        - Describing circles around it in order to rotate around the pool cue around the white ball.
        - Swiping in order to hit the ball with the cue already facing the desired position.
    2) Tool mode: Use a tool to manipulate the pool cue:
        - Grab a tool (like a pen) in order to pick up the pool cue.
        - Drop the tool in order to drop the cue.
        - Rotate the tool around the leap motion device in order to rotate the pool cue around the white ball.
        - Quickly movement the tool downwards in order to hit the white ball with the cue already facing the desired position.

    * In order to change between interfaces 1 and 2, simply press the keyboard's left arrow key in order to switch to mode 1 and right arrow key in order to switch to mode 2.
