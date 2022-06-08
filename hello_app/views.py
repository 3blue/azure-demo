import requests
import json
from datetime import datetime
from flask import Flask, render_template, request
from . import app
import speech_recognition as sr
import audiomath; audiomath.RequireAudiomathVersion( '1.12.0' )

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

class DuckTypedMicrophone( sr.AudioSource ): # descent from AudioSource is required purely to pass an assertion in Recognizer.listen()
    def __init__( self, device=None, chunkSeconds=1024/44100.0 ):  # 1024 samples at 44100 Hz is about 23 ms
        self.recorder = None
        self.device = device
        self.chunkSeconds = chunkSeconds
    def __enter__( self ):
        self.nSamplesRead = 0
        self.recorder = audiomath.Recorder( audiomath.Sound( 5, nChannels=1 ), loop=True, device=self.device )
        # Attributes required by Recognizer.listen():
        self.CHUNK = audiomath.SecondsToSamples( self.chunkSeconds, self.recorder.fs, int )
        self.SAMPLE_RATE = int( self.recorder.fs )
        self.SAMPLE_WIDTH = self.recorder.sound.nbytes
        return self
    def __exit__( self, *blx ):
        self.recorder.Stop()
        self.recorder = None
    def read( self, nSamples ):
        sampleArray = self.recorder.ReadSamples( self.nSamplesRead, nSamples )
        self.nSamplesRead += nSamples
        return self.recorder.sound.dat2str( sampleArray )
    @property
    def stream( self ): # attribute must be present to pass an assertion in Recognizer.listen(), and its value must have a .read() method
        return self if self.recorder else None
        
def listen_to_mic():
    r = sr.Recognizer()
    with DuckTypedMicrophone() as source:
        audio = r.listen(source)
        try:
            text = r.recognize_google(audio)
            return "You said : {}".format(text)
        except:
            return "Sorry, could not recognize what you said."