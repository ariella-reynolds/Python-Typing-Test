# -*- coding: utf-8 -*-

import numpy as np
import tkinter as tk
from tkinter import ttk
import pygame
import json
import random
import time
from collections import defaultdict, Counter
import matplotlib.pyplot as plt

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

# Load Passages (D = Tenzin; O = Ariella) """

# Attempt to load local JSON passages from typing_passages.json
try:
    with open("typing_passages.json", "r", encoding="utf-8") as f:
        LOCAL_PASSAGES = json.load(f).get("passages", [])
except (FileNotFoundError, json.JSONDecodeError):
    LOCAL_PASSAGES = {"easy": [], "medium": [], "hard": []}

# Built-in fallback passages if JSON is missing or broken
FALLBACK_PASSAGES = [
    "We hope you're enjoying our typing test!",
    "Feel free to share this test with your friends to see whose typing reigns supreme!",
    "Sometimes the best way to start is simply to begin, one word at a time.",
    "This is a fallback passage, used when your local text file can't be found."
]

def retrieve_quotation(num_paragraphs=3, difficulty="medium"):
    global word_counter

    suitable_passages = LOCAL_PASSAGES.get(difficulty, [])
    
    if not suitable_passages:
        suitable_passages = FALLBACK_PASSAGES

    selected_passage = random.choice(suitable_passages).replace('‘', '\'').replace('’', '\'').replace('–', '-')
    word_counter = Counter(selected_passage.split(" "))
    
    return [selected_passage]

"""# Establishing Proximity of Letters (Relative to Each Other)
(D = Ariella; O = Tenzin) """
keyboard_proximity = { # two letters were considered close to each other -- i.e., in near proximity -- when they were adjacent to each other, whether horizontally, vertically, or diagonally
    'a':['q','w','s','z'],'s':['a','w','e','d','x','z'],'d':['s','e','r','f','c','x'],'f':['d','r','t','g','v','c'],'g':['f','t','y','h','b','v'],'h':['g','y','u','j','n','b'],'j':['h','u','i','k','m','n'],'k':['j','i','o','l','m'],'l':['k','o','p'],'q':['w','a'],'w':['q','e','s','a'],'e':['w','r','d','s'],'r':['e','t','f','d'],'t':['r','y','g','f'],'y':['t','u','h','g'],'u':['y','i','j','h'],'i':['u','o','k','j'],'o':['i','p','l','k'],'p':['o','l'],'z':['a','s','x'],'x':['z','s','d','c'],'c':['x','d','f','v'],'v':['c','f','g','b'],'b':['v','g','h','n'],'n':['b','h','j','m'],'m':['n','j','k']
}

"""# Constructing GUI (D = Ariella, Tenzin)"""
class PythonTypingTestApp: # defines class of GUI
  def __init__(self,root): # initializes new objects within the class
    self.root = root # sets up and saves main window of typing test
    self.root.title("Python Typing Test") # creates title of typing test
    self.root.geometry('1020x720') # specifies size of window

    #multi-stage tracking variables
    self.paragraphs = []
    self.current_index = 0
    self.total_errors = 0
    self.total_chars = 0
    self.total_words = 0
    self.full_start_time = None

    self.setup_widgets() # places the elements of our GUI within the test (detailed in next section of the code)
    self.reset_test() # clears all previous data before (re)starting test
    self.show_instructions() # shows instructions to user when they first open the test

  # Adding Instruction for the user to the Game (D = Tenzin, O = Ariella)
  def show_instructions(self):
    instructions = tk.Toplevel(self.root)
    instructions.title("Instructions")
    instructions.geometry("720x680")
    instructions.grab_set()  # Prevent user from interacting with main window

    # Background frame to make the instructions a bit prettier
    frame = tk.Frame(instructions, bg="#f4f4f4")
    frame.pack(fill="both", expand=True, padx=20, pady=20)

    #Title
    title = tk.Label(frame, text="Instructions", font=("Optima", 30, "bold"), bg="#f4f4f4")
    title.pack(pady=(20, 10))

    # Instructions text
    msg_text = (
        "Welcome to the Python Typing Test!\n\n"
        "Instructions:\n\n"
        "1. Select a difficulty level from the dropdown menu.\n"
        "   ● Easy: Paragraphs with just the English Alphabet and periods.\n"
        "   ● Medium: Moderate-length passages with basic punctuation.\n"
        "   ● Hard: Paragraphs with special characters included.\n\n"
        "2. After changing a difficulty level, please press Restart Test. \n\n"
        "3. Start typing the paragraph shown in the white box. Your time has now started\n\n"
        "4. Characters will be highlighted as:\n"
        "   ● Green: Correct\n"
        "   ● Red: Incorrect\n"
        "   ● Yellow: Next character to type\n\n"
        "5. Progress bar shows your completion.\n\n"
        "6. The test ends automatically when you've typed all characters and will display your results.\n\n"
        "7. You can also press End Test at any time to end the test and view your results."
    )

    msg = tk.Label(frame,text= msg_text,justify="left", wraplength=560,font=("Baskerville", 15),fg="#333333",bg="#f4f4f4")
    msg.pack(padx=20, pady=(0, 10))

    # Styled a Button 
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Red.TButton", background="#8B0000",foreground="#F5E6C4", font=('Baskerville', 14, 'bold'),padding=6)

    # Hover (active) style
    style.map("Red.TButton",
    background=[("active", "#A97142")])  # Warm Bronze color for Hover

    start_btn = ttk.Button(frame, text="Start Test",command=instructions.destroy,style="Red.TButton")
    start_btn.pack(pady=(10, 20))
    
  """# Adding Specific Features to GUI (D = Tenzin, Ariella)"""
  def setup_widgets(self): # adds different elements to typing test
    self.root.configure(bg="#E7DCC7")  # Background color

    # Title and Subheading
    heading = tk.Label(self.root, text="Typing Test", font=('Times New Roman', 45, 'bold'), fg="#1A1A2E", background="#E7DCC7") # creates title of typing test
    heading.pack(pady=(20, 10))
    subheading = tk.Label(self.root, text="CLPS0950: Final Project by Tenzin Diki and Ariella Reynolds",font=('Baskerville', 16), fg="#3B4C66", background="#E7DCC7")
    subheading.pack(pady=(0, 20))

    note = tk.Label(self.root, text="Passages sourced from Babel by R.F. Kuang",font=('Baskerville', 16,), fg="#3B4C66", background="#E7DCC7")
    note.pack(side='bottom', pady=10)


    self.difficulty = tk.StringVar(value = "medium") # stores difficulty level, with medium difficulty level as default
    ttk.Label(self.root, text="Select Difficulty:", font=('Baskerville', 18), background ='#E7DCC7', foreground ='#1A1A2E').pack(pady=(20, 5)) # labels difficulty level selection window ("Difficulty:")
    ttk.Combobox(self.root, textvariable = self.difficulty, values = ["easy","medium","hard"]).pack() # allows user to select difficulty (either "easy," "medium," or "hard") through a dropdown option

    self.display_text = tk.Text(self.root, height=7, font=('Baskerville',18), wrap='word', bg='#FFFFFF', fg='#1A1A2E', relief='solid', bd=1)
    self.display_text.pack(fill='x', padx=20, pady=10)

    self.display_text.config(state='disabled')

    # Text tags for feedback
    self.display_text.tag_config("correct", foreground="green")
    self.display_text.tag_config("incorrect", foreground="red")
    self.display_text.tag_config("cursor", background="yellow", foreground="black")

    # Hidden input field for capturing keystrokes    
    self.hidden_input = tk.Entry(self.root)
    self.hidden_input.place(x=-1000, y=-1000)  # moves it off-screen
    self.hidden_input.bind("<KeyRelease>", self.on_key_press)
    self.hidden_input.focus_set()
    
    # Progress bar
    # Style for the progress bar
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("OxfordInk.Horizontal.TProgressbar", thickness=20, troughcolor="#1A1A2E", background="#C0C0C0") # sets color of progress bar to blue

    self.progress = ttk.Progressbar(self.root, maximum = 100, style = "OxfordInk.Horizontal.TProgressbar") 
    self.progress.pack(fill = 'x', padx=20, pady=(0, 15)) # displayed horizontally (progress bars are generally horizontal)

    self.end_btn = ttk.Button(self.root, text="End Test", command=self.end_test, style="Red.TButton")
    self.end_btn.pack(pady=(5, 20))
    
    self.restart_btn = ttk.Button(self.root, text = "Restart Test", command = self.reset_test, style="Red.TButton") # user can restart typing test by pressing "Restart Test" button
    self.restart_btn.pack(pady=(5, 20))
  
  """# Resetting Typing Test (D = Ariella, Tenzin)"""
  def reset_test (self): # clears prior attempt and creates fresh test for user after restarting
    global start_time, char_position, errors, total_char # makes sure these variables can be accessed within this function, even though they are created outside the function
    self.paragraphs = retrieve_quotation(num_paragraphs=3, difficulty=self.difficulty.get()) # calls function that retrieves quotation, which gives users a new quotation to type
    self.current_index = 0
    self.total_errors = 0
    self.total_chars = 0
    self.total_words = 0
    self.full_start_time = None
    self.load_paragraph()
    
    self.display_text.config(state = 'normal') # allows display to be edited (in this case, by updating it to create a new test)
    self.display_text.delete('1.0','end') # clears text from previous test
    self.display_text.insert('1.0',self.test) # places new text into text display window
    self.display_text.config(state = 'disabled') # switches display back to read-only format
    
    self.hidden_input.delete(0, 'end')
    self.hidden_input.focus_set()
    
    start_time = None # resets elapsed time to 0
    char_position = 0 # resets position of character within string of text to 0
    errors = 0 # resets number of mistakes made by user to 0
    total_char = len(self.test) # tracks total number of characters encountered during new test
    self.progress['value'] = 0 # resets progress bar to 0%

  # (D = Tenzin; O = Ariella)
  def load_paragraph(self):
    global char_position, errors, total_char, start_time

    if self.current_index == 0:
      self.full_start_time = time.time()

    self.test = self.paragraphs[self.current_index]
    self.display_text.config(state='normal')
    self.display_text.delete('1.0', 'end')
    self.display_text.insert('1.0', self.test)

    start_time = None
    char_position = 0
    errors = 0
    total_char = len(self.test)
    self.progress['value'] = 0
   
  """# Indicating What Happens When a User Presses a Key (D = Tenzin; O = Ariella)"""
  def on_key_press(self, event):
    global start_time, char_position, errors, total_char
    
    if not start_time:
      start_time = time.time()
      self.full_start_time = start_time
      
    typed_text = self.hidden_input.get()
    target_text = self.test

    # Sound effect on keypress
    key_sound.play()

    # Temporarily enable display to apply tags
    self.display_text.config(state='normal')
    self.display_text.tag_remove("correct", "1.0", "end")
    self.display_text.tag_remove("incorrect", "1.0", "end")
    self.display_text.config(state='disabled')

    #self.hidden_input.delete(0, 'end')
    #self.hidden_input.focus_set()

    min_len = min(len(typed_text), len(target_text))
    errors = 0

    i = min_len - 1
    expected = target_text[i]
    typed = typed_text[i]
    if typed != expected:
      errors += 1
      character_mistype[expected] += 1
    for i in range(min_len):
      expected = target_text[i]
      typed = typed_text[i]
      tag = "correct" if typed == expected else "incorrect"
      self.display_text.tag_add(tag, f"1.{i}", f"1.{i+1}")
    
    self.progress['value'] = (min_len / total_char) * 100
    for i in range(len(target_text), len(typed_text)):
      self.display_text.tag_add("incorrect", f"1.{i}", f"1.{i+1}")
      errors += 1

    self.display_text.config(state='normal') # temporarily enable to display cursor to show where you are typing
    self.display_text.tag_remove("cursor", "1.0", "end")  # Remove old cursor tag
      
    if len(typed_text) < len(target_text):
      next_index = len(typed_text)
      self.display_text.tag_add("cursor", f"1.{next_index}", f"1.{next_index + 1}")

    self.display_text.config(state='disabled')  # Disable again
      

    if len(typed_text) >= len(target_text):
      self.end_test()

  #(D = Tenzin, O = Ariella)
  def end_test(self):
    end_time = time.time()
    full_elapsed = (end_time - self.full_start_time) / 60 if self.full_start_time else 1
    
    #recalculate errors with a 'for' loop here
    typed_text = self.hidden_input.get()
    target_text = self.test
    
    errors = 0 
    for i in range(len(typed_text)):
      expected = target_text[i]
      typed = typed_text[i]
      if typed != expected:
        errors += 1
    
    self.total_errors += errors
    self.total_chars += len(self.test)
    self.total_words += len(self.test.split())
    final_wpm = self.total_words / full_elapsed if full_elapsed > 0 else 0

    self.display_text.config(state='disabled')
    self.progress['value'] = 100

    self.show_results() # show results windows when test ends

  #(D = Ariella, O = Tenzin)
  def show_results(self):
    global wpm_tracker
    
    time_taken = time.time() - self.full_start_time if self.full_start_time else 1
    wpm = (self.total_words / time_taken) * 60
    accuracy = ((self.total_chars - self.total_errors) / self.total_chars) * 100 if self.total_chars else 0
    wpm_tracker.append(wpm)

    result = tk.Toplevel(self.root)
    result.title("Results")
    ttk.Label(result, text=f"WPM: {wpm:.2f}").pack()
    ttk.Label(result, text=f"Accuracy: {accuracy:.2f}%").pack()
    ttk.Label(result, text=f"Highest Speed: {max(wpm_tracker):.2f} WPM").pack()
    ttk.Label(result, text=f"Average Speed: {sum(wpm_tracker)/len(wpm_tracker):.2f} WPM").pack()

    self.plot_error_rate_chart(result)
    self.plot_heatmap(result)
    self.save_typing_analysis()

  #(D = Ariella, O = Tenzin)
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

  #(D = Ariella, O = Tenzin)
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

  #(D = Ariella, O = Tenzin)
  def save_typing_analysis(self):
    print(word_counter)
    print(word_counter.most_common(20))
    analysis_data = {
       "common_errors": dict(character_mistype),
       "proximity_map": keyboard_proximity,
       "common_words": dict(word_counter.most_common(20))}
    
    with open("typing_analysis.json", "w") as f:
      json.dump(analysis_data, f, indent=4)

  #(D = Tenzin, O = Ariella)
# Run the GUI
if __name__ == "__main__":
  root = tk.Tk()
  app = PythonTypingTestApp(root)
  root.mainloop()

