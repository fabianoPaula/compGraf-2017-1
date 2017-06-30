# encoding: utf-8

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import sys
import copy

from ArcBall import * 		# ArcBallT and this tutorials set of points/vectors/matrix types

from lib.geometry import Point,Line
import lib.matrix as matrix
import numpy as np
from polihedron import *
from ply import *

from PIL.Image import open

PI2 = 2.0*3.1415926535		# 2 * PI (not squared!)	// PI Squared

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

POLIHEDRON_SET = 1
POLIEDRY = None
RAY = Line(Point(0.0,0.0,0.0,),Point(1.0,1.0,1.0))

ModelMatrix = None

profundidade = 12.0
translating_rate = 1.0

imageID = 0


def set_poliedry(poliedry_index):
    global POLIEDRY
    global g_isFaceSelected
    filename = ""

    if(poliedry_index == 1):
        filename = "data_ply/tetrahedron.ply"
    elif (poliedry_index == 2):
        filename = "data_ply/cube.ply"
    elif (poliedry_index == 3):
        filename = "data_ply/octahedron.ply"
    elif (poliedry_index == 4):
        filename = "data_ply/dodecahedron.ply"
    elif (poliedry_index == 5):
        filename = "data_ply/icosahedron.ply"

    POLIEDRY = Polihedron(PLY(filename))
    g_isFaceSelected = False
    print filename
    print "POLIEDRY CHANGED!"

# A general OpenGL initialization function.  Sets all of the initial parameters.
def Initialize (Width, Height, imageName = "images/water.jpg"):				# We call this right after our OpenGL window is created.
    global g_quadratic, ModelMatrix, imageID

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

    imageID = loadImage(1)
    set_poliedry(1)

    return True

# The function called whenever a key is pressed. Note the use of Python tuples to pass in: (key, x, y)
def keyPressed(*args):
    global g_quadratic
    global profundidade
    global translating_rate
    global POLIEDRY,alpha
    global imageID
    # If escape is pressed, kill everything.
    key = args [0]
    if key == ESCAPE:
        gluDeleteQuadric (g_quadratic)
        sys.exit ()
    elif key == 'i':
        profundidade += translating_rate
    elif key == 'I':
        profundidade -= translating_rate
    elif key == 'a':
        if POLIEDRY.face_selected == -1:
            print "Please, Select a face to open the poliedry"
            return
        alpha = 0.
        POLIEDRY.animate()
    elif key == 'A':
        POLIEDRY.static()
    elif key == 'o':
        if POLIEDRY.face_selected == -1:
            print "Please, Select a face to open the poliedry."
            return
        alpha = 0.
        POLIEDRY.open()
    elif key == 'O':
        POLIEDRY.close()
    elif key == 'm':
        if POLIEDRY.face_selected == -1:
            print "Please, Select a face to focus the texture."
            return
        POLIEDRY.set_texture()
        POLIEDRY.build_texture()
    elif key == 'M':
        POLIEDRY.unset_texture()

    elif key == '1':
        set_poliedry(1)
    elif key == '2':
        set_poliedry(2)
    elif key == '3':
        set_poliedry(3)
    elif key == '4':
        set_poliedry(4)
    elif key == '5':
        set_poliedry(5)


    elif key == 'q':
        imageID = loadImage(1)
    elif key == 'w':
        imageId = loadImage(2)
    elif key == 'e':
        imageID = loadImage(3)
    elif key == 'r':
        imageID = loadImage(4)
    elif key == 't':
        imageID = loadImage(5)

    #elif key == 'u':
    #    POLIEDRY.skeletonOn()
    #elif key == 'j':
    #    POLIEDRY.skeletonOff()


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
            print "Estou vendo o evento"
            if(POLIEDRY.face_intersect(RAY) != -1):
                POLIEDRY.face_select(POLIEDRY.last_face_clicked)
                print "Seleted face %d" % POLIEDRY.face_selected
                g_isFaceSelected = True
        elif (POLIEDRY.face_intersect(RAY) == POLIEDRY.face_selected)and\
                (POLIEDRY.isOpened == False):
                print "Face unselected"
                POLIEDRY.face_unselect()
                g_isFaceSelected = False

    g_isDragging = False
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

def loadImage(image_index):
    """Load an image file as a 2D texture using PIL"""
    if(image_index == 1):
        imageName = "data_image/image1.jpg"
    elif (image_index == 2):
        imageName = "data_image/image2.jpg"
    elif (image_index == 3):
        imageName = "data_image/image3.jpg"
    elif (image_index == 4):
        imageName = "data_image/image4.jpg"
    elif (image_index == 5):
        imageName = "data_image/image5.jpg"

    # PIL defines an "open" method which is Image specific!
    im = open(imageName)
    try:
            ix, iy, image = im.size[0], im.size[1], im.tobytes("raw", "RGBA", 0, -1)
    except (SystemError, ValueError):
            ix, iy, image = im.size[0], im.size[1], im.tobytes("raw", "RGBX", 0, -1)
    except AttributeError:
            ix, iy, image = im.size[0], im.size[1], im.tostring("raw", "RGBX", 0, -1)

    ID = glGenTextures(1)

    glBindTexture(GL_TEXTURE_2D, ID)
    glPixelStorei(GL_UNPACK_ALIGNMENT,1)

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
    return ID

def setupTexture():
    global imageID

    """Render-time texture environment setup"""

    # Configure the texture rendering parameters
    glEnable(GL_TEXTURE_2D)

    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
    # Re-select our texture, could use other generated textures if we had generated them earlier...
    glBindTexture(GL_TEXTURE_2D, imageID)


alpha = 0.
factor = 1./100.

def Draw ():
    global POLIEDRY,RAY,profundidade,g_isFaceSelected
    global alpha,factor

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT); # Clear Screen And Depth Buffer
    glLoadIdentity();				        # Reset The Current Modelview Matrix
    glTranslatef(0.0,0.0,-profundidade);    # Move Left 1.5 Units And Into The Screen 6.0

    ModelMatrix = glGetDoublev(GL_MODELVIEW_MATRIX)

    glMultMatrixf(g_Transform); 		    # NEW: Apply Dynamic Transform

    if POLIEDRY.isAnimated:
        POLIEDRY.open_like_BFS(alpha)
        alpha += factor
        #print "Alpha: %f" % alpha
        if((alpha >= 1)or(alpha < 0.)):
            factor *= -1.

    #RAY.draw()

    if POLIEDRY.isOpened:
        POLIEDRY.open_like_BFS(1.0)

    if POLIEDRY.useTexture:
        setupTexture()
    else:
        glDisable(GL_TEXTURE_2D)

    POLIEDRY.draw()

    glFlush();                             # Flush The GL Rendering Pipeline
    glutSwapBuffers()
    return
