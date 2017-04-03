# encoding: UTF-8

from OpenGL.GL   import *
from OpenGL.GLUT import *
from OpenGL.GLU  import *
import serial
import os
import threading 

ESCAPE = '\033'

window = 0 

#rotation
X_AXIS = .0
Y_AXIS = .0
Z_AXIS = .0

DIRECTION = 1


def initGL(width,height):
    glClearColor(0.0,0.0,0.0,0.0)
    glClearDepth(1.0)
    glDepthFunc(GL_LESS)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0,float(width)/float(height),0.1,100.0)
    glMatrixMode(GL_MODELVIEW)


def keyPressed(*args):
    global ESCAPE
    if args[0] == ESCAPE:
        sys.exit()

def drawGLScene():
    global X_AXIS,Y_AXIS,Z_AXIS
    global DIRECTION

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glLoadIdentity()
    glTranslate(0.0,0.0,-6.0)

    glRotate(X_AXIS,1.0,0.0,0.0)
    glRotate(X_AXIS,0.0,1.0,0.0)
    glRotate(X_AXIS,0.0,0.0,1.0)

    # Draw Cube (multiple quads)
    glBegin(GL_QUADS)

    glColor3f(0.0,1.0,0.0)
    glVertex3f( 1.0, 1.0,-1.0)
    glVertex3f(-1.0, 1.0,-1.0)
    glVertex3f(-1.0, 1.0, 1.0)
    glVertex3f( 1.0, 1.0, 1.0) 
                        
    glColor3f(1.0,0.0,0.0)
    glVertex3f( 1.0,-1.0, 1.0)
    glVertex3f(-1.0,-1.0, 1.0)
    glVertex3f(-1.0,-1.0,-1.0)
    glVertex3f( 1.0,-1.0,-1.0) 
               
    glColor3f(0.0,1.0,0.0)
    glVertex3f( 1.0,1.0,1.0)
    glVertex3f(-1.0,1.0,1.0)
    glVertex3f(-1.0,-1.0,1.0)
    glVertex3f(1.0,-1.0, 1.0)

    glColor3f(1.0,1.0,0.0)
    glVertex3f(1.0,-1.0,-1.0)
    glVertex3f(-1.0,-1.0,-1.0)
    glVertex3f(-1.0,1.0,-1.0)
    glVertex3f( 1.0,1.0,-1.0)

    glColor3f(0.0,0.0,1.0)
    glVertex3f(-1.0,1.0,1.0) 
    glVertex3f(-1.0,1.0,-1.0)
    glVertex3f(-1.0,-1.0,-1.0) 
    glVertex3f(-1.0,-1.0,1.0) 

    glColor3f(1.0,0.0,1.0)
    glVertex3f(1.0,1.0,-1.0) 
    glVertex3f(1.0,1.0, 1.0)
    glVertex3f(1.0,-1.0,1.0)
    glVertex3f(1.0,-1.0,-1.0)


    glEnd()

    X_AXIS = X_AXIS - 0.3
    Z_AXIS = Z_AXIS - 0.3

    glutSwapBuffers()

def main():
    global window

    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(640,480)
    glutInitWindowPosition(200,200)

    window = glutCreateWindow('OpenGL Python Cube')

    glutDisplayFunc(drawGLScene)
    glutIdleFunc(drawGLScene)
    glutKeyboardFunc(keyPressed)
    initGL(640,480)
    glutMainLoop()

if __name__ == "__main__": main()
