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

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

import math

import copy

from lib import matrix
from lib.geometry import Point,Polygon,Line,Box

import numpy as np



#from Image import open


class Polihedron(object):

    def __init__(self, PLY = None):

        if PLY == None:
            print "PLY não fornecido"
            exit(0)

        self.box    = Box()
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

        self.isOpened = False
        self.isAnimated = False
        self.useTexture = False
        self.mapRotate  = matrix.identity()

        # Contructing graph

        # contruindo listas com as arestas de cada face
        #edges_per_face = [[(face[i],face[i]) for i in xrange(len(face))] for face in self.faces ]
        edges_per_face = []
        points_per_face = []
        points_per_face_orig = []
        polygons = []
        #print len(self.vertex)
        #print len(self.faces)

        for face in self.faces:
            #print face
            edges_per_face.append([])
            points_per_face.append([])
            points_per_face_orig.append([])
            for i in xrange(len(face)):
                points_per_face[-1].append(copy.deepcopy(self.vertex[face[i]]))
                points_per_face_orig[-1].append(copy.deepcopy(self.vertex[face[i]]))
                if i  != (len(face)-1):
                    edges_per_face[-1].append((face[i],face[i+1]))
                else:
                    edges_per_face[-1].append((face[i],face[0]))
            polygons.append(Polygon(points_per_face_orig[-1]))

        adjacences_list = []
        edge_between_faces = {}

        # Testando aonde uma aresta pode estar nas outras faces
        for i in xrange(len(edges_per_face)):
            adjacences_list.append([])
            for j in xrange(len(edges_per_face[i])):
                edge = edges_per_face[i][j]
                for k in xrange(len(edges_per_face)):
                    if k != i:
                        if (((edge[1],edge[0]) in edges_per_face[k])or((edge[0],edge[1]) in edges_per_face[k])) :
                            adjacences_list[i].append(k)
                            edge_between_faces[(i,k)] = edge
                            edge_between_faces[(k,i)] = edge
                            break
            if len(edges_per_face[i]) != len(adjacences_list[i]):
                print "Inconsistence in graph contruction"

        self.edges_per_face   = edges_per_face
        self.points_per_face  = points_per_face
        self.points_per_face_orig  = points_per_face_orig
        self.adjacences_list  = adjacences_list
        self.polygons         = polygons
        self.edge_between_faces = edge_between_faces
        self.selected = [0 for elem in edges_per_face]
        self.face_selected = -1

        return



    def draw(self):
        points = []

        for i,face in enumerate(self.faces):
            # informando ao OpenGl o que vou desenhar
            if ( len(face) % 3 == 0):
                glBegin(GL_TRIANGLES)
            elif ( len(face) % 4 == 0):
                glBegin(GL_QUADS)
            else:
                glBegin(GL_POLYGON)

            # vendo se é escolhido
            if not self.useTexture:
                if(self.selected[i] == 1):
                    glColor3f(0.,0.,0.)
                else:
                    c = self.colors[i % len(self.colors)]
                    glColor3f(1.0*c[0],1.0*c[1],1.0*c[2])

            if (self.isOpened or self.isAnimated):
                points = self.points_per_face[i]
            else:
                points = self.points_per_face_orig[i]

            for point in points:
                if self.useTexture:
                    p = self.box.normalize(point.transform(self.mapRotate))
                    glTexCoord2f(p.x,p.y)
                    glVertex3f(point.x,point.y,point.z)
                else:
                    glVertex3f(point.x,point.y,point.z)


            glEnd()

    def face_intersect(self,ray):
        face_to_select = -1
        smaller_u = 100000000000000000.0

        for i,poly in enumerate(self.polygons):
            result = ray.intersectToPlane(poly)
            if not(result == None) and (poly.contains(result[0])):
                if abs(result[1]) < abs(smaller_u):
                    smaller_u = abs(result[1])
                    face_to_select = i

        self.last_face_clicked = face_to_select
        return face_to_select

    def face_select(self,i):
        self.selected[self.last_face_clicked] = 1.
        self.face_selected = self.last_face_clicked

    def face_unselect(self):
        self.selected[self.face_selected] = 0.
        self.face_selected = -1

    def open_like_BFS(self,alpha):
        Q = []
        visite1 = [False for i in self.faces]
        transf_vec = [None for i in self.faces]
        altura = [0 for i in self.faces]

        q0 = self.face_selected
        Q.append(q0)
        visite1[q0] = True
        transf_vec[q0] = matrix.identity()
        altura[q0] = 1.

        self.points_per_face[q0] = copy.deepcopy(self.points_per_face_orig[q0])

        while len(Q) > 0:
            q1 = Q.pop(0)
            for v in self.adjacences_list[q1]:
                if visite1[v] == False :
                    visite1[v] = True
                    Q.append(v)
                    altura[v] = altura[q0] + 1

                    #print "------------------------------------------------"
                    #print (q1,v)

                    N1 = self.polygons[q1].normal
                    N2 = self.polygons[v].normal

                    (np1,np2) = self.edge_between_faces[(q1,v)]

                    v0 = self.vertex[np1]
                    v1 = self.vertex[np2]

                    edge = Line(v0,v1)
                    # ângulo de rotação
                    # para testar o ângulo é preciso fazer o produto interno
                    ang = np.rad2deg(math.acos(N1.dotProd(N2)))
                    # Eixo de rotação
                    # edge.dir

                    axis = edge.dir

                    if axis.tripleProd(N1,N2) > 0:
                        ang = -ang

                    ang = alpha*ang

                    R = matrix.translateAndRotate(ang,v1,edge.dir)
                    #R = matrix.translateAndRotate(ang,v0,edge.dir)

                    transf_vec[v] = matrix.dot(transf_vec[q1],R)
                    #transf_vec[v] = R

                    for i in xrange(len(self.points_per_face[v])):
                        self.points_per_face[v][i] =\
                        self.points_per_face_orig[v][i].transform(transf_vec[v])

        if self.useTexture:
            axis_z = Point(0.,0.,1.)

            angle_z = axis_z.dotProd(self.polygons[q0].normal)
            axis_r = axis_z.crossProd(self.polygons[q0].normal)

            self.mapRotate = matrix.translateAndRotate(angle_z,axis_r,self.points_per_face[q0][0])

            for points in self.points_per_face:
                for point in points:
                    self.box.add(point.transform(self.mapRotate))

            self.box.setParameters()

    def open(self):
        self.isOpened = True

    def close(self):
        self.isOpened = False

    def set_texture(self):
        self.useTexture = True

    def unset_texture(self):
        self.useTexture = False

    def animate(self):
        self.isAnimated = True

    def static(self):
        self.isAnimated = False
