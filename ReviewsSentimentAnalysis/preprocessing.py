import re
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

wnl = WordNetLemmatizer()

def preprocess_text(text: str) -> str:
    text = re.sub(r'[^a-zA-Z0-9]', ' ', text)
    text = text.lower()
    text = word_tokenize(text)
    text = [wnl.lemmatize(word) for word in text]
    text = ' '.join(text)
    return text