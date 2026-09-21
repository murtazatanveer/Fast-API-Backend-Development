from Model.loadModel import vec,model

def prediction(review):
    X = vec.transform([review])
    pred = model.predict(X)
    prob = model.predict_proba(X) * 100
    return [pred,prob]