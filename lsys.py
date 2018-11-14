import matplotlib
matplotlib.use('agg')

import numpy as np
import matplotlib.collections as mc
import matplotlib.pyplot as plt

class State:
    def __init__(self, p, v):
        self.p = np.array(p)
        self.v = np.array(v)

    def copy(self):
        return State(p=self.p.copy(),
                     v=self.v.copy())

    def move(self, mag):
        self.p += self.v*mag

    def turn(self, angle):
        r = angle * np.pi / 180.0
        m = np.array([ [ np.cos(r), np.sin(r) ],
                       [ -np.sin(r), np.cos(r) ] ])
        
        self.v = np.dot(m, self.v)

class Turtle:
    def __init__(self):
        self.state = State(p=[0.0,0.0],
                           v=[1.0,0.0])

        self.segs = []

    def go(self, action, *args, **kwargs):
        fn = getattr(self, action)(*args, **kwargs)
        
    def draw(self, mag):
        p0 = self.state.p.copy()
        self.move(mag)
        p1 = self.state.p.copy()
        
        self.segs.append([p0,p1])
        
    def move(self, mag):
        self.state.move(mag)
        
    def turn(self, angle):
        self.state.turn(angle)

    def plot(self):
        segs = np.array(self.segs)
        lc = mc.LineCollection(segs, linewidth=2)
        fig, ax = plt.subplots()
        ax.set_xlim(segs[:,:,0].min(axis=None)-1,
                    segs[:,:,0].max(axis=None)+1)
        ax.set_ylim(segs[:,:,1].min(axis=None)-1,
                    segs[:,:,1].max(axis=None)+1)
        ax.add_collection(lc)
        plt.show()
        
    
class LSystem:
    def __init__(self, axiom, rules, actions):
        self.axiom = axiom
        self.rules = rules
        self.actions = actions

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

        turtle = Turtle()
        
        for element in self.axiom:
            action = self.actions.get(element, None)

            if action:
                if action[0] == 'push':
                    stack.append(turtle.state.copy())
                elif action[0] == 'pop':
                    turtle.state = stack.pop()
                else:
                    turtle.go(*action)

        return turtle

def koch():
    rules = {
        'F': 'F+F-F-F+F'
    }

    actions = {
        'F': ( 'draw', 1 ),
        '+': ( 'turn', -90 ),
        '-': ( 'turn', 90 )
    }

    return LSystem('F', rules, actions)

def sierpinski():
    rules = {
        'F': 'F-G+F+G-F',
        'G': 'GG'
    }

    actions = {
        'F': ( 'draw', 1 ),
        'G': ( 'draw', 1 ),
        '+': ( 'turn', 120 ),
        '-': ( 'turn', -120 )
    }

    return LSystem('F-G-G', rules, actions)

def fern():
    rules = {
        'X': 'F+[[X]-X]-F[-FX]+X',
        'F': 'FF'
    }

    actions = {
        'F': ( 'draw', 1 ),
        '-': ( 'turn', 25 ),
        '+': ( 'turn', -25 ),
        '[': ( 'push', ),
        ']': ( 'pop', )
    }

    return LSystem('X', rules, actions)
    
def main():
    lsys = fern()
    lsys.expand(7)
    turtle = lsys.render()
    turtle.plot()
    plt.savefig('test.png')

if __name__ == "__main__": main()
