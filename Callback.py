# encoding: utf-8

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import sys
import copy

from ArcBall import * 		# ArcBallT and this tutorials set of points/vectors/matrix types

from lib.geometry import Point,Line
from lib.matrix import *

import numpy as np

PI2 = 2.0*3.1415926535		# 2 * PI (not squared!) 		// PI Squared


#Definitions of the window
winX = 640
winY = 480

# Some api in the chain is translating the keystrokes to this octal string
# so instead of saying: ESCAPE = 27, we use the following.
ESCAPE = '\033'

g_Transform = Matrix4fT ()
g_LastRot = Matrix3fT ()
g_ThisRot = Matrix3fT ()

g_ArcBall = ArcBallT (winX, winY)
g_isDragging = False
g_quadratic = None

g_isFaceSelected = False

POLIEDRY = None
RAY = Line(Point(0.0,0.0,0.0,),Point(1.0,1.0,1.0))

ModelMatrix = None

profundidade = 12.0
translating_rate = 1.0

def set_poliedry(poliedry = None):
    global POLIEDRY
    POLIEDRY = poliedry
    print "SAVED"

# A general OpenGL initialization function.  Sets all of the initial parameters.
def Initialize (Width, Height):				# We call this right after our OpenGL window is created.
    global g_quadratic, ModelMatrix

    glClearColor(1.0, 1.0, 1.0, 1.0)			# This Will Clear The Background Color To Black
    glClearDepth(1.0)					# Enables Clearing Of The Depth Buffer
    glDepthFunc(GL_LEQUAL)				# The Type Of Depth Test To Do
    glEnable(GL_DEPTH_TEST)				# Enables Depth Testing
    glShadeModel (GL_FLAT);				# Select Flat Shading (Nice Definition Of Objects)
    glHint (GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST) 	# Really Nice Perspective Calculations

    #g_quadratic = gluNewQuadric();
    #gluQuadricNormals(g_quadratic, GLU_SMOOTH);
    #gluQuadricDrawStyle(g_quadratic, GLU_FILL);
    # Why? this tutorial never maps any textures?! ?
    # gluQuadricTexture(g_quadratic, GL_TRUE);		# // Create Texture Coords

    glEnable (GL_COLOR_MATERIAL)


    return True

# The function called whenever a key is pressed. Note the use of Python tuples to pass in: (key, x, y)
def keyPressed(*args):
    global g_quadratic
    global profundidade
    global translating_rate
    # If escape is pressed, kill everything.
    key = args [0]
    if key == ESCAPE:
        gluDeleteQuadric (g_quadratic)
        sys.exit ()
    # key == 'u':
    elif key == '\165':
        profundidade += translating_rate
    elif key == '\152':
    # key == 'j':
        profundidade -= translating_rate


def Upon_Drag (cursor_x, cursor_y):
    """ Mouse cursor is moving
	Glut calls this function (when mouse button is down)
	and pases the mouse cursor postion in window coords as the mouse moves.
    """
    global g_isDragging, g_LastRot, g_Transform, g_ThisRot

    if (g_isDragging):
	mouse_pt = Point2fT (cursor_x, cursor_y)
	ThisQuat = g_ArcBall.drag (mouse_pt)				        # Update End Vector And Get Rotation As Quaternion
	g_ThisRot = Matrix3fSetRotationFromQuat4f (ThisQuat)		        # Convert Quaternion Into Matrix3fT
	# Use correct Linear Algebra matrix multiplication C = A * B
	g_ThisRot = Matrix3fMulMatrix3f (g_LastRot, g_ThisRot)		        # Accumulate Last Rotation Into This One
	g_Transform = Matrix4fSetRotationFromMatrix3f (g_Transform, g_ThisRot)	# Set Our Final Transform's Rotation From This One
    return

# This function helps to transport the window coordinate to space coordinates
def get_mouse_position_transform(winX,winY,z1):
    global ModelMatrix
    ModelMatrix = glGetDoublev(GL_MODELVIEW_MATRIX)
    ProjMatrix  = glGetDoublev(GL_PROJECTION_MATRIX)
    Viewport    = glGetIntegerv(GL_VIEWPORT)

    (newX,newY,newZ) = gluUnProject(winX,480 - winY,z1,ModelMatrix,ProjMatrix,Viewport)
    return Point(newX,newY,newZ)


def Upon_Click (button, button_state, cursor_x, cursor_y):
    """ Mouse button clicked.
	Glut calls this function when a mouse button is
	clicked or released.
    """
    global g_isDragging, g_LastRot, g_Transform, g_ThisRot
    global POLIEDRY,g_isFaceSelected,RAY

    if button_state == GLUT_DOWN:
        p_s0 = get_mouse_position_transform(cursor_x,cursor_y,0.0)
        p_s1 = get_mouse_position_transform(cursor_x,cursor_y,1.0)
        RAY = Line(p_s0,p_s1)
        if (g_isFaceSelected == False)and(button == GLUT_LEFT_BUTTON):
            if(POLIEDRY.face_intersect(RAY) != -1):
                POLIEDRY.face_select(POLIEDRY.last_face_clicked)
                print "Seleted face %d" % POLIEDRY.face_selected
                g_isFaceSelected = True
        else:
            if (button == GLUT_LEFT_BUTTON)and(POLIEDRY.face_intersect(RAY) == POLIEDRY.face_selected):
                print "Face unselected"
                POLIEDRY.face_unselect()
                g_isFaceSelected = False
            elif (button == GLUT_RIGHT_BUTTON):
                if POLIEDRY.isOpened:
                    POLIEDRY.close()
                else:
                    POLIEDRY.open()

    g_isDragging = False
    #if (button == GLUT_RIGHT_BUTTON and button_state == GLUT_UP):
        # Right button click
	#g_LastRot = Matrix3fSetIdentity ();					# Reset Rotation
	#g_ThisRot = Matrix3fSetIdentity ();					# Reset Rotation
	#g_Transform = Matrix4fSetRotationFromMatrix3f (g_Transform, g_ThisRot);	# Reset Rotation

    #elif (button == GLUT_LEFT_BUTTON and button_state == GLUT_UP):
    if (button == GLUT_LEFT_BUTTON and button_state == GLUT_UP):
	# Left button released
	g_LastRot = copy.copy (g_ThisRot);					# Set Last Static Rotation To Last Dynamic One
    elif (button == GLUT_LEFT_BUTTON and button_state == GLUT_DOWN):
	# Left button clicked down
	g_LastRot = copy.copy (g_ThisRot);					# Set Last Static Rotation To Last Dynamic One
	g_isDragging = True							        # Prepare For Dragging
	mouse_pt = Point2fT (cursor_x, cursor_y)
        g_ArcBall.click (mouse_pt)						# Update Start Vector And Prepare For Dragging
    return

alpha = 0.
factor = 1./100.

def Draw ():
    global POLIEDRY,RAY,profundidade,g_isFaceSelected
    global alpha,factor

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT); # Clear Screen And Depth Buffer
    glLoadIdentity();				        # Reset The Current Modelview Matrix
    glTranslatef(0.0,0.0,-profundidade);    # Move Left 1.5 Units And Into The Screen 6.0

    ModelMatrix = glGetDoublev(GL_MODELVIEW_MATRIX)


    #glPushMatrix();				            # NEW: Prepare Dynamic Transform
    glMultMatrixf(g_Transform); 		    # NEW: Apply Dynamic Transform
    
    if g_isFaceSelected:
        RAY.draw()

    if POLIEDRY.isOpened:
        POLIEDRY.open_like_BFS(alpha)
        alpha += factor
        #print "Alpha: %f" % alpha
        if((alpha >= 1)or(alpha < 0.)):
            factor *= -1.
            


    #print "Alpha: %f" % alpha

    POLIEDRY.draw()


    #glPopMatrix();				            # NEW: Unapply Dynamic Transform

    glFlush ();                             # Flush The GL Rendering Pipeline
    glutSwapBuffers()
    return
