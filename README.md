# jobscrapers
As I was wondering to track my applications' progress, I needed to update the "dashboard" of the job offers that were being pubilshed every week. Thus, I decided to build a scraper who could help me to check periodically.

I will upload the script shortly.

'''python
import os
import numpy as np
from math import *
import matplotlib.pyplot as plt
import matplotlib.animation as animation

os.chdir("/Users/andrealandini/Desktop")
plt.style.use("ggplot")


class DB:
    def __init__(self):

        self.k = 1
        self.qì = 6
        self.chi = .4
        self.d = np.linspace(0,self.chi*self.qì*self.k,1000)


        self.beta_b = .6
        self.y1b = 10
        self.y2b = 11
        self.q = 5
        #db = (d*(1+beta_b)+beta_b*(y1b-q*k))**(-1)*(y2b+qì*k)
        self.db = np.piecewise(self.d, [self.d < self.chi*self.qì*self.k, self.d >= self.chi*self.qì*self.k],
                        [lambda x: (self.qì*self.k+self.y2b)/(x*(1+self.beta_b)+self.beta_b*(self.y1b-self.q*self.k)), 0])        
'''
