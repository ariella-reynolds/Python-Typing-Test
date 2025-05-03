# -*- coding: utf-8 -*-

import numpy as np
import tkinter as tk
from tkinter import ttk
import pygame
import json
import requests
#import math
#import threading
#import os
import random
import time
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
#from scipy.io import wavfile
#from IPython.display import Audio, display


# Setting Up Test (Initialization)
# (D = Ariella; O = Tenzin)

pygame.mixer.init() # initializes pygame mixer, which creates sound effects within typing test
try:
  key_sound = pygame.mixer.Sound('type.wav') # loads file that provides sound effects (key tapping sounds as user types)
except Exception as e:
  print(f"Sound loading error: {e}")
  key_sound = None

# Global Variables
start_time = None # tracks elapsed time (starts at 0)
char_position = 0 # tracks position of character within string of text (starts at 0)
errors = 0 # tracks number of mistakes made by user (starts at 0)
wpm_tracker = [] # tracks words per minute values as they change throughout a given test
character_mistype = defaultdict(int) # tracks number of times user incorrectly types a particular character
word_counter = Counter() # tracks number of times a particular word emerges during the test
total_char = 0 # tracks total number of characters encountered during a test (starts at 0)

"""# Loading Text
(D = Tenzin; O = Ariella)
"""
# Attempt to load local JSON passages from typing_passages.json
try:
    with open("typing_passages.json", "r", encoding="utf-8") as f:
        LOCAL_PASSAGES = json.load(f).get("passages", [])
except (FileNotFoundError, json.JSONDecodeError):
    LOCAL_PASSAGES = []

# Built-in fallback passages if JSON is missing or broken
FALLBACK_PASSAGES = [
    "We hope you're enjoying our typing test!",
    "Feel free to share this test with your friends to see whose typing reigns supreme!",
    "Sometimes the best way to start is simply to begin, one word at a time.",
    "This is a fallback passage, used when your local text file can't be found."
]

def retrieve_quotation(num_paragraphs=3):
    if LOCAL_PASSAGES:
        return random.sample(LOCAL_PASSAGES, k=num_paragraphs)
    else:
        print("Using fallback passage — typing_passages.json missing or empty.")
        return random.sample(LOCAL_PASSAGES, k=num_paragraphs)

    for word in text.split():
        word_counter[word.lower()] += 1
    return text

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

    #multi-stage tracking variables
    self.paragraphs = []
    self.current_index = 0
    self.total_errors = 0
    self.total_chars = 0
    self.total_words = 0
    self.full_start_time = None

    self.setup_widgets() # places the elements of our GUI within the test (detailed in next section of the code)
    self.reset_test() # clears all previous data before (re)starting test
  
  """# Adding Specific Features to GUI (D = Ariella, Tenzin)"""
  def setup_widgets(self): # adds different elements to typing test
    self.root.configure(bg="#4682b4")  # Background color

    heading = tk.Label(self.root, text="Python Typing Test", font=('Times New Roman', 24, 'bold'), bg="#fda4ba", fg="#fffffd")
    heading.pack(pady=(20, 10))

    self.difficulty = tk.StringVar(value = "medium") # stores difficulty level, with medium difficulty level as default
    ttk.Label(self.root, text="Select Difficulty:", font=('Times New Roman', 14), background="#f4f4f4").pack(pady=(20, 5)) # labels difficulty level selection window ("Difficulty:")
    ttk.Combobox(self.root, textvariable = self.difficulty, values = ["easy","medium","hard"]).pack() # allows user to select difficulty (either "easy," "medium," or "hard") through a dropdown option

    self.display_text = tk.Text(self.root, height = 4, font=('Times New Roman',18), wrap='word', bg='#ffffff', fg='#333333', relief='solid', bd=1) # displays text for user to type
    self.display_text.pack(fill = 'x', padx=20, pady=10) # displayed horizontally for readability
    self.display_text.config(state = 'disabled') # read-only display

    self.input_var = tk.StringVar() # stores text as user types
    self.entry = tk.Entry(self.root, textvariable = self.input_var, font=('Times New Roman',18), bg='#f0f0f0', fg='#000000', relief='groove', bd=2) # provides box in which user can type; user will type in same font as display text
    self.entry.pack(fill = 'x', padx=20, pady=(0, 15)) # displayed horizontally (text should be written from left to right)
    self.entry.bind('<KeyRelease>', self.on_key_press) # checks which key is pressed, which allows program to determine accuracy of typed text as compared to provided text

    self.progress = ttk.Progressbar(self.root, maximum = 100) # creates progress bar, with 100% as maximum value
    self.progress.pack(fill = 'x', padx=20, pady=(0, 15)) # displayed horizontally (progress bars are generally horizontal)
    
    self.end_btn = ttk.Button(self.root, text="End Test", command=self.end_test, style="Pink.TButton")
    self.end_btn.pack(pady=(0, 20))

    # Custom styled pink button
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Pink.TButton", background="#fda4ba", foreground="white", font=('Times New Roman', 14, 'bold'), padding=6)
    style.map("Pink.TButton",background=[("active", "#fdab4a")],foreground=[("disabled", "#ccc")])
    
    self.restart_btn = ttk.Button(self.root, text = "Restart Test", command = self.reset_test, style="Pink.TButton") # user can restart typing test by pressing "Restart Test" button
    self.restart_btn.pack(pady=(5, 20))
  
  """# Resetting Typing Test (D = Ariella; O = Tenzin)"""
  def reset_test (self): # clears prior attempt and creates fresh test for user after restarting
    global start_time, char_position, errors, total_char # makes sure these variables can be accessed within this function, even though they are created outside the function
    self.paragraphs = retrieve_quotation(num_paragraphs=3) # calls function that retrieves quotation, which gives users a new quotation to type
    self.current_index = 0
    self.total_errors = 0
    self.total_chars = 0
    self.total_words = 0
    self.full_start_time = None
    self.load_paragraph()
    
    self.entry.delete(0, 'end') # clears entry box
    self.display_text.config(state = 'normal') # allows display to be edited (in this case, by updating it to create a new test)
    self.display_text.delete('1.0','end') # clears text from previous test
    self.display_text.insert('1.0',self.test) # places new text into text display window
    self.display_text.config(state = 'disabled') # switches display back to read-only format
    start_time = None # resets elapsed time to 0
    char_position = 0 # resets position of character within string of text to 0
    errors = 0 # resets number of mistakes made by user to 0
    total_char = len(self.test) # tracks total number of characters encountered during new test
    self.progress['value'] = 0 # resets progress bar to 0%
    self.input_var.set("") # clears "StringVar" variable so that no text is stored from the previous test and text from the new test can be stored instead

  ''' (D = Tenzin; O = Ariella)'''
  def load_paragraph(self):
    global char_position, errors, total_char, start_time

    if self.current_index == 0:
      self.full_start_time = time.time()

    self.test = self.paragraphs[self.current_index]
    self.display_text.config(state='normal')
    self.display_text.delete('1.0', 'end')
    self.display_text.insert('1.0', self.test)
    self.display_text.config(state='disabled')

    self.entry.config(state='normal')
    self.entry.delete(0, 'end')

    start_time = None
    char_position = 0
    errors = 0
    total_char = len(self.test)
    self.progress['value'] = 0
    self.input_var.set("") 
   
  """# Indicating What Happens When a User Presses a Key (D = Tenzin; O = Ariella)"""
  def on_key_press(self, event):
    global start_time, char_position, errors, total_char
    if not start_time:
      start_time = time.time()
      typed_text = self.entry.get()
      target_text = self.test

    # Stop if user types more than target
    if char_position >= len(target_text):
      return
    
    expected_char = target_text[char_position]

    # Sound effect on keypress
    key_sound.play()

    if typed_text[-1:] == expected_char:
      char_position += 1
      self.progress['value'] = (char_position / total_char) * 100
    else:
      errors += 1
      character_mistype[expected_char] += 1
      
    if char_position == total_char:
      end_time = time.time()
      elapsed_minutes = (end_time - start_time) / 60
      words_typed = len(self.test.split())
      wpm = words_typed / elapsed_minutes if elapsed_minutes > 0 else 0

      self.total_errors += errors
      self.total_chars += len(self.test)
      self.total_words += words_typed

      self.current_index += 1

      if self.current_index < len(self.paragraphs):
         self.load_paragraph()
      else:
        full_elapsed = (end_time - self.full_start_time) / 60
        final_wpm = self.total_words / full_elapsed if full_elapsed > 0 else 0
        self.entry.config(state='disabled')
        self.results_label.config(text=f"Test Complete! WPM: {final_wpm:.2f} | Total Errors: {self.total_errors}")

  def end_test(self):
    end_time = time.time()
    full_elapsed = (end_time - self.full_start_time) / 60 if self.full_start_time else 1
    final_wpm = self.total_words / full_elapsed if full_elapsed > 0 else 0

    self.entry.config(state='disabled')
    self.display_text.config(state='disabled')
    self.progress['value'] = 100  # force full bar

    if hasattr(self, 'results_label'):
      self.results_label.config(text=f"Test Ended! WPM: {final_wpm:.2f} | Total Errors: {self.total_errors}")
    else:
      self.results_label = ttk.Label(self.root, text=f"Test Ended! WPM: {final_wpm:.2f} | Total Errors: {self.total_errors}", font=('Times New Roman', 14), background="#f4f4f4")
      self.results_label.pack()

  def show_results(self):
    global wpm_records

    time_taken = time.time() - start_time
    word_count = len(self.text.split())
    wpm = (word_count / time_taken) * 60
    accuracy = ((len(self.text) - errors) / len(self.text)) * 100
    wpm_records.append(wpm)

    result = tk.Toplevel(self.root)
    result.title("Results")
    ttk.Label(result, text=f"WPM: {wpm:.2f}").pack()
    ttk.Label(result, text=f"Accuracy: {accuracy:.2f}%").pack()
    ttk.Label(result, text=f"Highest Speed: {max(wpm_records):.2f} WPM").pack()
    ttk.Label(result, text=f"Average Speed: {sum(wpm_records)/len(wpm_records):.2f} WPM").pack()

    self.plot_error_rate_chart(result)
    self.plot_heatmap(result)

    self.save_typing_analysis()

  def plot_error_rate_chart(self, parent):
    fig, ax = plt.subplots(figsize=(5, 3))
    keys = list(character_mistype.keys())
    values = [character_mistype[k] for k in keys]
    ax.bar(keys, values)
    ax.set_title("Typing Error Frequency")
    ax.set_ylabel("Mistakes")
    plt.tight_layout()
    fig.canvas.manager.set_window_title("Error Analysis")
    plt.show()

  def plot_heatmap(self, parent):
    heat_data = [[0]*10 for _ in range(5)]
    for char, count in character_mistype.items():
      row = ord(char.lower()) // 10 % 5
      col = ord(char.lower()) % 10
      heat_data[row][col] = count
      
      fig, ax = plt.subplots()
      cax = ax.imshow(heat_data, cmap='Reds', interpolation='nearest')
      ax.set_title("Typing Error Heatmap")
      fig.colorbar(cax)
      plt.tight_layout()
      plt.show()

  def save_typing_analysis(self):
    analysis_data = {
       "common_errors": dict(character_mistype),
       "proximity_map": keyboard_proximity,
       "common_words": dict(word_counter.most_common(20))}
    
    with open("typing_analysis.json", "w") as f:
      json.dump(analysis_data, f, indent=4)

# Run the GUI
if __name__ == "__main__":
  root = tk.Tk()
  app = PythonTypingTestApp(root)
  root.mainloop()