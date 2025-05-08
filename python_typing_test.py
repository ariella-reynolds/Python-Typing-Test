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
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Sets Up Test (Initialization) (D = Tenzin; O = Ariella)
pygame.mixer.init() # initializes pygame mixer, which creates sound effects within typing test
try:
  key_sound = pygame.mixer.Sound('type.wav') # loads file that provides sound effects (key tapping sounds as user types)
except Exception as e: # if sound doesn't work
  print(f"Sound loading error: {e}")
  key_sound = None
key_sound.set_volume(0.3) # lowers volume of sound
key_sound.play(loops=-1)  # loops sound indefinitely

# Global Variables (D = Tenzin; O = Ariella); used mainly for constants
start_time = None # tracks elapsed time (starts at 0)
char_position = 0 # tracks position of character within string of text (starts at 0)
errors = 0 # tracks number of mistakes made by user (starts at 0)
wpm_tracker = [] # tracks words per minute (wpm) values as they change throughout a given test
character_mistype = defaultdict(int) # tracks number of times user incorrectly types a particular character
word_counter = Counter() # tracks number of times a particular word emerges during the test
total_char = 0 # tracks total number of characters encountered during a test (starts at 0)

# Loads Passages (D = Tenzin; O = Ariella)

try: # attempts to load local JSON passages from typing_passages.json
    with open("typing_passages.json", "r", encoding="utf-8") as f:
        LOCAL_PASSAGES = json.load(f).get("passages", [])
except (FileNotFoundError, json.JSONDecodeError):
    LOCAL_PASSAGES = {"easy": [], "medium": [], "hard": []}

FALLBACK_PASSAGES = [ # built-in fallback passages if JSON is missing or broken
    "We hope you're enjoying our typing test!",
    "Feel free to share this test with your friends to see whose typing reigns supreme!",
    "Sometimes the best way to start is simply to begin, one word at a time.",
    "This is a fallback passage, used when your local text file can't be found."
]

def retrieve_quotation(num_paragraphs=3, difficulty="medium"): # obtains passage of text with three paragraphs for a medium difficulty level test
    global word_counter

    suitable_passages = LOCAL_PASSAGES.get(difficulty, []) # retrieves a selection of passages that fit the criteria in the function above
    
    if not suitable_passages: # if there is no passage found with the necessary criteria, as defined above, the test offers the user a default option
        suitable_passages = FALLBACK_PASSAGES

    selected_passage = random.choice(suitable_passages).replace('‘', '\'').replace('’', '\'').replace('–', '-') # randomly picks passage from selection of passages with the necessary criteria ("suitable_passages") and ensures that users are able to type certain non-alphanumeric characters accurately
    word_counter = Counter(selected_passage.split(" ")) # counts number of words in the passage for post-test word frequency analysis
    
    return [selected_passage] 

# Establishes Proximity of Letters (Relative to Each Other) (D = Ariella; O = Tenzin)
keyboard_proximity = { # two letters were considered close to each other -- i.e., in near proximity -- when they were adjacent to each other, whether horizontally, vertically, or diagonally
    'a':['q','w','s','z'],'s':['a','w','e','d','x','z'],'d':['s','e','r','f','c','x'],'f':['d','r','t','g','v','c'],'g':['f','t','y','h','b','v'],'h':['g','y','u','j','n','b'],'j':['h','u','i','k','m','n'],'k':['j','i','o','l','m'],'l':['k','o','p'],'q':['w','a'],'w':['q','e','s','a'],'e':['w','r','d','s'],'r':['e','t','f','d'],'t':['r','y','g','f'],'y':['t','u','h','g'],'u':['y','i','j','h'],'i':['u','o','k','j'],'o':['i','p','l','k'],'p':['o','l'],'z':['a','s','x'],'x':['z','s','d','c'],'c':['x','d','f','v'],'v':['c','f','g','b'],'b':['v','g','h','n'],'n':['b','h','j','m'],'m':['n','j','k']
}

# Constructs GUI (D = Ariella, O = Tenzin)
class PythonTypingTestApp: # defines class of GUI
  def __init__(self,root): # initializes new objects within the class
    self.root = root # sets up and saves main window of typing test
    self.root.title("Python Typing Test") # creates title of typing test
    self.root.geometry('1020x720') # specifies size of window

    # multi-stage tracking variables (used within GUI class, along with global variables; also used mainly for evolving values)
    self.paragraphs = [] # holds text to be typed by user
    self.current_index = 0 # tracks which paragraph user is typing (starts at 0, or first paragraph, and therefore, the first test)
    self.total_errors = 0 # tracks number of mistakes made by user (starts at 0)
    self.total_chars = 0 # tracks total number of characters encountered during a test (starts at 0)
    self.total_words = 0 # tracks total number of words encountered during a test (starts at 0)
    self.full_start_time = None # tracks elapsed time (starts at 0)

    self.setup_widgets() # places the elements of our GUI within the test (detailed in next section of the code)
    self.reset_test() # clears all previous data before (re)starting test
    self.show_instructions() # shows instructions to user when they first open the test

  # Adds Instructions Window (D = Tenzin, O = Ariella)
  def show_instructions(self):
    instructions = tk.Toplevel(self.root)
    instructions.title("Instructions")
    instructions.geometry("720x680")
    instructions.grab_set()  # prevents user from interacting with main window

    # background frame to make the instructions a bit prettier
    frame = tk.Frame(instructions, bg="#f4f4f4")
    frame.pack(fill="both", expand=True, padx=20, pady=20)

    # title formatting
    title = tk.Label(frame, text="Instructions", font=("Optima", 30, "bold"), bg="#f4f4f4")
    title.pack(pady=(20, 10))

    # instructions text and formatting
    msg_text = (
        "Welcome to the Python Typing Test!\n\n"
        "Instructions:\n\n"
        "1. Select a difficulty level from the dropdown menu.\n"
        "   ● Easy: Paragraphs with just the English alphabet and periods.\n"
        "   ● Medium: Moderate-length passages with basic punctuation.\n"
        "   ● Hard: Paragraphs with other special characters included.\n\n"
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

    # styles the "start test" button 
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Red.TButton", background="#8B0000",foreground="#F5E6C4", font=('Baskerville', 14, 'bold'),padding=6)

    style.map("Red.TButton", 
    background=[("active", "#A97142")])  # hover (active) style used, which changes the button's color when the user's mouse touches it (without necessarily clicking on it), thereby providing the user with dynamic feedback; warm bronze color added

    start_btn = ttk.Button(frame, text="Start Test",command=instructions.destroy,style="Red.TButton")
    start_btn.pack(pady=(10, 20))
    
  # Adds Specific Features to GUI (D = Tenzin, O = Ariella)
  def setup_widgets(self): # adds different elements to typing test
    self.root.configure(bg="#E7DCC7")  # background color

    # title and subheading
    heading = tk.Label(self.root, text="Typing Test", font=('Times New Roman', 45, 'bold'), fg="#1A1A2E", background="#E7DCC7") # creates title of typing test
    heading.pack(pady=(20, 10))
    subheading = tk.Label(self.root, text="CLPS0950: Final Project by Tenzin Diki and Ariella Reynolds",font=('Baskerville', 16), fg="#3B4C66", background="#E7DCC7")
    subheading.pack(pady=(0, 20))

    note = tk.Label(self.root, text="Passages sourced from Babel by R.F. Kuang",font=('Baskerville', 16,), fg="#3B4C66", background="#E7DCC7")
    note.pack(side='bottom', pady=10)

    # difficulty levels and formatting
    self.difficulty = tk.StringVar(value = "medium") # stores difficulty level, with medium difficulty level as default
    ttk.Label(self.root, text="Select Difficulty:", font=('Baskerville', 18), background ='#E7DCC7', foreground ='#1A1A2E').pack(pady=(20, 5)) # labels difficulty level selection window ("Difficulty:")
    ttk.Combobox(self.root, textvariable = self.difficulty, values = ["easy","medium","hard"]).pack() # allows user to select difficulty (either "easy," "medium," or "hard") through a dropdown option

    self.display_text = tk.Text(self.root, height=7, font=('Baskerville',18), wrap='word', bg='#FFFFFF', fg='#1A1A2E', relief='solid', bd=1)
    self.display_text.pack(fill='x', padx=20, pady=10)

    self.display_text.config(state='disabled') # switches display back to read-only format

    # text tags for feedback
    self.display_text.tag_config("correct", foreground="green") # if typed letter is correct
    self.display_text.tag_config("incorrect", foreground="red") # if typed letter is incorrect
    self.display_text.tag_config("cursor", background="yellow", foreground="black")

    # hidden input field: This block of code captures keystrokes without the user seeing it do so   
    self.hidden_input = tk.Entry(self.root) # creates hidden text input box
    self.hidden_input.place(x=-1000, y=-1000) # moves the input box off-screen (so that the user can't see it)
    self.hidden_input.bind("<KeyRelease>", self.on_key_press) # collects data every time user releases a key
    self.hidden_input.focus_set() # requires keyboard input to be focused on widget
    
    # progress bar and formatting
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("OxfordInk.Horizontal.TProgressbar", thickness=20, troughcolor="#1A1A2E", background="#C0C0C0") # sets color of progress bar to blue

    self.progress = ttk.Progressbar(self.root, maximum = 100, style = "OxfordInk.Horizontal.TProgressbar") 
    self.progress.pack(fill = 'x', padx=20, pady=(0, 15)) # displayed horizontally (progress bars are generally horizontal)

    # styles the "end test" button
    self.end_btn = ttk.Button(self.root, text="End Test", command=self.end_test, style="Red.TButton")
    self.end_btn.pack(pady=(5, 20))

    # styles the "restart test" button
    self.restart_btn = ttk.Button(self.root, text = "Restart Test", command = self.reset_test, style="Red.TButton") # user can restart typing test by pressing "Restart Test" button
    self.restart_btn.pack(pady=(5, 20))
  
  # Resets Typing Test (D = Ariella, O = Tenzin)
  def reset_test (self): # clears prior attempt and creates fresh test for user after restarting
    global start_time, char_position, errors, total_char # makes sure these variables can be accessed within this function, even though they are created outside the function
    self.paragraphs = retrieve_quotation(num_paragraphs=3, difficulty=self.difficulty.get()) # calls function that retrieves quotation, which gives users a new quotation to type
    self.current_index = 0 # resets the paragraph user is typing to 0, or first paragraph (first test)
    self.total_errors = 0 # resets number of mistakes made by user to 0
    self.total_chars = 0 # resets total number of characters encountered during a test to 0
    self.total_words = 0 # resets total number of words encountered during a test to 0
    self.full_start_time = None # resets elapsed time to 0
    self.load_paragraph() # retrieves a new paragraph for the user
    
    self.display_text.config(state = 'normal') # temporarily allows display to be edited (in this case, by updating it to create a new test)
    self.display_text.delete('1.0','end') # clears text from previous test
    self.display_text.insert('1.0',self.test) # places new text into text display window
    self.display_text.config(state = 'disabled') # switches display back to read-only format
    
    self.hidden_input.delete(0, 'end') # clears previous typed content in hidden text input box
    self.hidden_input.focus_set() # requires keyboard input to be focused on widget
    
    start_time = None # resets elapsed time to 0
    char_position = 0 # resets position of character within string of text to 0
    errors = 0 # resets number of mistakes made by user to 0
    total_char = len(self.test) # tracks total number of characters encountered during new test
    self.progress['value'] = 0 # resets progress bar to 0%
    wpm_tracker.clear() # clears tracked words per minute values

    self.update_stats() # begins tracking wpm

  def update_stats(self): # tracks and updates wpm as user types
    global start_time, wpm_tracker
    if not start_time: # if user hasn't started typing
        start_time = time.time() # start time is the current time when the user hasn't started typing

    current_time = time.time()
    elapsed_minutes = (current_time - start_time) / 60  # calculates elapsed time in minutes
    typed = self.hidden_input.get().split()  # gets the typed words from hidden input field
    if elapsed_minutes > 0: # once user has started the test
        wpm = len(typed) / elapsed_minutes  # calculates wpm
        wpm_tracker.append(wpm)  # stores wpm in a list
    
    self.root.after(1000, self.update_stats) # schedules this method to run again after each second (updates the wpm as it changes over the course of a test)

  # (D = Tenzin; O = Ariella)
  def load_paragraph(self): # gives the user a new paragraph to type
    global char_position, errors, total_char, start_time

    if self.current_index == 0: # if user is on the first paragraph (first test)
      self.full_start_time = time.time() # time tracked during the test

    self.test = self.paragraphs[self.current_index] # loads one paragraph for user given the number of paragraphs user has typed (0 at the beginning of the test)
    self.display_text.config(state='normal') # temporarily allows text display to be edited
    self.display_text.delete('1.0', 'end') # clears text display
    self.display_text.insert('1.0', self.test) # provides user with new text display
   
  # Indicates What Happens When a User Presses a Key (D = Tenzin; O = Ariella)
  def on_key_press(self, event): # methods controls what happens when a user presses a key
    global start_time, char_position, errors, total_char
    
    if not start_time: # if user hasn't started typing
      start_time = time.time() # start time is the current time when the user hasn't started typing
      self.full_start_time = start_time # time tracked during the test
      
    typed_text = self.hidden_input.get() # user's typed text (collected in hidden input field)
    target_text = self.test # what the user should type for full accuracy

    self.display_text.config(state='normal') # temporarily allows text display to be edited (see below for specific edits)
    self.display_text.tag_remove("correct", "1.0", "end") # clears previous green highlights (if letter is typed correctly)
    self.display_text.tag_remove("incorrect", "1.0", "end") # clears previous red highlights (if letter is typed incorrectly)
    self.display_text.config(state='disabled') # switches display back to read-only format

    min_len = min(len(typed_text), len(target_text)) # takes shortest length of typed text that matches target text (typed characters will not be compared to target characters past this point)
    errors = 0 # resets number of mistakes made by user to 0

  # Indicates What Happens During the Test (D = Ariella; O = Tenzin) 
    i = min_len - 1 # index of the last character that is typed (because Python indexing starts at 0)
    expected = target_text[i]
    typed = typed_text[i]
    if typed != expected: # if the typed text does not align with the expected (accurate) text
      errors += 1 # count discrepancy as an error
      character_mistype[expected] += 1 # captures error
    for i in range(min_len): # for all characters in the shortest line of typed text
      expected = target_text[i] 
      typed = typed_text[i]
      tag = "correct" if typed == expected else "incorrect" # typed text considered correct if it matches the target text
      self.display_text.tag_add(tag, f"1.{i}", f"1.{i+1}") # highlights characters as green (correct) or red (incorrect) based on accuracy
    
    self.progress['value'] = (min_len / total_char) * 100 # updates progress bar depending on the amount of text user has typed relative to the entire text
    for i in range(len(target_text), len(typed_text)): # for all typed characters beyond the target text
      self.display_text.tag_add("incorrect", f"1.{i}", f"1.{i+1}") # marked as incorrect
      errors += 1 # count discrepancy as an error

    self.display_text.config(state='normal') # temporarily allows text display to be edited
    self.display_text.tag_remove("cursor", "1.0", "end") # clears cursor from display
      
    if len(typed_text) < len(target_text): # if user has not typed the entirety of the target text
      next_index = len(typed_text) # next letter that the user should type
      self.display_text.tag_add("cursor", f"1.{next_index}", f"1.{next_index + 1}") # cursor is added to indicate which letter the user should type next

    self.display_text.config(state='disabled') # switches display back to read-only format
      
    if len(typed_text) >= len(target_text): # if user has typed more than or an equal number of characters as the target text
      self.end_test() # ends the test

  # Post-Test Calculations (D = Tenzin, O = Ariella)
  def end_test(self): # after the test ends
    end_time = time.time() # end time is the current time when the user has finished typing
    full_elapsed = (end_time - self.full_start_time) / 60 if self.full_start_time else 1 # calculates total time (in minutes) spent on typing test (set as one minute in case time was not calculated properly)
    
    typed_text = self.hidden_input.get() # user's typed text (collected in hidden input field)
    target_text = self.test # what the user should type for full accuracy
    
    errors = 0 # resets number of mistakes made by user to 0
    for i in range(len(typed_text)): # for all characters in the typed text
      expected = target_text[i]
      typed = typed_text[i]
      if typed != expected: # if the typed text does not align with the expected (accurate) text
        errors += 1 # count discrepancy as an error
    
    self.total_errors += errors # adds mistakes made by user during test to total number of mistakes made by user across all tests
    self.total_chars += len(self.test) # adds total number of characters encountered during a test to number encountered across all tests
    self.total_words += len(self.test.split()) # adds total number of words encountered during a test to number encountered across all tests

    self.display_text.config(state='disabled') # switches display back to read-only format
    self.progress['value'] = 100 # progress bar is shown to be 100% filled once the user has completed the test

    self.show_results() # shows results windows when test ends

  # WPM and Accuracy Statistics (D = Ariella, O = Tenzin)
  def show_results(self): # displays typing statistics once test is completed
    global wpm_tracker 
    
    time_taken = time.time() - self.full_start_time if self.full_start_time else 1 # calculates the amount of time user has spent on the test (fallback option is 1 second so that the calculation does not cause an error if there are no data on start time)
    wpm = (self.total_words / time_taken) * 60  # calculates wpm for the test
    accuracy = ((self.total_chars - self.total_errors) / self.total_chars) * 100 if self.total_chars else 0 # calculates accuracy for the test as a percentage (falls back to 0 if there are no data on accuracy)

    highest_speed = max(wpm_tracker) if wpm_tracker else 0  # calculates the highest wpm achieved during the test
    average_speed = sum(wpm_tracker) / len(wpm_tracker) if wpm_tracker else 0  # calculates the average wpm achieved during the test

    # adds results window
    result = tk.Toplevel(self.root) 
    result.title("Results")
    ttk.Label(result, text=f"Accuracy: {accuracy:.2f}%").pack()
    ttk.Label(result, text=f"Final Speed: {wpm:.2f} WPM").pack()
    ttk.Label(result, text=f"Highest Speed: {highest_speed:.2f} WPM").pack()
    ttk.Label(result, text=f"Average Speed: {average_speed:.2f} WPM").pack()

    self.plot_error_rate_chart(result) # displays error plot (coded in the next section, directly below)

  # Error Plot (D = Ariella, O = Tenzin) 
  def plot_error_rate_chart(self, parent): # creates a bar chart that documents all errors made by user during the test
    fig, ax = plt.subplots(figsize=(5, 3)) # establishes dimensions of chart
    keys = list(character_mistype.keys()) # keeps track of mistyped characters
    values = [character_mistype[k] for k in keys] # keeps track of how many times each character was mistyped
    ax.bar(keys, values)
    ax.set_title("Typing Error Frequency") # title
    ax.set_ylabel("Mistakes") # y-axis
    plt.tight_layout() # modifies spacing to ensure that labels on x- and y-axes do not overlap

    # formatting
    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    canvas.get_tk_widget().pack()

  # Saves Data on Letter/Word Frequency and Proximity (D = Ariella, O = Tenzin)
  def save_typing_analysis(self): # saves data (described below) to file after test is over
    analysis_data = {
       "common_errors": dict(character_mistype), # data on which characters are most frequently missed by user
       "proximity_map": keyboard_proximity, # data on which keys are closest to each other (see line 62 for greater elaboration on this point)
       "common_words": dict(word_counter.most_common(20))} # data on which words appeared most often during tests
    
    with open("typing_analysis.json", "w") as f: # opens file
      json.dump(analysis_data, f, indent=4) # data are placed in file

# Runs the GUI (D = Tenzin, O = Ariella)
if __name__ == "__main__":
  root = tk.Tk()
  app = PythonTypingTestApp(root)
  root.mainloop()

