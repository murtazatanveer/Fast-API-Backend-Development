from fastapi import FastAPI 
from Model.modelPrediction import prediction
from preprocessing import preprocess_text # Function used by vectorizor during text preprocessing
from Schema.reviewSchema import Review , PredictionResponce

app = FastAPI(
    title="Sentiment Analysis API",
    description="Predicts sentiment of restaurant reviews using Logistic Regression",
    version="1.0.0",
)

@app.get("/")
def hello():
    return {"message": "Welcome to Sentiment Analysis Project"}

@app.post("/prediction",response_model=PredictionResponce)
def review_prediction(review: Review):
    
    pred,prob = prediction(review=review.review)

    return {
        "message": "Model Prediction done Successfully",
        "success": True,
        "prediction": {
            "result": int(pred[0]),
            "positivity_percent": int(prob[0][1]),
            "negativity_percent": int(prob[0][0])
        },
    }




    