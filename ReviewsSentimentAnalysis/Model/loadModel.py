import pickle

def load_model():
    with open("Model/sentiment_analysis_model.pkl", "rb") as file:
        return pickle.load(file)


model_data = load_model()
vec = model_data["vectorizer"]
model = model_data["classifier"]