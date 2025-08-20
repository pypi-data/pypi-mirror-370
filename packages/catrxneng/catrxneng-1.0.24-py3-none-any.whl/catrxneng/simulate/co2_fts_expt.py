from .expt import Expt

class Co2FtsExpt(Expt):

    def __init__(self, reactors):
        self.reactors = reactors

    def simulate(self):
        self.steps = []
        for reactor in self.reactors:

