#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
## @package geometry
#
#  Classes and geometric utilities commonly used in computational geometry, such as:
#  point, line, polygon, triangle and box.
#
#  @author Flavia Cavalcanti
#  @date 01/02/2017
#


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


        end_header = 10000

        with open(filename) as f:
            for ln, line in enumerate(f, 1):
                words = line.split()

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
                    # Reading Faces
                    else:
                        aux_points = []
                        for i in xrange(1,int(words[0])+1):
                            aux_points.append(int(words[i]))
                        self.faces.append(aux_points)
