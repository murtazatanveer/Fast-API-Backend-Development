from fastapi import FastAPI
from pydantic import BaseModel,Field
from typing import Annotated
import pickle
import re
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

app = FastAPI()

wnl = WordNetLemmatizer()

def preprocess_text(text: str) -> str:
    text = re.sub(r'[^a-zA-Z0-9]', ' ', text)
    text = text.lower()
    text = word_tokenize(text)
    text = [wnl.lemmatize(word) for word in text]
    text = ' '.join(text)
    return text

def load_model():
    with open("sentiment_analysis_model.pkl", "rb") as file:
        model_data = pickle.load(file)
    return model_data

model_data = load_model()

@app.get("/")
def hello():
    return {"message":"Wlcome to Sentiment Analysis Project"}

class Review(BaseModel):
    review: Annotated[str,Field(...,min_length=5,max_length=800,description="Customer review")]

@app.post("/prediction")
def reviewPrediction(review:Review):

    vec = model_data["vectorizer"]
    model = model_data["classifier"]

    pred = model.predict(vec.transform([review.review]))
    prob = model.predict_proba(vec.transform([review.review])) * 100

    return {
        "message":"Model Prediction done Successfully",
        "success":True,
        "prediction":{
            "result":pred[0],
            "positivity percent":round(prob[0][1],2),
            "negativity percent":round(prob[0][0],2)
            }
    }


