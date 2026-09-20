from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Annotated
import pickle

# Import the module so pickle can find preprocessing.preprocess_text
from preprocessing import preprocess_text  # noqa: F401

app = FastAPI(
    title="Sentiment Analysis API",
    description="Predicts sentiment of restaurant reviews using Logistic Regression",
    version="1.0.0",
)


def load_model():
    with open("sentiment_analysis_model.pkl", "rb") as file:
        return pickle.load(file)


model_data = load_model()
vec = model_data["vectorizer"]
model = model_data["classifier"]


@app.get("/")
def hello():
    return {"message": "Welcome to Sentiment Analysis Project"}


class Review(BaseModel):
    review: Annotated[str,Field(..., min_length=5, max_length=800,description="Customer review text",)]


@app.post("/prediction")
def review_prediction(review: Review):
    X = vec.transform([review.review])
    pred = model.predict(X)
    prob = model.predict_proba(X) * 100

    return {
        "message": "Model Prediction done Successfully",
        "success": True,
        "prediction": {
            "result": int(pred[0]),
            "positivity_percent": round(float(prob[0][1]), 2),
            "negativity_percent": round(float(prob[0][0]), 2),
        },
    }