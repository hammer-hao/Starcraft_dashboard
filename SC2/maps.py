# -*- coding: utf-8 -*-
"""
Created on Thu Nov 10 23:54:11 2022

@author: hammerhao
"""

rush_distance = {
    "Cosmic Sapphire":[38, 6.5],
    "Waterfall": [32, 7],
    "Data-C": [36, 8],
    "Inside and Out": [32, 6],
    "Moondance": [31, 9],
    "Stargazers": [35, 6.5],
    "Tropical Sacrifice": [37, 7]
    }

num_bases = {
    }

class map:
    def __init__(self, name):
        self.name = name
    def getrushdistance(self):
        return rush_distance[self.name]
    def getbases(self):
        return num_bases[self.name]