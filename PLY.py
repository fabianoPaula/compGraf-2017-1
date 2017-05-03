# encoding: UTF-8

from OpenGL.GL import *                                                          
from OpenGL.GLUT import *                                                        
from OpenGL.GLU import *  

from os.path      import isfile
from sys          import exit

from lib.geometry import Point

class PLY(object):

    def __init__(self,filename = "/"):
        self.format = ""
        self.author = ""
        self.comment = ""
        self.variables = []
        self.n_variables = 0
        self.n_vertex = 0
        self.n_faces  = 0 

        self.vertex = []
        self.faces  = []
        

        #if( isfile(filename)):
        #    print "No file given"
        #    print "FILENAME: %s" % (filename)
        #    exit(0)

        end_header = 10000

        with open(filename) as f:
            for ln, line in enumerate(f, 1):
                words = line.split()
#                print line 
#                print words
#                print end_header,self.n_vertex,ln

                # Header of PLY file 
                if not( end_header <= ln):
                    if ( words[0] == "ply"):
                        print "PLY file FORMAT"
                    elif (words[0] == "format"):
                        self.format = line
                    elif (words[0] == "comment"):
                        if (words[1] == "made"):
                            self.autor = " ".join(words[3:])
                        else:
                            self.comment = " ".join(words[1:])
                    elif (words[0] == "element"):
                        if( words[1] == "face"):
                            self.n_faces = int(words[2])
                        elif(words[1] == "vertex"):
                            self.n_vertex = int(words[2])
                    elif (words[0] == "property"):
                        if (words[1] == "float32"):
                            self.n_variables += 1
                            self.variables.append(words[2])
                    elif (words[0] == "end_header"):
                        end_header = ln
                else:
                # Body of PLY file

                    # Reading vertex
                    if ( end_header+self.n_vertex >= ln):
                        self.vertex.append(Point(float(words[0]),float(words[1]),float(words[2])))
 #                       print self.vertex

                    # Reading Faces
                    else:
                        aux_points = []
                        for i in xrange(1,int(words[0])+1):
                            aux_points.append(int(words[i]))
                        self.faces.append(aux_points)
#                        print self.faces

       # exit(0)


class Poliedry(object):
    
    def __init__(self, PLY = None):
        
        if PLY == None:
            print "PLY não fornecido"
            exit(0)

        self.vertex = PLY.vertex
        self.faces  = PLY.faces
        self.colors = [
                (0.0,0.0,0.5), 
                (0.0,0.0,1.0), 
                (0.0,0.5,0.0), 
                (0.0,0.5,0.5), 
                (0.0,0.5,1.0), 
                (0.0,1.0,0.0), 
                (0.0,1.0,0.5), 
                (0.0,1.0,1.0), 
                (0.5,0.0,0.0), 
                (0.5,0.0,0.5), 
                (0.5,0.0,1.0), 
                (0.5,0.5,0.0), 
                (0.5,0.5,0.5), 
                (0.5,0.5,1.0), 
                (0.5,1.0,0.0), 
                (0.5,1.0,0.5), 
                (0.5,1.0,1.0),
                (1.0,0.0,0.0), 
                (1.0,0.0,0.5), 
                (1.0,0.0,1.0), 
                (1.0,0.5,0.0), 
                (1.0,0.5,0.5), 
                (1.0,0.5,1.0), 
                (1.0,1.0,0.0), 
                (1.0,1.0,0.5), 
                (1.0,1.0,1.0)
                ] 
        
        

        return 

    def draw(self):
        if ( len(self.faces[0]) % 3 == 0):
            glBegin(GL_TRIANGLES)
        elif ( len(self.faces[0]) % 4 == 0):
            glBegin(GL_QUADS)
        else:
            glBegin(GL_POLYGON)
#        print len(self.faces)
        for i,face in enumerate(self.faces):
            c = self.colors[i % len(self.colors)]
            glColor3f(c[0],c[1],c[2])
#            print "# face %d" % (i)
            for point in face:
                p = self.vertex[point]
                glVertex3f(p.x,p.y,p.z)
        glEnd()



#    glColor3f(0.0,1.0,0.0)
#    glVertex3f( 1.0, 1.0,-1.0)
