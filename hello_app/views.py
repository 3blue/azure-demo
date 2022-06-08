import requests
import json
from datetime import datetime
from flask import Flask, render_template, request
from . import app
import speech_recognition as sr

@app.route("/", methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        #response = query(request.form['question'], request.form['context'])
        #response = ''.join( c for c in response if  c not in '[]",' )
        #out = "THE MODEL SAYS: " + response
        return render_template("home.html") + listen_to_mic()
    return render_template("home.html")

@app.route("/about/")
def about():
    return render_template("about.html")


@app.route("/contact/")
def contact():
    return render_template("contact.html")

@app.route("/hello/")
@app.route("/hello/<name>")
def hello_there(name = None):
    return render_template(
        "hello_there.html",
        name=name,
        date=datetime.now()
    )

@app.route("/api/data")
def get_data():
    return app.send_static_file("data.json")


def query(question, context):

    scoring_uri = 'http://a969e5da-ec26-4ceb-967c-4d8f2c25f65a.eastus.azurecontainer.io/score'
    key = 'MOdyhuXuBfxZFv04xWMyXB6ejMAcLKBv'

    # Set the appropriate headers
    headers = {"Content-Type": "application/json"}
    headers["Authorization"] = f"Bearer {key}"

    # Make the request and display the response and logs
    data = {
        "query": question,
        "context": context,
    }
    data = json.dumps(data)
    resp = requests.post(scoring_uri, data=data, headers=headers)
    return resp.text
    
def listen_to_mic():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        #print("Speak Anything :")
        audio = r.listen(source)
        try:
            text = r.recognize_google(audio)
            return "You said : {}".format(text)
        except:
            return "Sorry could not recognize what you said"