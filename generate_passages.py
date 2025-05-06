import json
import re

def load_text_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def categorize_passage(passage):
    if re.match(r'^[A-Za-z\s\.]+$', passage):
        return 'easy'
    elif re.match(r'^[A-Za-z0-9\s\.,\?!\'\"]+$', passage):
        return 'medium'
    else:
        return 'hard'
    
def split_into_passages(text, max_length=600, min_length=200):
    paragraphs = [p.strip().replace('\n', ' ') for p in text.split('\n\n') if p.strip()]
    passages = {'easy': [], 'medium': [], 'hard': []}

    for para in paragraphs:
        chunks = []
        if len(para) <= max_length:
            if len(para) >= min_length:
                chunks.append(para)
        else:
            sentences = para.split('. ')
            chunk = ""
            for s in sentences:
                sentence = s + '. '
                if len(chunk) + len(sentence) < max_length:
                    chunk += sentence
                else:
                    if len(chunk.strip()) >= min_length:
                        chunks.append(chunk.strip())
                    chunk = sentence
            if chunk.strip() and len(chunk.strip()) >= min_length:
                chunks.append(chunk.strip())

        for chunk in chunks:
            difficulty = categorize_passage(chunk)
            passages[difficulty].append(chunk)

    return passages

def save_as_json(passages, out_file='typing_passages.json'):
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump({"passages": passages}, f, indent=2)

# Using actual file name
text = load_text_file("R.-F.-Kuang-Babel.txt")
passages = split_into_passages(text)
save_as_json(passages, out_file='typing_passages.json')