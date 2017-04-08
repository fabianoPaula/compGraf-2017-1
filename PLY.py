# encoding: UTF-8

from lib.geometry import *
from os.path      import isfile
from sys          import exit

class PLY(object):

    def __init__(self):
        self.format = ""
        self.author = ""
        self.comment = ""
        self.variables = []
        self.n_variables = 0
        self.n_vertex = 0
        self.n_faces  = 0 
        

    def __init__(self,filename = "/"):
        self.format = ""
        self.author = ""
        self.comment = ""
        self.variables = []
        self.n_variables = 0
        self.n_vertex = 0
        self.n_faces  = 0 
        

        if( isfile(filename)):
            print "No file given"
            print "FILENAME: %s" % (filename)
            exit(0)

        with open(filename) as f:
            for ln, line in enumerate(f, 1):
                words = line.split()

                # Header of PLY file 
                if not( end_header >= ln):
                    if ( word[0] == "ply"):
                        print "PLY file FORMAT"
                    else if (word[0] == "format"):
                        self.format = line
                    else if (word[0] == "comment"):
                        if (word[1] == "made"):
                            self.autor = " ".join(word[3:])
                        else:
                            self.comment = " ".join(word[1:])
                    else if (word[0] == "element"):
                        if( word[1] == "face"):
                            self.n_faces = int(word[2])
                        else if(word[1] == "vertex"):
                            self.n_vertex = int(word[2])
                    else if (word[0] == "property"):
                        if (word[1] == "float32"):
                            self.n_variables += 1
                            self.variables.append(word[2])
                    else if (word[0] == "end_header"):
                        end_header = ln
                else:
                # Body of PLY file
                    


                
        return


class Poliedry(object):
    
    def __init__(self):
        return 
