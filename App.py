# Important Libraries
from flask import Flask , render_template,request ,redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_executor import Executor
import speech_recognition as sr
import pyttsx3
import time
import os
import json
import random
import ml
import wikipedia

from sqlalchemy import JSON

with open('msg.json','r') as c:
    doctor_msg=json.load(c)
    
    

# Configuration 
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:''@localhost/smartdoc'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Mysql Tables 
class Newprofile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(120),  nullable=False)
    gender = db.Column(db.Integer, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    bp = db.Column(db.Integer,  nullable=False)
    weight = db.Column(db.Integer, unique=True, nullable=False)
    height = db.Column(db.Integer,  nullable=False)
    sugar = db.Column(db.String(120), nullable=False)

class Symptoms(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sym_name = db.Column(db.String(200),  nullable=False)
    

# Retreive Patient Profile Data 
class patient_profile:
    patient_id=''
    patient_name=''
    patient_bp=''
    patient_sugar=''
    patient_weight=''
    gender=''
    def __init__(self):
        db_resp=Newprofile.query.filter_by(id=1).first()
        self.patient_name=db_resp.first_name
        self.patient_bp=db_resp.bp
        self.patient_sugar=db_resp.sugar
        self.patient_weight=db_resp.weight
        self.gender=db_resp.gender
    def getp_name(self):
        return self.patient_name
    def getp_bp(self):
        return self.patient_bp
    def getp_sugar(self):
        return self.patient_sugar
    def getp_weight(self):
        return self.patient_weight
    def getp_gender(self):
        return self.gender

pp=patient_profile()     

def speakDoctor(text):
    # voice[0] For Men , voice[1] For women
    engine = pyttsx3.init('sapi5')
    voices=engine.getProperty('voices')
    rate=engine.getProperty('rate')
    engine.setProperty('rate',rate-60)  # Set Voice Speed 
    # Check if gender 
    if(pp.getp_gender()==1): # if Male
        engine.setProperty('voice',voices[0].id)  
    else:   # if female
        engine.setProperty('voice',voices[1].id)
    engine.say(text)
    return engine.runAndWait()

def takeCommand():
    try:
        r= sr.Recognizer()
        with sr.Microphone() as source:
            audio=r.listen(source)
        query=r.recognize_google(audio,language='en').lower()
        print(f"user saud: {query}")
        return query
    except:
        speakDoctor(choose_rand(doctor_msg['excuse_for_sound']))
        
def choose_rand(array):
    # secure random generator
    secure_random = random.SystemRandom()
    return secure_random.choice(array)

def is_exitcmd(query):
    if query in doctor_msg['exit_cmd']:
        return 1
    return 0

    
def phase_0():
    speakDoctor(choose_rand(doctor_msg['wc_msg']))
    while True:
        Query=takeCommand()
        if Query=='hi doctor':
            break

def phase_1():
    speakDoctor(f"Hi {pp.getp_name}. how you doing?")
    while True:
        Query=takeCommand()
        if is_exitcmd(Query):
            break
        if Query=='i am fine':
            speakDoctor(f"I recieved your details.")
            if pp.getp_bp<92:
                speakDoctor('You have high blood pressure.')
                break
            if  pp.getp_sugar>100:
                speakDoctor('You have low Sugar.')
                break
def phase_2():
    speakDoctor(f"{pp.getp_name}. What symptoms do you have?")
    

    

def start_convers():
    phase_0()
    phase_1()
    phase_2()

def prev_convers():
    speakDoctor('What disease might you have?')
    while True:
        Query=takeCommand()
        if Query=='thanks':
            speakDoctor('Have a nice day')
            break
        wiki_res=wikipedia.summary(f"prevention of {Query}",sentences=2)
        speakDoctor(wiki_res)
        return wiki_res


@app.route("/")
def Home():
    return render_template('index.html')

@app.route("/clinic")
def clinic():
    return render_template('clinic.html')

@app.route("/profile", methods = ['GET' , 'POST'])
def profile():
    if(request.method=='POST'):
        # Add Entry to Database 
        f_name = request.form.get('f_name')
        gender = request.form.get('gender')
        page = request.form.get('age')
        pbp = request.form.get('bp')
        pweight = request.form.get('weight')
        psugar = request.form.get('sugar')
        pheight = request.form.get('height')

        entry=Newprofile(first_name=f_name,gender=gender,age=page,bp=pbp,weight=pweight,sugar=psugar,height=pheight)

        db.session.add(entry)
        db.session.commit()
        # return redirect(url_for('clinic'))
    return render_template('profile.html')

@app.route("/doctor", methods=['GET', 'POST'])
def doctor():
    # if request.method=='POST':
    #     data = json.loads(request.data)
    #     for key in data:
    #         user_sym=data[key]
    #     final_pred=ml.main(user_sym)
    #     speakDoctor(f"You might have {final_pred}. Please visit Prevention Section for Quick Treatment and remdey.")   
        
    executor.submit(start_convers)
    
    return render_template('doctor.html',symptoms=ml.symptoms())
    

@app.route("/report")
def report():
    return render_template('report.html')
@app.route("/prevention")
def pre():
    # executor.submit(prev_convers)
    return render_template('prevention.html')

@app.route('/fetch_data', methods=['POST', 'GET'])
def fetchdata():
    if request.method == "POST":
       user_data = request.data
       print(user_data)
 
    
    return 0

def report():
    return render_template('report.html')

if __name__=='__main__':
    executor = Executor(app)
    app.run(debug=True)



