import json
import re

# Generating Passages from Babel for Typing Test (D = Tenzin; O = Ariella)
def load_text_file(path): # opens a file given the path provided
    with open(path, 'r', encoding='utf-8') as f: # correctly encodes file to ensure that non-alphanumeric characters are properly displayed
        return f.read() # returns file as a string

def categorize_passage(passage): # groups passages according to difficulty
    if re.match(r'^[A-Za-z\s\.]+$', passage): # paragraphs with just the English alphabet and periods
        return 'easy'
    elif re.match(r'^[A-Za-z0-9\s\.,\?!\'\"]+$', passage): # moderate-length passages with basic punctuation
        return 'medium'
    else: # paragraphs with other special characters included
        return 'hard'
    
def split_into_passages(text, max_length=600, min_length=200): # separates Babel (text from which we drew passages) into 200- to 600-character passages that users can type
    paragraphs = [p.strip().replace('\n', ' ') for p in text.split('\n\n') if p.strip()] # splits text into paragraphs and allows user to type a space instead of a line break; all blank space except for singular spaces are not considered within the function
    passages = {'easy': [], 'medium': [], 'hard': []} # stores all passages

    for para in paragraphs: # for each paragraph
        chunks = [] # separates into smaller parts
        if len(para) <= max_length: # if paragraph is at most 600 characters (the maximum length for a paragraph within this typing test)
            if len(para) >= min_length: # if paragraph is at least 200 characters (the minimum length for n paragraph within this typing test)
                chunks.append(para) # paragraph is used
        else:
            sentences = para.split('. ') # splits paragraph into sentences
            chunk = "" # initializes string for each chunk (which will eventually comprise a new paragraph)
            for s in sentences: # for each sentence
                sentence = s + '. ' # adds back period at the end of each sentence that was removed during the splitting process
                if len(chunk) + len(sentence) < max_length: # if adding a new sentence still allows the paragraph to be at most 600 characters (the maximum length for a paragraph within this typing test)
                    chunk += sentence # sentence is added to chunk
                else:
                    if len(chunk.strip()) >= min_length: # if adding a new sentence causes the paragraph to be at least 200 characters (the minimum length for a paragraph within this typing test)
                        chunks.append(chunk.strip()) # chunk is used, with extra spaces removed
                    chunk = sentence # new chunk begins with added sentence
            if chunk.strip() and len(chunk.strip()) >= min_length: # if chunk is at least 200 characters and some text is left in chunk
                chunks.append(chunk.strip()) # added as final chunk

        for chunk in chunks: # for each chunk
            difficulty = categorize_passage(chunk) # assigned a difficulty level
            passages[difficulty].append(chunk) # chunk (passage) stored

    return passages

def save_as_json(passages, out_file='typing_passages.json'): # saves data to output file
    with open(out_file, 'w', encoding='utf-8') as f: # opens file: writes over it if it has already been opened, correctly encodes file to ensure that non-alphanumeric characters are properly displayed, and exits from file once data have been added to it
        json.dump({"passages": passages}, f, indent=2) # converts Python object to JSON string to ensure that it can be added to file

text = load_text_file("R.-F.-Kuang-Babel.txt") # generates text file from Babel and returns it as a string
passages = split_into_passages(text) # chunked passages processed and stored
save_as_json(passages, out_file='typing_passages.json') # saves passages as JSON file