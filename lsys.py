#import matplotlib
#matplotlib.use('agg')

from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Line3DCollection

import numpy as np
import matplotlib.collections as mc
import matplotlib.pyplot as plt

class Turtle:
    def __init__(self):
        self.segs = []

    def go(self, action, *args, **kwargs):
        return getattr(self, action)(*args, **kwargs)

    def draw(self, mag, std=0):
        p0 = self.p.copy()
        self.move(mag, std)
        p1 = self.p.copy()
        
        self.segs.append([p0,p1])

    def move(self, mag, std=0):
        if std > 0:
            mag = np.random.normal(mag, std)
            
        self.p += self.v*mag

    def turn(self, angle, std=0):
        if std > 0:
            angle = np.random.normal(angle, std)
            
        m = self.turn_transform(angle)
        self.v = np.dot(m, self.v)        
        
    def spin(self, angle, std=0):
        raise NotImplementedError()

    def copy(self):
        raise NotImplementedError()

    def turn_transform(self):
        raise NotImplementedError()

    def get_state(self):
        raise NotImplementedError()

    def set_state():
        raise NotImplementedError()
    

class Turtle2D(Turtle):
    def __init__(self, p=None, v=None):
        super().__init__()
        
        self.p = p if p is not None else np.array([0.0,0.0])
        self.v = v if v is not None else np.array([1.0,0.0])

    def copy(self):
        return Turtle2D(p=self.p.copy(),
                        v=self.v.copy())
    
    def turn_transform(self, angle):
        r = angle * np.pi / 180.0

        return np.array([ [ np.cos(r), -np.sin(r) ],
                          [ np.sin(r), np.cos(r) ] ])

    def plot(self):
        segs = np.array(self.segs)

        lc = mc.LineCollection(segs, linewidth=2)

        fig, ax = plt.subplots()

        ax.add_collection(lc)
            
        ax.set_xlim(segs[:,:,0].min(axis=None)-1,
                    segs[:,:,0].max(axis=None)+1)
        ax.set_ylim(segs[:,:,1].min(axis=None)-1,
                    segs[:,:,1].max(axis=None)+1)

        #plt.axis('off')
        plt.show()

    def get_state(self):
        return self.p.copy(), self.v.copy()

    def set_state(self, p, v):
        self.p, self.v = p, v
        
    
class Turtle3D(Turtle):
    def __init__(self, p=None, v=None, u=None):
        super().__init__()
        
        self.p = p if p is not None else np.array([0.0, 0.0, 0.0])
        self.v = v if v is not None else np.array([1.0, 0.0, 0.0])
        self.u = u if u is not None else np.array([0.0, 0.0, 1.0])

    def turn_transform(self, angle, u=None):
        th = angle * np.pi / 180.0
        cth = np.cos(th)
        sth = np.sin(th)

        if u is None:
            u = self.u
        
        return np.array([ [ cth + u[0]*u[0]*(1-cth),      u[0]*u[1]*(1-cth) - u[2]*sth,  u[0]*u[2]*(1-cth) + u[1]*sth ],
                          [ u[1]*u[0]*(1-cth) + u[2]*sth, cth + u[1]*u[1]*(1-cth),       u[1]*u[2]*(1-cth) - u[0]*sth ],
                          [ u[2]*u[0]*(1-cth) - u[1]*sth, u[2]*u[1]*(1-cth) + u[0]*sth,  cth + u[2]*u[2]*(1-cth) ] ])

    def spin(self, angle, std=0):
        if std > 0:
            angle = np.random.normal(angle, std)
            
        m = self.turn_transform(angle)
        self.u = np.dot(m, self.v)

    def copy(self):
        return Turtle3D(p=self.p.copy(),
                        v=self.v.copy(),
                        u=self.u.copy())    

    def plot(self):
        segs = np.array(self.segs)

        lc = Line3DCollection(segs, linewidths=0.6, alpha=0.4)
        
        fig = plt.figure()            
        ax = fig.gca(projection='3d')
        
        ax.add_collection3d(lc)
            
        ax.set_xlim(segs[:,:,0].min(axis=None)-1,
                    segs[:,:,0].max(axis=None)+1)
        ax.set_ylim(segs[:,:,1].min(axis=None)-1,
                    segs[:,:,1].max(axis=None)+1)
        ax.set_zlim(segs[:,:,2].min(axis=None)-1,
                    segs[:,:,2].max(axis=None)+1)
            
        plt.axis('off')
        plt.show()

    def get_state(self):
        return self.p.copy(), self.v.copy(), self.u.copy()

    def set_state(self, p, v, u):
        self.p, self.v, self.u = p, v, u
        
    
class LSystem:
    def __init__(self, axiom, rules, actions, dims=2):
        self.axiom = axiom
        self.rules = rules
        self.actions = actions

        if dims == 2:
            self.turtle_class = Turtle2D
        elif dims == 3:
            self.turtle_class = Turtle3D

    def expand(self, N=1):

        for i in range(N):
            new_axiom = ""
            for element in self.axiom:
                if element in self.rules:
                    new_axiom += self.rules[element]
                else:
                    new_axiom += element
            self.axiom = new_axiom

        return self.axiom
        

    def render(self):
        stack = []

        turtle = self.turtle_class()
        
        for element in self.axiom:
            action = self.actions.get(element, None)

            if action:
                if action[0] == 'push':
                    stack.append(turtle.get_state())
                elif action[0] == 'pop':
                    turtle.set_state(*stack.pop())
                else:
                    turtle.go(*action)

        return turtle

LIBRARY = dict(
    koch = dict(
        rules = {
            'F': 'F+F-F-F+F'
        },
        actions = {
            'F': ( 'draw', 1 ),
            '+': ( 'turn', 90 ),
            '-': ( 'turn', -90 )
        },
        axiom = 'F'
    ),
    sierpinski_triangle = dict(
        rules = {
            'F': 'F-G+F+G-F',
            'G': 'GG'
        },
        actions = {
            'F': ( 'draw', 1 ),
            'G': ( 'draw', 1 ),
            '+': ( 'turn', -120 ),
            '-': ( 'turn', 120 )
        },
        axiom = 'F-G-G'
    ),
    sierpinski_arrowhead = dict(
        rules = {
            'A': 'B-A-B',
            'B': 'A+B+A'
        },
        actions = {
            'A': ( 'draw', 1 ),
            'B': ( 'draw', 1 ),
            '+': ( 'turn', -60 ),
            '-': ( 'turn', 60 )
        },
        axiom = 'A'
    ),
    fern = dict(
        rules = {
            'X': 'F+[[X]-X]-F[-FX]+X',
            'F': 'FF'
        },
        actions = {
            'F': ( 'draw', 1 ),
            '-': ( 'turn', -25 ),
            '+': ( 'turn', 25 ),
            '[': ( 'push', ),
            ']': ( 'pop', )
        },
        axiom = 'X'
    ),
    tritree = dict(
        rules = {
            'A': 'B[[-A][A][+A]]',
            'B': 'BB'
        },
        actions = {
            'A': ( 'draw', .2, 0.02 ),
            'B': ( 'draw', 1, 0.1 ),
            '[': ( 'push', ),
            ']': ( 'pop', ),
            '+': ( 'turn', 30, 3 ),
            '-': ( 'turn', -30, 3 ),
        },
        axiom = 'A',
        dims = 3
    ),
    pentabroccoli = dict(
        rules = {
            'A': 'B[[-A][<-A][<<-A][<<<-A][<<<<-A]]',
            'B': 'BB'
        },
        actions = {
            'A': ( 'draw', 1, .02 ),
            'B': ( 'draw', .5, .02 ),
            '[': ( 'push', ),
            ']': ( 'pop', ),
            '<': ( 'spin', 72, 0 ),
            '-': ( 'turn', -30, 3),
        },
        axiom = 'A',
        dims = 3
    ),
)
    
def main():
    lsys = LSystem(**LIBRARY['pentabroccoli'])
    
    lsys.expand(6)
    turtle = lsys.render()
    turtle.plot()
    plt.savefig('test.png')

if __name__ == "__main__": main()
