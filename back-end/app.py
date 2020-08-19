from flask import Flask 
from flask_cors import CORS
import pandas as pd
import datetime
import run_model

import random
app = Flask(__name__) 
CORS(app)
@app.route('/') 
def index():
    return 'Welcome to the Nuloft API. Documentation for the API is still a work in progress' 

@app.route('/getPM10') 
def pm10(): 
    return run_model.keyraLikan().to_json(orient='records',date_format='iso')
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=83)
