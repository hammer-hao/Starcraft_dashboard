# -*- coding: utf-8 -*-
"""
Created on Fri Oct 28 19:53:00 2022

@author: hammerhao
"""
import numpy as np
import pandas as pd

#loading the dataset
data_full_matches = pd.read_csv("C:/Users/hammerhao/OneDrive/Desktop/DS105/matches_data.csv")

data_full_matches = data_full_matches.drop(
    data_full_matches[data_full_matches.Type!="1v1"].index
    )
data_full_matches = data_full_matches.drop(data_full_matches.columns[0], axis=1)
data_full_matches = data_full_matches.drop_duplicates(keep=False)
data_full_matches = data_full_matches[
    (data_full_matches["Map"]=="Cosmic Sapphire") |
    (data_full_matches["Map"]=="Waterfall") |
    (data_full_matches["Map"]=="Data-C") |
    (data_full_matches["Map"]=="Moondance") |
    (data_full_matches["Map"]=="Inside and Out") |
    (data_full_matches["Map"]=="Stargazers") |
    (data_full_matches["Map"]=="Tropical Sacrifice")
]
maps = data_full_matches["Map"].unique()
data_full_matches["Map"].value_counts()