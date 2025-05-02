# -*- coding: utf-8 -*-


import numpy as np
import tkinter as tk
from tkinter import ttk
import pygame
import json
import requests
import math
import threading
import os
import random
import time
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
from scipy.io import wavfile
from IPython.display import Audio, display



"""# Setting Up Test (Initialization)
(D = Ariella; O = Tenzin)
"""

pygame.mixer.init() # initializes pygame mixer, which creates sound effects within typing test
key_sound = pygame.mixer.Sound('type.wav') # loads file that provides sound effects (key tapping sounds as user types)
start_time = None # tracks elapsed time (starts at 0)
char_position = 0 # tracks position of character within string of text (starts at 0)
errors = 0 # tracks number of mistakes made by user (starts at 0)
wpm_tracker = [] # tracks words per minute values as they change throughout a given test
character_mistype = defaultdict(int) # tracks number of times user incorrectly types a particular character
word_counter = Counter() # tracks number of times a particular word emerges during the test
total_char = 0 # tracks total number of characters encountered during a test (starts at 0)

"""# Loading Text
(D = Ariella; O = Tenzin)
"""

API_URL = "https://quoteapi.pythonanywhere.com/" # test retrieves quotations from this site
def retrieve_quotation(): # function retrieves quotation
  try:
    quotation = requests.get(API_URL) # requests quotation from our chosen API
    if quotation.ok: # if quotation can be retrieved
      text = quotation.json()['content'] # specifically transfers quotation from API to Python; JSON string is converted into Python object
      for word in text.split(): # isolates each word in the text
        word_counter[word.lower()] += 1 # every time a particular word appears, a word counter is updated to keep track of how many times that word has appeared during the test; also makes sure each word is lowercase
      return text
  except: # if quotation cannot be retrieved
    fallback = random.choice(["We hope you're enjoying our typing test!","Feel free to share this test with your friends to see whose typing reigns supreme!"]) # example sentences that user can type if quotations do not load
    for word in fallback.split(): # isolates each word in the text
      word_counter[word.lower()] += 1 # every time a particular word appears, a word counter is updated to keep track of how many times that word has appeared during the test; also makes sure each word is lowercase
    return fallback

"""# Establishing Proximity of Letters (Relative to Each Other)
(D = Ariella; O = Tenzin)
"""

keyboard_proximity = { # two letters were considered close to each other -- i.e., in near proximity -- when they were adjacent to each other, whether horizontally, vertically, or diagonally
    'a':['q','w','s','z'],'s':['a','w','e','d','x','z'],'d':['s','e','r','f','c','x'],'f':['d','r','t','g','v','c'],'g':['f','t','y','h','b','v'],'h':['g','y','u','j','n','b'],'j':['h','u','i','k','m','n'],'k':['j','i','o','l','m'],'l':['k','o','p'],'q':['w','a'],'w':['q','e','s','a'],'e':['w','r','d','s'],'r':['e','t','f','d'],'t':['r','y','g','f'],'y':['t','u','h','g'],'u':['y','i','j','h'],'i':['u','o','k','j'],'o':['i','p','l','k'],'p':['o','l'],'z':['a','s','x'],'x':['z','s','d','c'],'c':['x','d','f','v'],'v':['c','f','g','b'],'b':['v','g','h','n'],'n':['b','h','j','m'],'m':['n','j','k']
}

"""# Constructing GUI
(D = Ariella; O = Tenzin)
"""

class PythonTypingTestApp: # defines class of GUI
  def __init__(self,root): # initializes new objects within the class
    self.root = root # sets up and saves main window of typing test
    self.root.title("Python Typing Test") # creates title of typing test
    self.root.geometry('900x500') # specifies size of window

    self.setup_widgets() # places the elements of our GUI within the test (detailed in next section of the code)
    self.reset_test() # clears all previous data before (re)starting test

"""# Adding Specific Features to GUI
(D = Ariella; O = Tenzin)
"""

def add_features(self): # adds different elements to typing test
  self.difficulty = tk.StringVar(value = "medium") # stores difficulty level, with medium difficulty level as default
  ttk.Label(self.root, text = "Difficulty:").pack() # labels difficulty level selection window ("Difficulty:")
  ttk.Combobox(self.root, textvariable = self.difficulty, values = ["easy","medium","hard"]).pack() # allows user to select difficulty (either "easy," "medium," or "hard") through a dropdown option

  self.display_text = tk.Text(self.root, height = 4, font=('Times New Roman',18)) # displays text for user to type
  self.display_text.pack(fill = 'x') # displayed horizontally for readability
  self.display_text.config(state = 'disabled') # read-only display

  self.input_var = tk.StringVar() # stores text as user types
  self.entry = tk.Entry(self.root, textvariable = self.input_var, font=('Times New Roman',18)) # provides box in which user can type; user will type in same font as display text
  self.entry.pack(fill = 'x') # displayed horizontally (text should be written from left to right)
  self.entry.bind('<KeyRelease>', self.on_key_press) # checks which key is pressed, which allows program to determine accuracy of typed text as compared to provided text

  self.progress = ttk.Progressbar(self.root, maximum = 100) # creates progress bar, with 100% as maximum value
  self.progress.pack(fill = 'x') # displayed horizontally (progress bars are generally horizontal)

  self.restart_btn = ttk.Button(self.root, text = "Restart Test", command = self.reset_test) # user can restart typing test by pressing "Restart Test" button

"""# Resetting Typing Test
(D = Ariella; O = Tenzin)
"""

def reset_test (self): # clears prior attempt and creates fresh test for user after restarting
  global start_time, char_position, errors, total_char # makes sure these variables can be accessed within this function, even though they are created outside the function
  self.test = retrieve_quotation() # calls function that retrieves quotation, which gives users a new quotation to type
  self.entry.delete(0, 'end') # clears entry box
  self.display_text.config(state = 'normal') # allows display to be edited (in this case, by updating it to create a new test)
  self.display_text.delete('1.0','end') # clears text from previous test
  self.display_text.insert('1.0',self.text) # places new text into text display window
  self.display_text.config(state = 'disabled') # switches display back to read-only format
  start_time = None # resets elapsed time to 0
  char_position = 0 # resets position of character within string of text to 0
  errors = 0 # resets number of mistakes made by user to 0
  total_char = len(self.text) # tracks total number of characters encountered during new test
  self.progress['value'] = 0 # resets progress bar to 0%
  self.input_var.set("") # clears "StringVar" variable so that no text is stored from the previous test and text from the new test can be stored instead

"""# Indicating What Happens When a User Presses a Key
(D = Ariella; O = Tenzin)
"""

def on_key_press(self, event): # checks which key is pressed
  global start_time, char_position, errors, total_char # makes sure these variables can be accessed within this function, even though they are created outside the function

  if not start_time: # if timer has not started yet
    start_time = time.time() # starts timer once user first presses key